#!/usr/bin/env python
# coding: utf-8

# # Docugami
# This notebook covers how to load documents from `Docugami`. It provides the advantages of using this system over alternative data loaders.
# 
# ## Prerequisites
# 1. Install necessary python packages.
# 2. Grab an access token for your workspace, and make sure it is set as the `DOCUGAMI_API_KEY` environment variable.
# 3. Grab some docset and document IDs for your processed documents, as described here: https://help.docugami.com/home/docugami-api

# In[1]:


# You need the dgml-utils package to use the DocugamiLoader (run pip install directly without "poetry run" if you are not using poetry)
get_ipython().system('poetry run pip install docugami-langchain dgml-utils==0.3.0 --upgrade --quiet')


# ## Quick start
# 
# 1. Create a [Docugami workspace](http://www.docugami.com) (free trials available)
# 2. Add your documents (PDF, DOCX or DOC) and allow Docugami to ingest and cluster them into sets of similar documents, e.g. NDAs, Lease Agreements, and Service Agreements. There is no fixed set of document types supported by the system, the clusters created depend on your particular documents, and you can [change the docset assignments](https://help.docugami.com/home/working-with-the-doc-sets-view) later.
# 3. Create an access token via the Developer Playground for your workspace. [Detailed instructions](https://help.docugami.com/home/docugami-api)
# 4. Explore the [Docugami API](https://api-docs.docugami.com) to get a list of your processed docset IDs, or just the document IDs for a particular docset. 
# 6. Use the DocugamiLoader as detailed below, to get rich semantic chunks for your documents.
# 7. Optionally, build and publish one or more [reports or abstracts](https://help.docugami.com/home/reports). This helps Docugami improve the semantic XML with better tags based on your preferences, which are then added to the DocugamiLoader output as metadata. Use techniques like [self-querying retriever](/docs/how_to/self_query) to do high accuracy Document QA.
# 
# ## Advantages vs Other Chunking Techniques
# 
# Appropriate chunking of your documents is critical for retrieval from documents. Many chunking techniques exist, including simple ones that rely on whitespace and recursive chunk splitting based on character length. Docugami offers a different approach:
# 
# 1. **Intelligent Chunking:** Docugami breaks down every document into a hierarchical semantic XML tree of chunks of varying sizes, from single words or numerical values to entire sections. These chunks follow the semantic contours of the document, providing a more meaningful representation than arbitrary length or simple whitespace-based chunking.
# 2. **Semantic Annotations:** Chunks are annotated with semantic tags that are coherent across the document set, facilitating consistent hierarchical queries across multiple documents, even if they are written and formatted differently. For example, in set of lease agreements, you can easily identify key provisions like the Landlord, Tenant, or Renewal Date, as well as more complex information such as the wording of any sub-lease provision or whether a specific jurisdiction has an exception section within a Termination Clause.
# 3. **Structured Representation:** In addition, the XML tree indicates the structural contours of every document, using attributes denoting headings, paragraphs, lists, tables, and other common elements, and does that consistently across all supported document formats, such as scanned PDFs or DOCX files. It appropriately handles long-form document characteristics like page headers/footers or multi-column flows for clean text extraction.
# 4. **Additional Metadata:** Chunks are also annotated with additional metadata, if a user has been using Docugami. This additional metadata can be used for high-accuracy Document QA without context window restrictions. See detailed code walk-through below.
# 

# In[2]:


import os

from docugami_langchain.document_loaders import DocugamiLoader


# ## Load Documents
# 
# If the DOCUGAMI_API_KEY environment variable is set, there is no need to pass it in to the loader explicitly otherwise you can pass it in as the `access_token` parameter.

# In[3]:


DOCUGAMI_API_KEY = os.environ.get("DOCUGAMI_API_KEY")


# In[4]:


docset_id = "26xpy3aes7xp"
document_ids = ["d7jqdzcj50sj", "cgd1eacfkchw"]

# To load all docs in the given docset ID, just don't provide document_ids
loader = DocugamiLoader(docset_id=docset_id, document_ids=document_ids)
chunks = loader.load()
len(chunks)


