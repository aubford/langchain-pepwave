#!/usr/bin/env python
# coding: utf-8

# # Text Embeddings Inference
# 
# >[Hugging Face Text Embeddings Inference (TEI)](https://huggingface.co/docs/text-embeddings-inference/index) is a toolkit for deploying and serving open-source
# > text embeddings and sequence classification models. `TEI` enables high-performance extraction for the most popular models,
# >including `FlagEmbedding`, `Ember`, `GTE` and `E5`.
# 
# To use it within langchain, first install `huggingface-hub`.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade huggingface-hub')


# Then expose an embedding model using TEI. For instance, using Docker, you can serve `BAAI/bge-large-en-v1.5` as follows:
# 
# ```bash
# model=BAAI/bge-large-en-v1.5
# revision=refs/pr/5
# volume=$PWD/data # share a volume with the Docker container to avoid downloading weights every run
# 
# docker run --gpus all -p 8080:80 -v $volume:/data --pull always ghcr.io/huggingface/text-embeddings-inference:0.6 --model-id $model --revision $revision
# ```
# 
# Specifics on Docker usage might vary with the underlying hardware. For example, to serve the model on Intel Gaudi/Gaudi2 hardware, refer to the [tei-gaudi repository](https://github.com/huggingface/tei-gaudi) for the relevant docker run command.

# Finally, instantiate the client and embed your texts.

# In[2]:


from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings


# In[3]:


embeddings = HuggingFaceEndpointEmbeddings(model="http://localhost:8080")


# In[4]:


text = "What is deep learning?"


# In[5]:


query_result = embeddings.embed_query(text)
query_result[:3]


# In[6]:


doc_result = embeddings.embed_documents([text])


# In[7]:


doc_result[0][:3]

