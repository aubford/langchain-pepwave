#!/usr/bin/env python
# coding: utf-8

# # IPEX-LLM: Local BGE Embeddings on Intel CPU
# 
# > [IPEX-LLM](https://github.com/intel-analytics/ipex-llm) is a PyTorch library for running LLM on Intel CPU and GPU (e.g., local PC with iGPU, discrete GPU such as Arc, Flex and Max) with very low latency.
# 
# This example goes over how to use LangChain to conduct embedding tasks with `ipex-llm` optimizations on Intel CPU. This would be helpful in applications such as RAG, document QA, etc.
# 
# ## Setup

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain-community')


# Install IPEX-LLM for optimizations on Intel CPU, as well as `sentence-transformers`.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --pre --upgrade ipex-llm[all] --extra-index-url https://download.pytorch.org/whl/cpu')
get_ipython().run_line_magic('pip', 'install sentence-transformers')


# > **Note**
# >
# > For Windows users, `--extra-index-url https://download.pytorch.org/whl/cpu` when install `ipex-llm` is not required.
# 
# ## Basic Usage

# In[ ]:


from langchain_community.embeddings import IpexLLMBgeEmbeddings

embedding_model = IpexLLMBgeEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={},
    encode_kwargs={"normalize_embeddings": True},
)


# API Reference
# - [IpexLLMBgeEmbeddings](https://python.langchain.com/api_reference/community/embeddings/langchain_community.embeddings.ipex_llm.IpexLLMBgeEmbeddings.html)

# In[ ]:


sentence = "IPEX-LLM is a PyTorch library for running LLM on Intel CPU and GPU (e.g., local PC with iGPU, discrete GPU such as Arc, Flex and Max) with very low latency."
query = "What is IPEX-LLM?"

text_embeddings = embedding_model.embed_documents([sentence, query])
print(f"text_embeddings[0][:10]: {text_embeddings[0][:10]}")
print(f"text_embeddings[1][:10]: {text_embeddings[1][:10]}")

query_embedding = embedding_model.embed_query(query)
print(f"query_embedding[:10]: {query_embedding[:10]}")

