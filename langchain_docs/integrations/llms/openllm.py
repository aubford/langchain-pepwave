#!/usr/bin/env python
# coding: utf-8

# # OpenLLM
# 
# [🦾 OpenLLM](https://github.com/bentoml/OpenLLM) lets developers run any **open-source LLMs** as **OpenAI-compatible API** endpoints with **a single command**.
# 
# - 🔬 Build for fast and production usages
# - 🚂 Support llama3, qwen2, gemma, etc, and many **quantized** versions [full list](https://github.com/bentoml/openllm-models)
# - ⛓️ OpenAI-compatible API
# - 💬 Built-in ChatGPT like UI
# - 🔥 Accelerated LLM decoding with state-of-the-art inference backends
# - 🌥️ Ready for enterprise-grade cloud deployment (Kubernetes, Docker and BentoCloud)

# ## Installation
# 
# Install `openllm` through [PyPI](https://pypi.org/project/openllm/)

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  openllm')


# ## Launch OpenLLM server locally
# 
# To start an LLM server, use `openllm hello` command:
# 
# ```bash
# openllm hello
# ```
# 
# 
# ## Wrapper

# In[ ]:


from langchain_community.llms import OpenLLM

server_url = "http://localhost:3000"  # Replace with remote host if you are running on a remote server
llm = OpenLLM(base_url=server_url, api_key="na")


# In[ ]:


llm("To build a LLM from scratch, the following are the steps:")

