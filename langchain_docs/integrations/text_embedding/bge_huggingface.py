#!/usr/bin/env python
# coding: utf-8

# # BGE on Hugging Face
# 
# >[BGE models on the HuggingFace](https://huggingface.co/BAAI/bge-large-en-v1.5) are one of [the best open-source embedding models](https://huggingface.co/spaces/mteb/leaderboard).
# >BGE model is created by the [Beijing Academy of Artificial Intelligence (BAAI)](https://en.wikipedia.org/wiki/Beijing_Academy_of_Artificial_Intelligence). `BAAI` is a private non-profit organization engaged in AI research and development.
# 
# This notebook shows how to use `BGE Embeddings` through `Hugging Face`

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  sentence_transformers')


# In[ ]:


from langchain_community.embeddings import HuggingFaceBgeEmbeddings

model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
hf = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)


# Note that you need to pass `query_instruction=""` for `model_name="BAAI/bge-m3"` see [FAQ BGE M3](https://huggingface.co/BAAI/bge-m3#faq). 

# In[5]:


embedding = hf.embed_query("hi this is harrison")
len(embedding)


# In[ ]:




