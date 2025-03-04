#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Milvus Hybrid Search
---
# # Milvus Hybrid Search Retriever
# 
# > [Milvus](https://milvus.io/docs) is an open-source vector database built to power embedding similarity search and AI applications. Milvus makes unstructured data search more accessible, and provides a consistent user experience regardless of the deployment environment.
# 
# This will help you getting started with the Milvus Hybrid Search [retriever](/docs/concepts/retrievers), which combines the strengths of both dense and sparse vector search. For detailed documentation of all `MilvusCollectionHybridSearchRetriever` features and configurations head to the [API reference](https://python.langchain.com/api_reference/milvus/retrievers/langchain_milvus.retrievers.milvus_hybrid_search.MilvusCollectionHybridSearchRetriever.html).
# 
# See also the Milvus Multi-Vector Search [docs](https://milvus.io/docs/multi-vector-search.md).
# 
# ### Integration details
# 
# import {ItemTable} from "@theme/FeatureTables";
# 
# <ItemTable category="document_retrievers" item="MilvusCollectionHybridSearchRetriever" />
# 
# ## Setup
# 
# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# This retriever lives in the `langchain-milvus` package. This guide requires the following dependencies:

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet pymilvus[model] langchain-milvus langchain-openai')


# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
from langchain_milvus.utils.sparse import BM25SparseEmbedding
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    WeightedRanker,
    connections,
)


# ### Start the Milvus service
# 
# Please refer to the [Milvus documentation](https://milvus.io/docs/install_standalone-docker.md) to start the Milvus service.
# 
# After starting milvus, you need to specify your milvus connection URI.

# In[4]:


CONNECTION_URI = "http://localhost:19530"


# ### Prepare OpenAI API Key
# 
# Please refer to the [OpenAI documentation](https://platform.openai.com/account/api-keys) to obtain your OpenAI API key, and set it as an environment variable.
# 
# ```shell
# export OPENAI_API_KEY=<your_api_key>
# ```
# 

# ### Prepare dense and sparse embedding functions
# 
# Let us fictionalize 10 fake descriptions of novels. In actual production, it may be a large amount of text data.

# In[5]:


texts = [
    "In 'The Whispering Walls' by Ava Moreno, a young journalist named Sophia uncovers a decades-old conspiracy hidden within the crumbling walls of an ancient mansion, where the whispers of the past threaten to destroy her own sanity.",
    "In 'The Last Refuge' by Ethan Blackwood, a group of survivors must band together to escape a post-apocalyptic wasteland, where the last remnants of humanity cling to life in a desperate bid for survival.",
    "In 'The Memory Thief' by Lila Rose, a charismatic thief with the ability to steal and manipulate memories is hired by a mysterious client to pull off a daring heist, but soon finds themselves trapped in a web of deceit and betrayal.",
    "In 'The City of Echoes' by Julian Saint Clair, a brilliant detective must navigate a labyrinthine metropolis where time is currency, and the rich can live forever, but at a terrible cost to the poor.",
    "In 'The Starlight Serenade' by Ruby Flynn, a shy astronomer discovers a mysterious melody emanating from a distant star, which leads her on a journey to uncover the secrets of the universe and her own heart.",
    "In 'The Shadow Weaver' by Piper Redding, a young orphan discovers she has the ability to weave powerful illusions, but soon finds herself at the center of a deadly game of cat and mouse between rival factions vying for control of the mystical arts.",
    "In 'The Lost Expedition' by Caspian Grey, a team of explorers ventures into the heart of the Amazon rainforest in search of a lost city, but soon finds themselves hunted by a ruthless treasure hunter and the treacherous jungle itself.",
    "In 'The Clockwork Kingdom' by Augusta Wynter, a brilliant inventor discovers a hidden world of clockwork machines and ancient magic, where a rebellion is brewing against the tyrannical ruler of the land.",
    "In 'The Phantom Pilgrim' by Rowan Welles, a charismatic smuggler is hired by a mysterious organization to transport a valuable artifact across a war-torn continent, but soon finds themselves pursued by deadly assassins and rival factions.",
    "In 'The Dreamwalker's Journey' by Lyra Snow, a young dreamwalker discovers she has the ability to enter people's dreams, but soon finds herself trapped in a surreal world of nightmares and illusions, where the boundaries between reality and fantasy blur.",
]


