#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Konko
---
# # Konko
# 
# >[Konko](https://www.konko.ai/) API is a fully managed Web API designed to help application developers:
# 
# 1. **Select** the right open source or proprietary LLMs for their application
# 2. **Build** applications faster with integrations to leading application frameworks and fully managed APIs
# 3. **Fine tune** smaller open-source LLMs to achieve industry-leading performance at a fraction of the cost
# 4. **Deploy production-scale APIs** that meet security, privacy, throughput, and latency SLAs without infrastructure set-up or administration using Konko AI's SOC 2 compliant, multi-cloud infrastructure
# 
# This example goes over how to use LangChain to interact with `Konko` completion [models](https://docs.konko.ai/docs/list-of-models#konko-hosted-models-for-completion)
# 
# To run this notebook, you'll need Konko API key. Sign in to our web app to [create an API key](https://platform.konko.ai/settings/api-keys) to access models
# 
# #### Set Environment Variables
# 
# 1. You can set environment variables for 
#    1. KONKO_API_KEY (Required)
#    2. OPENAI_API_KEY (Optional)
# 2. In your current shell session, use the export command:
# 
# ```shell
# export KONKO_API_KEY={your_KONKO_API_KEY_here}
# export OPENAI_API_KEY={your_OPENAI_API_KEY_here} #Optional
# ```
# 
# ## Calling a model
# 
# Find a model on the [Konko overview page](https://docs.konko.ai/docs/list-of-models)
# 
# Another way to find the list of models running on the Konko instance is through this [endpoint](https://docs.konko.ai/reference/get-models).
# 
# From here, we can initialize our model:

# In[ ]:


from langchain_community.llms import Konko

llm = Konko(model="mistralai/mistral-7b-v0.1", temperature=0.1, max_tokens=128)

input_ = """You are a helpful assistant. Explain Big Bang Theory briefly."""
print(llm.invoke(input_))