# The `metadata` for each `Document` (really, a chunk of an actual PDF, DOC or DOCX) contains some useful additional information:
# 
# 1. **id and source:** ID and Name of the file (PDF, DOC or DOCX) the chunk is sourced from within Docugami.
# 2. **xpath:** XPath inside the XML representation of the document, for the chunk. Useful for source citations directly to the actual chunk inside the document XML.
# 3. **structure:** Structural attributes of the chunk, e.g. h1, h2, div, table, td, etc. Useful to filter out certain kinds of chunks if needed by the caller.
# 4. **tag:** Semantic tag for the chunk, using various generative and extractive techniques. More details here: https://github.com/docugami/DFM-benchmarks
# 
# You can control chunking behavior by setting the following properties on the `DocugamiLoader` instance:
# 
# 1. You can set min and max chunk size, which the system tries to adhere to with minimal truncation. You can set `loader.min_text_length` and `loader.max_text_length` to control these.
# 2. By default, only the text for chunks is returned. However, Docugami's XML knowledge graph has additional rich information including semantic tags for entities inside the chunk. Set `loader.include_xml_tags = True` if you want the additional xml metadata on the returned chunks.
# 3. In addition, you can set `loader.parent_hierarchy_levels` if you want Docugami to return parent chunks in the chunks it returns. The child chunks point to the parent chunks via the `loader.parent_id_key` value. This is useful e.g. with the [MultiVector Retriever](/docs/how_to/multi_vector) for [small-to-big](https://www.youtube.com/watch?v=ihSiRrOUwmg) retrieval. See detailed example later in this notebook.

# In[5]:


loader.min_text_length = 64
loader.include_xml_tags = True
chunks = loader.load()

for chunk in chunks[:5]:
    print(chunk)


# ## Basic Use: Docugami Loader for Document QA
# 
# You can use the Docugami Loader like a standard loader for Document QA over multiple docs, albeit with much better chunks that follow the natural contours of the document. There are many great tutorials on how to do this, e.g. [this one](https://www.youtube.com/watch?v=3yPBVii7Ct0). We can just use the same code, but use the `DocugamiLoader` for better chunking, instead of loading text or PDF files directly with basic splitting techniques.

# In[6]:


get_ipython().system('poetry run pip install --upgrade langchain-openai tiktoken langchain-chroma hnswlib')


# In[7]:


# For this example, we already have a processed docset for a set of lease documents
loader = DocugamiLoader(docset_id="zo954yqy53wp")
chunks = loader.load()

# strip semantic metadata intentionally, to test how things work without semantic metadata
for chunk in chunks:
    stripped_metadata = chunk.metadata.copy()
    for key in chunk.metadata:
        if key not in ["name", "xpath", "id", "structure"]:
            # remove semantic metadata
            del stripped_metadata[key]
    chunk.metadata = stripped_metadata

print(len(chunks))


# The documents returned by the loader are already split, so we don't need to use a text splitter. Optionally, we can use the metadata on each document, for example the structure or tag attributes, to do any post-processing we want.
# 
# We will just use the output of the `DocugamiLoader` as-is to set up a retrieval QA chain the usual way.

# In[8]:


from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_openai import OpenAI, OpenAIEmbeddings

embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(documents=chunks, embedding=embedding)
retriever = vectordb.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(), chain_type="stuff", retriever=retriever, return_source_documents=True
)


# In[9]:


# Try out the retriever with an example query
qa_chain("What can tenants do with signage on their properties?")


# ## Using Docugami Knowledge Graph for High Accuracy Document QA
# 
# One issue with large documents is that the correct answer to your question may depend on chunks that are far apart in the document. Typical chunking techniques, even with overlap, will struggle with providing the LLM sufficent context to answer such questions. With upcoming very large context LLMs, it may be possible to stuff a lot of tokens, perhaps even entire documents, inside the context but this will still hit limits at some point with very long documents, or a lot of documents.
# 
# For example, if we ask a more complex question that requires the LLM to draw on chunks from different parts of the document, even OpenAI's powerful LLM is unable to answer correctly.

# In[10]:


chain_response = qa_chain("What is rentable area for the property owned by DHA Group?")
chain_response["result"]  # correct answer should be 13,500 sq ft


# In[11]:


chain_response["source_documents"]


# At first glance the answer may seem reasonable, but it is incorrect. If you review the source chunks carefully for this answer, you will see that the chunking of the document did not end up putting the Landlord name and the rentable area in the same context, and produced irrelevant chunks therefore the answer is incorrect (should be **13,500 sq ft**)

# Docugami can help here. Chunks are annotated with additional metadata created using different techniques if a user has been [using Docugami](https://help.docugami.com/home/reports). More technical approaches will be added later.
# 
# Specifically, let's ask Docugami to return XML tags on its output, as well as additional metadata:

# In[12]:


loader = DocugamiLoader(docset_id="zo954yqy53wp")
loader.include_xml_tags = (
    True  # for additional semantics from the Docugami knowledge graph
)
chunks = loader.load()
print(chunks[0].metadata)


# We can use a [self-querying retriever](/docs/how_to/self_query) to improve our query accuracy, using this additional metadata:

