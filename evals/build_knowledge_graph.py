import pandas as pd
import typing as t
from langchain_core.documents import Document
from util.document_utils import df_to_documents
from ragas.testset.graph import KnowledgeGraph, Node, NodeType, Relationship
from ragas.testset.transforms import apply_transforms
from ragas.testset.transforms.base import BaseGraphTransformation
from ragas.testset.transforms.relationship_builders import (
    CosineSimilarityBuilder,
    OverlapScoreBuilder,
)
from ragas.utils import num_tokens_from_string
from ragas.testset.transforms import Parallel
from evals.evals_utils import (
    node_meta,
    gen_nodes_parquet,
    output_nodes_path,
    gen_relationships_parquet,
    kg_input_data_path,
    kg_json_path,
)
from langsmith import tracing_context


def construct_kg_nodes(docs: list[Document]) -> KnowledgeGraph:
    """Apply the following columns from df to nodes.properties:
    - entities: List[str]
    - themes: List[str]
    - title_embedding: List[float]
    - technical_summary: str
    - technical_summary_embedding: List[float]
    """
    knowledge_graph = KnowledgeGraph()
    for doc in docs:
        # Convert entities from comma-separated string to list if it's a string
        entities = doc.metadata["entities"]
        if isinstance(entities, str):
            entities = [entity.strip() for entity in entities.split(",")]

        knowledge_graph.nodes.append(
            Node(
                type=NodeType.DOCUMENT,
                properties={
                    "page_content": doc.page_content,
                    "document_metadata": doc.metadata,
                    "entities": entities,
                    "themes": doc.metadata.get("themes", []),
                    "title_embedding": doc.metadata.get("title_embedding", []),
                    "technical_summary": doc.metadata.get("technical_summary", ""),
                    "technical_summary_embedding": doc.metadata.get(
                        "technical_summary_embedding", []
                    ),
                },
            )
        )
    return knowledge_graph


def is_valid_metadata(v):
    if v is None:
        return False
    try:
        return not pd.isna(v)
    except BaseException:
        return True


def clean_meta(doc: Document) -> Document:
    # Filter out metadata fields with null-like values
    doc.metadata = {k: v for k, v in doc.metadata.items() if is_valid_metadata(v)}
    return doc


def count_relationship_types(kg: KnowledgeGraph) -> None:
    """Display only: Relationship types and their counts."""
    relationship_types = {}
    for rel in kg.relationships:
        rel_type = rel.type
        if rel_type in relationship_types:
            relationship_types[rel_type] += 1
        else:
            relationship_types[rel_type] = 1
    # Separate relationships into sibling and non-sibling types
    sibling_types = {}
    non_sibling_types = {}

    for rel_type, count in relationship_types.items():
        if rel_type.startswith("sibling_"):
            sibling_types[rel_type] = count
        else:
            non_sibling_types[rel_type] = count

    print("\nRelationships:", flush=True)
    for rel_type, count in non_sibling_types.items():
        print(f"  {rel_type}: {count}", flush=True)
    print("\nSibling relationships:", flush=True)
    for rel_type, count in sibling_types.items():
        print(f"  {rel_type}: {count}", flush=True)


def merge_kg_relationships(kg: KnowledgeGraph):
    """
    Merge relationships that have the same source-target pairs.
    Consider bidirectionality by merging A->B with both A->B and B->A relations.
    Skip relationships with 'sibling' in their type.
    """
    # Get all relationships
    relationships: list[Relationship] = kg.relationships
    original_count = len(relationships)

    # Separate sibling and non-sibling relationships
    sibling_relationships = [rel for rel in relationships if "sibling" in rel.type]
    non_sibling_relationships = [
        rel for rel in relationships if "sibling" not in rel.type
    ]

    # Create a dict to group relationships by source-target pairs
    relationship_groups = {}

    # First, identify all relationships with the same source-target pairs
    for rel in non_sibling_relationships:
        # Create a normalized key for source-target pairs
        # Sort to handle bidirectionality (A->B and B->A will have the same key)
        source, target = rel.source, rel.target
        # Sort by string representation of IDs to avoid comparing Node objects directly
        key = tuple(sorted([str(source.id), str(target.id)]))

        if key not in relationship_groups:
            relationship_groups[key] = []
        relationship_groups[key].append(rel)

    # Create new merged relationships
    merged_relationships = []
    for key, rels in relationship_groups.items():
        if len(rels) == 1:
            # No merging needed if there's only one relationship
            merged_relationships.append(rels[0])
        else:
            # Merge relationships
            base_rel = rels[0]

            # Create a new relationship with merged properties
            merged_properties = {}
            for rel in rels:
                merged_properties.update(rel.properties)

            # Create new relationship based on the first one
            # Since we're merging relationships regardless of direction,
            # all merged relationships should be bidirectional
            merged_rel = Relationship(
                source=base_rel.source,
                target=base_rel.target,
                type="multi",
                bidirectional=True,
                properties=merged_properties,
            )

            merged_relationships.append(merged_rel)

    # Combine merged non-sibling relationships with unchanged sibling relationships
    final_relationships = merged_relationships + sibling_relationships

    # Update the knowledge graph
    kg.relationships = final_relationships

    # Print statistics
    final_count = len(final_relationships)
    merged_count = original_count - final_count
    print(f"\n\nOriginal relationship count: {original_count}", flush=True)
    print(f"Merged relationship count: {final_count}", flush=True)
    print(
        f"Reduction percentage: {(merged_count / original_count) * 100:.2f}%",
        flush=True,
    )
    print(f"Sibling relationships preserved: {len(sibling_relationships)}", flush=True)

    return kg


