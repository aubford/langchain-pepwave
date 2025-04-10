#!/usr/bin/env python
# coding: utf-8

# # Baichuan Text Embeddings
# 
# As of today (Jan 25th, 2024) BaichuanTextEmbeddings ranks #1 in C-MTEB (Chinese Multi-Task Embedding Benchmark) leaderboard.
# 

# Leaderboard (Under Overall -> Chinese section): https://huggingface.co/spaces/mteb/leaderboard

# Official Website: https://platform.baichuan-ai.com/docs/text-Embedding
# 
# An API key is required to use this embedding model. You can get one by registering at https://platform.baichuan-ai.com/docs/text-Embedding.

# BaichuanTextEmbeddings support 512 token window and preduces vectors with 1024 dimensions. 

# Please NOTE that BaichuanTextEmbeddings only supports Chinese text embedding. Multi-language support is coming soon.

# In[ ]:


from langchain_community.embeddings import BaichuanTextEmbeddings

embeddings = BaichuanTextEmbeddings(baichuan_api_key="sk-*")


# Alternatively, you can set API key this way:

# In[ ]:


import os

os.environ["BAICHUAN_API_KEY"] = "YOUR_API_KEY"


# In[ ]:


text_1 = "今天天气不错"
text_2 = "今天阳光很好"

query_result = embeddings.embed_query(text_1)
query_result


# In[ ]:


doc_result = embeddings.embed_documents([text_1, text_2])
doc_result

