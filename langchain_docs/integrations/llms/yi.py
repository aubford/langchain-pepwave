#!/usr/bin/env python
# coding: utf-8

# # Yi
# [01.AI](https://www.lingyiwanwu.com/en), founded by Dr. Kai-Fu Lee, is a global company at the forefront of AI 2.0. They offer cutting-edge large language models, including the Yi series, which range from 6B to hundreds of billions of parameters. 01.AI also provides multimodal models, an open API platform, and open-source options like Yi-34B/9B/6B and Yi-VL.

# In[ ]:


## Installing the langchain packages needed to use the integration
get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# ## Prerequisite
# An API key is required to access Yi LLM API. Visit https://www.lingyiwanwu.com/ to get your API key. When applying for the API key, you need to specify whether it's for domestic (China) or international use.

# ## Use Yi LLM

# In[ ]:


import os

os.environ["YI_API_KEY"] = "YOUR_API_KEY"

from langchain_community.llms import YiLLM

# Load the model
llm = YiLLM(model="yi-large")

# You can specify the region if needed (default is "auto")
# llm = YiLLM(model="yi-large", region="domestic")  # or "international"

# Basic usage
res = llm.invoke("What's your name?")
print(res)


# In[ ]:


# Generate method
res = llm.generate(
    prompts=[
        "Explain the concept of large language models.",
        "What are the potential applications of AI in healthcare?",
    ]
)
print(res)


# In[ ]:


# Streaming
for chunk in llm.stream("Describe the key features of the Yi language model series."):
    print(chunk, end="", flush=True)


# In[ ]:


# Asynchronous streaming
import asyncio


async def run_aio_stream():
    async for chunk in llm.astream(
        "Write a brief on the future of AI according to Dr. Kai-Fu Lee's vision."
    ):
        print(chunk, end="", flush=True)


asyncio.run(run_aio_stream())


# In[ ]:


# Adjusting parameters
llm_with_params = YiLLM(
    model="yi-large",
    temperature=0.7,
    top_p=0.9,
)

res = llm_with_params(
    "Propose an innovative AI application that could benefit society."
)
print(res)

