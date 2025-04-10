#!/usr/bin/env python
# coding: utf-8

# # MosaicML
# 
# >[MosaicML](https://docs.mosaicml.com/en/latest/inference.html) offers a managed inference service. You can either use a variety of open-source models, or deploy your own.
# 
# This example goes over how to use LangChain to interact with `MosaicML` Inference for text embedding.

# In[ ]:


# sign up for an account: https://forms.mosaicml.com/demo?utm_source=langchain

from getpass import getpass

MOSAICML_API_TOKEN = getpass()


# In[ ]:


import os

os.environ["MOSAICML_API_TOKEN"] = MOSAICML_API_TOKEN


# In[ ]:


from langchain_community.embeddings import MosaicMLInstructorEmbeddings


# In[ ]:


embeddings = MosaicMLInstructorEmbeddings(
    query_instruction="Represent the query for retrieval: "
)


# In[ ]:


query_text = "This is a test query."
query_result = embeddings.embed_query(query_text)


# In[ ]:


document_text = "This is a test document."
document_result = embeddings.embed_documents([document_text])


# In[ ]:


import numpy as np

query_numpy = np.array(query_result)
document_numpy = np.array(document_result[0])
similarity = np.dot(query_numpy, document_numpy) / (
    np.linalg.norm(query_numpy) * np.linalg.norm(document_numpy)
)
print(f"Cosine similarity between document and query: {similarity}")