# In[13]:


get_ipython().system('poetry run pip install --upgrade lark --quiet')


# In[14]:


from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_chroma import Chroma

EXCLUDE_KEYS = ["id", "xpath", "structure"]
metadata_field_info = [
    AttributeInfo(
        name=key,
        description=f"The {key} for this chunk",
        type="string",
    )
    for key in chunks[0].metadata
    if key.lower() not in EXCLUDE_KEYS
]

document_content_description = "Contents of this chunk"
llm = OpenAI(temperature=0)

vectordb = Chroma.from_documents(documents=chunks, embedding=embedding)
retriever = SelfQueryRetriever.from_llm(
    llm, vectordb, document_content_description, metadata_field_info, verbose=True
)
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=True,
)


# Let's run the same question again. It returns the correct result since all the chunks have metadata key/value pairs on them carrying key information about the document even if this information is physically very far away from the source chunk used to generate the answer.

# In[15]:


qa_chain(
    "What is rentable area for the property owned by DHA Group?"
)  # correct answer should be 13,500 sq ft


# This time the answer is correct, since the self-querying retriever created a filter on the landlord attribute of the metadata, correctly filtering to document that specifically is about the DHA Group landlord. The resulting source chunks are all relevant to this landlord, and this improves answer accuracy even though the landlord is not directly mentioned in the specific chunk that contains the correct answer.

# # Advanced Topic: Small-to-Big Retrieval with Document Knowledge Graph Hierarchy

# Documents are inherently semi-structured and the DocugamiLoader is able to navigate the semantic and structural contours of the document to provide parent chunk references on the chunks it returns. This is useful e.g. with the [MultiVector Retriever](/docs/how_to/multi_vector) for [small-to-big](https://www.youtube.com/watch?v=ihSiRrOUwmg) retrieval.
# 
# To get parent chunk references, you can set `loader.parent_hierarchy_levels` to a non-zero value.

# In[16]:


from typing import Dict, List

from docugami_langchain.document_loaders import DocugamiLoader
from langchain_core.documents import Document

loader = DocugamiLoader(docset_id="zo954yqy53wp")
loader.include_xml_tags = (
    True  # for additional semantics from the Docugami knowledge graph
)
loader.parent_hierarchy_levels = 3  # for expanded context
loader.max_text_length = (
    1024 * 8
)  # 8K chars are roughly 2K tokens (ref: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)
loader.include_project_metadata_in_doc_metadata = (
    False  # Not filtering on vector metadata, so remove to lighten the vectors
)
chunks: List[Document] = loader.load()

# build separate maps of parent and child chunks
parents_by_id: Dict[str, Document] = {}
children_by_id: Dict[str, Document] = {}
for chunk in chunks:
    chunk_id = chunk.metadata.get("id")
    parent_chunk_id = chunk.metadata.get(loader.parent_id_key)
    if not parent_chunk_id:
        # parent chunk
        parents_by_id[chunk_id] = chunk
    else:
        # child chunk
        children_by_id[chunk_id] = chunk


# In[17]:


# Explore some of the parent chunk relationships
for id, chunk in list(children_by_id.items())[:5]:
    parent_chunk_id = chunk.metadata.get(loader.parent_id_key)
    if parent_chunk_id:
        # child chunks have the parent chunk id set
        print(f"PARENT CHUNK {parent_chunk_id}: {parents_by_id[parent_chunk_id]}")
        print(f"CHUNK {id}: {chunk}")


# In[18]:


from langchain.retrievers.multi_vector import MultiVectorRetriever, SearchType
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# The vectorstore to use to index the child chunks
vectorstore = Chroma(collection_name="big2small", embedding_function=OpenAIEmbeddings())

# The storage layer for the parent documents
store = InMemoryStore()

# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=store,
    search_type=SearchType.mmr,  # use max marginal relevance search
    search_kwargs={"k": 2},
)

# Add child chunks to vector store
retriever.vectorstore.add_documents(list(children_by_id.values()))

# Add parent chunks to docstore
retriever.docstore.mset(parents_by_id.items())


# In[19]:


# Query vector store directly, should return chunks
found_chunks = vectorstore.similarity_search(
    "what signs does Birch Street allow on their property?", k=2
)

for chunk in found_chunks:
    print(chunk.page_content)
    print(chunk.metadata[loader.parent_id_key])


# In[20]:


# Query retriever, should return parents (using MMR since that was set as search_type above)
retrieved_parent_docs = retriever.invoke(
    "what signs does Birch Street allow on their property?"
)
for chunk in retrieved_parent_docs:
    print(chunk.page_content)
    print(chunk.metadata["id"])

