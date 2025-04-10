#!/usr/bin/env python
# coding: utf-8

# # DeepSparse
# 
# This page covers how to use the [DeepSparse](https://github.com/neuralmagic/deepsparse) inference runtime within LangChain.
# It is broken into two parts: installation and setup, and then examples of DeepSparse usage.
# 
# ## Installation and Setup
# 
# - Install the Python package with `pip install deepsparse`
# - Choose a [SparseZoo model](https://sparsezoo.neuralmagic.com/?useCase=text_generation) or export a support model to ONNX [using Optimum](https://github.com/neuralmagic/notebooks/blob/main/notebooks/opt-text-generation-deepsparse-quickstart/OPT_Text_Generation_DeepSparse_Quickstart.ipynb)
# 
# 
# There exists a DeepSparse LLM wrapper, that provides a unified interface for all models:

# In[ ]:


from langchain_community.llms import DeepSparse

llm = DeepSparse(
    model="zoo:nlg/text_generation/codegen_mono-350m/pytorch/huggingface/bigpython_bigquery_thepile/base-none"
)

print(llm.invoke("def fib():"))


# Additional parameters can be passed using the `config` parameter:

# In[ ]:


config = {"max_generated_tokens": 256}

llm = DeepSparse(
    model="zoo:nlg/text_generation/codegen_mono-350m/pytorch/huggingface/bigpython_bigquery_thepile/base-none",
    config=config,
)

