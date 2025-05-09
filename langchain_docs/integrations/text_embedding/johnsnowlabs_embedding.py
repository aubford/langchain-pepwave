#!/usr/bin/env python
# coding: utf-8

# # John Snow Labs
# 
# >[John Snow Labs](https://nlp.johnsnowlabs.com/) NLP & LLM ecosystem includes software libraries for state-of-the-art AI at scale, Responsible AI, No-Code AI, and access to over 20,000 models for Healthcare, Legal, Finance, etc.
# >
# >Models are loaded with [nlp.load](https://nlp.johnsnowlabs.com/docs/en/jsl/load_api) and spark session is started >with [nlp.start()](https://nlp.johnsnowlabs.com/docs/en/jsl/start-a-sparksession) under the hood.
# >For all 24.000+ models, see the [John Snow Labs Model Models Hub](https://nlp.johnsnowlabs.com/models)
# 

# ## Setting up

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  johnsnowlabs')


# In[ ]:


# If you have a enterprise license, you can run this to install enterprise features
# from johnsnowlabs import nlp
# nlp.install()


# ## Example

# In[ ]:


from langchain_community.embeddings.johnsnowlabs import JohnSnowLabsEmbeddings


# Initialize Johnsnowlabs Embeddings and Spark Session

# In[ ]:


embedder = JohnSnowLabsEmbeddings("en.embed_sentence.biobert.clinical_base_cased")


# Define some example texts . These could be any documents that you want to analyze - for example, news articles, social media posts, or product reviews.

# In[ ]:


texts = ["Cancer is caused by smoking", "Antibiotics aren't painkiller"]


# Generate and print embeddings for the texts . The JohnSnowLabsEmbeddings class generates an embedding for each document, which is a numerical representation of the document's content. These embeddings can be used for various natural language processing tasks, such as document similarity comparison or text classification.

# In[ ]:


embeddings = embedder.embed_documents(texts)
for i, embedding in enumerate(embeddings):
    print(f"Embedding for document {i+1}: {embedding}")


# Generate and print an embedding for a single piece of text. You can also generate an embedding for a single piece of text, such as a search query. This can be useful for tasks like information retrieval, where you want to find documents that are similar to a given query.

# In[ ]:


query = "Cancer is caused by smoking"
query_embedding = embedder.embed_query(query)
print(f"Embedding for query: {query_embedding}")

