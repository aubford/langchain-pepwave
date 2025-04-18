#!/usr/bin/env python
# coding: utf-8

# # Voyage AI
# 
# >[Voyage AI](https://www.voyageai.com/) provides cutting-edge embedding/vectorizations models.
# 
# Let's load the Voyage AI Embedding class. (Install the LangChain partner package with `pip install langchain-voyageai`)

# In[1]:


from langchain_voyageai import VoyageAIEmbeddings


# Voyage AI utilizes API keys to monitor usage and manage permissions. To obtain your key, create an account on our [homepage](https://www.voyageai.com). Then, create a VoyageEmbeddings model with your API key. You can use any of the following models: ([source](https://docs.voyageai.com/docs/embeddings)):
# 
# - `voyage-3-large`
# - `voyage-3`
# - `voyage-3-lite`
# - `voyage-large-2`
# - `voyage-code-2`
# - `voyage-2`
# - `voyage-law-2`
# - `voyage-large-2-instruct`
# - `voyage-finance-2`
# - `voyage-multilingual-2`

# In[2]:


embeddings = VoyageAIEmbeddings(
    voyage_api_key="[ Your Voyage API key ]", model="voyage-law-2"
)


# Prepare the documents and use `embed_documents` to get their embeddings.

# In[3]:


documents = [
    "Caching embeddings enables the storage or temporary caching of embeddings, eliminating the necessity to recompute them each time.",
    "An LLMChain is a chain that composes basic LLM functionality. It consists of a PromptTemplate and a language model (either an LLM or chat model). It formats the prompt template using the input key values provided (and also memory key values, if available), passes the formatted string to LLM and returns the LLM output.",
    "A Runnable represents a generic unit of work that can be invoked, batched, streamed, and/or transformed.",
]


# In[4]:


documents_embds = embeddings.embed_documents(documents)


# In[5]:


documents_embds[0][:5]


# Similarly, use `embed_query` to embed the query.

# In[6]:


query = "What's an LLMChain?"


# In[7]:


query_embd = embeddings.embed_query(query)


# In[8]:


query_embd[:5]


# ## A minimalist retrieval system

# The main feature of the embeddings is that the cosine similarity between two embeddings captures the semantic relatedness of the corresponding original passages. This allows us to use the embeddings to do semantic retrieval / search.

#  We can find a few closest embeddings in the documents embeddings based on the cosine similarity, and retrieve the corresponding document using the `KNNRetriever` class from LangChain.

# In[9]:


from langchain_community.retrievers import KNNRetriever

retriever = KNNRetriever.from_texts(documents, embeddings)

# retrieve the most relevant documents
result = retriever.invoke(query)
top1_retrieved_doc = result[0].page_content  # return the top1 retrieved result

print(top1_retrieved_doc)