# We will use the [OpenAI Embedding](https://platform.openai.com/docs/guides/embeddings) to generate dense vectors, and the [BM25 algorithm](https://en.wikipedia.org/wiki/Okapi_BM25) to generate sparse vectors.
# 
# Initialize dense embedding function and get dimension

# In[6]:


dense_embedding_func = OpenAIEmbeddings()
dense_dim = len(dense_embedding_func.embed_query(texts[1]))
dense_dim


# Initialize sparse embedding function.
# 
# Note that the output of sparse embedding is a set of sparse vectors, which represents the index and weight of the keywords of the input text.

# In[7]:


sparse_embedding_func = BM25SparseEmbedding(corpus=texts)
sparse_embedding_func.embed_query(texts[1])


# ### Create Milvus Collection and load data
# 
# Initialize connection URI and establish connection

# In[8]:


connections.connect(uri=CONNECTION_URI)


# Define field names and their data types

# In[9]:


pk_field = "doc_id"
dense_field = "dense_vector"
sparse_field = "sparse_vector"
text_field = "text"
fields = [
    FieldSchema(
        name=pk_field,
        dtype=DataType.VARCHAR,
        is_primary=True,
        auto_id=True,
        max_length=100,
    ),
    FieldSchema(name=dense_field, dtype=DataType.FLOAT_VECTOR, dim=dense_dim),
    FieldSchema(name=sparse_field, dtype=DataType.SPARSE_FLOAT_VECTOR),
    FieldSchema(name=text_field, dtype=DataType.VARCHAR, max_length=65_535),
]


# Create a collection with the defined schema

# In[10]:


schema = CollectionSchema(fields=fields, enable_dynamic_field=False)
collection = Collection(
    name="IntroductionToTheNovels", schema=schema, consistency_level="Strong"
)


# Define index for dense and sparse vectors

# In[11]:


dense_index = {"index_type": "FLAT", "metric_type": "IP"}
collection.create_index("dense_vector", dense_index)
sparse_index = {"index_type": "SPARSE_INVERTED_INDEX", "metric_type": "IP"}
collection.create_index("sparse_vector", sparse_index)
collection.flush()


# Insert entities into the collection and load the collection

# In[12]:


entities = []
for text in texts:
    entity = {
        dense_field: dense_embedding_func.embed_documents([text])[0],
        sparse_field: sparse_embedding_func.embed_documents([text])[0],
        text_field: text,
    }
    entities.append(entity)
collection.insert(entities)
collection.load()


# ## Instantiation
# 
# Now we can instantiate our retriever, defining search parameters for sparse and dense fields:

# In[ ]:


sparse_search_params = {"metric_type": "IP"}
dense_search_params = {"metric_type": "IP", "params": {}}
retriever = MilvusCollectionHybridSearchRetriever(
    collection=collection,
    rerank=WeightedRanker(0.5, 0.5),
    anns_fields=[dense_field, sparse_field],
    field_embeddings=[dense_embedding_func, sparse_embedding_func],
    field_search_params=[dense_search_params, sparse_search_params],
    top_k=3,
    text_field=text_field,
)


# In the input parameters of this Retriever, we use a dense embedding and a sparse embedding to perform hybrid search on the two fields of this Collection, and use WeightedRanker for reranking. Finally, 3 top-K Documents will be returned.

# ## Usage

# In[14]:


retriever.invoke("What are the story about ventures?")


# ## Use within a chain
# 
# Initialize ChatOpenAI and define a prompt template

# In[15]:


llm = ChatOpenAI()

PROMPT_TEMPLATE = """
Human: You are an AI assistant, and provides answers to questions by using fact based and statistical information when possible.
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.

<context>
{context}
</context>

<question>
{question}
</question>

Assistant:"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)


# Define a function for formatting documents

# In[16]:


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Define a chain using the retriever and other components

# In[17]:


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# Perform a query using the defined chain

# In[18]:


rag_chain.invoke("What novels has Lila written and what are their contents?")


# Drop the collection

# In[19]:


collection.drop()


# ## API reference
# 
# For detailed documentation of all `MilvusCollectionHybridSearchRetriever` features and configurations head to the [API reference](https://python.langchain.com/api_reference/milvus/retrievers/langchain_milvus.retrievers.milvus_hybrid_search.MilvusCollectionHybridSearchRetriever.html).