def create_kg(df: pd.DataFrame, transforms: list[BaseGraphTransformation]) -> None:
    docs = df_to_documents(df)
    docs = [clean_meta(doc) for doc in docs]
    num_docs = len(docs)
    print(f"\nConstructing KG with {num_docs} docs", flush=True)
    kg = construct_kg_nodes(docs)
    print(f"KG has {len(kg.nodes)} nodes", flush=True)
    apply_transforms(kg, transforms)
    print(f"Transformed KG has {len(kg.nodes)} nodes", flush=True)
    print(f"Transformed KG has {len(kg.relationships)} relationships", flush=True)
    count_relationship_types(kg)
    kg = merge_kg_relationships(kg)
    gen_relationships_parquet(kg)
    count_relationship_types(kg)
    print(f"Saving KG.....", flush=True)
    gen_nodes_parquet(kg, output_nodes_path)
    kg.save(kg_json_path)
    print(f"KG saved.", flush=True)


################################### MAIN ###################################

"""
1. Create relationships for all properties:
- entities
- themes
- title_embedding
- technical_summary
- technical_summary_embedding
2. Separate siblings into their own relationship types for future clustering logic
3. Merge multi-relationships into a single "multi" relationship
4. Normalize the scores for each between 0 and 1

Final relationship types:
- multi
- technical_summary_embedding_cosine_similarity
- title_embedding_cosine_similarity
- entities_overlap_score
- html_overlap_score (overlap with user manual entities)
- themes_overlap_score
- sibling_technical_summary_embedding_cosine_similarity
- sibling_title_embedding_cosine_similarity
- sibling_themes_overlap_score
- sibling_entities_overlap_score
"""

with tracing_context(enabled=False):

    def filter_out_html(node):
        return node_meta(node)["type"] != "html"

    def filter_title_sim(node):
        return (
            filter_out_html(node)
            and num_tokens_from_string(node_meta(node)["title"]) > 6
            and "webinar" not in node_meta(node)["title"].lower()
        )

    def filter_overlap(node, property_name: str, min_items: int = 2):
        return len(node.properties[property_name]) > min_items and filter_out_html(node)

    def filter_themes_overlap(node):
        return filter_overlap(node, "themes", 2)

    def filter_entities_overlap(node):
        return filter_overlap(node, "entities", 3)

    def target_html_filter(node):
        return node_meta(node)["type"] == "html"

    def get_transforms() -> t.List[BaseGraphTransformation]:
        cosine_sim_builder = CosineSimilarityBuilder(
            property_name="title_embedding",
            new_property_name="title_similarity",
            threshold=0.8,
            filter_nodes=filter_title_sim,
        )
        summary_cosine_sim_builder = CosineSimilarityBuilder(
            property_name="technical_summary_embedding",
            new_property_name="summary_similarity",
            threshold=0.8,
            filter_nodes=filter_out_html,
        )
        overlap_threshold = 0.2
        themes_overlap_sim = OverlapScoreBuilder(
            property_name="themes",
            new_property_name="themes_overlap_score",
            distance_threshold=0.94,
            noise_threshold=0.1,
            threshold=overlap_threshold * 1.5,
            filter_nodes=filter_themes_overlap,
        )
        # compare non-html docs with >2 items against each other
        entities_overlap_sim = OverlapScoreBuilder(
            property_name="entities",
            new_property_name="entities_overlap_score",
            distance_threshold=0.93,
            noise_threshold=0.07,
            threshold=overlap_threshold,
            filter_nodes=filter_entities_overlap,
        )
        # compare non-html docs against html docs since HTML docs (user manual) contains the most pertinent named entities
        html_overlap_sim = OverlapScoreBuilder(
            property_name="entities",
            new_property_name="html_overlap_score",
            distance_threshold=0.92,
            threshold=0.03,
            noise_threshold=0.11,
            target_cross_source=target_html_filter,
        )
        transforms = Parallel(
            cosine_sim_builder,
            summary_cosine_sim_builder,
            entities_overlap_sim,
            themes_overlap_sim,
            html_overlap_sim,
        )
        return transforms  # type: ignore

    input_data_df = pd.read_parquet(kg_input_data_path)
    create_kg(input_data_df, get_transforms())
