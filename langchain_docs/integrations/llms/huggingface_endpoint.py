#!/usr/bin/env python
# coding: utf-8

# # Huggingface Endpoints
# 
# >The [Hugging Face Hub](https://huggingface.co/docs/hub/index) is a platform with over 120k models, 20k datasets, and 50k demo apps (Spaces), all open source and publicly available, in an online platform where people can easily collaborate and build ML together.
# 
# The `Hugging Face Hub` also offers various endpoints to build ML applications.
# This example showcases how to connect to the different Endpoints types.
# 
# In particular, text generation inference is powered by [Text Generation Inference](https://github.com/huggingface/text-generation-inference): a custom-built Rust, Python and gRPC server for blazing-faset text generation inference.

# In[ ]:


from langchain_huggingface import HuggingFaceEndpoint


# ## Installation and Setup

# To use, you should have the ``huggingface_hub`` python [package installed](https://huggingface.co/docs/huggingface_hub/installation).

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet huggingface_hub')


# In[ ]:


# get a token: https://huggingface.co/docs/api-inference/quicktour#get-your-api-token

from getpass import getpass

HUGGINGFACEHUB_API_TOKEN = getpass()


# In[ ]:


import os

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN


# ## Prepare Examples

# In[ ]:


from langchain_huggingface import HuggingFaceEndpoint


# In[ ]:


from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate


# In[ ]:


question = "Who won the FIFA World Cup in the year 1994? "

template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# ## Examples
# 
# Here is an example of how you can access `HuggingFaceEndpoint` integration of the free [Serverless Endpoints](https://huggingface.co/inference-endpoints/serverless) API.

# In[ ]:


repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    max_length=128,
    temperature=0.5,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
)
llm_chain = prompt | llm
print(llm_chain.invoke({"question": question}))


# ## Dedicated Endpoint
# 
# 
# The free serverless API lets you implement solutions and iterate in no time, but it may be rate limited for heavy use cases, since the loads are shared with other requests.
# 
# For enterprise workloads, the best is to use [Inference Endpoints - Dedicated](https://huggingface.co/inference-endpoints/dedicated).
# This gives access to a fully managed infrastructure that offer more flexibility and speed. These resoucres come with continuous support and uptime guarantees, as well as options like AutoScaling
# 
# 

# In[ ]:


# Set the url to your Inference Endpoint below
your_endpoint_url = "https://fayjubiy2xqn36z0.us-east-1.aws.endpoints.huggingface.cloud"


# In[ ]:


llm = HuggingFaceEndpoint(
    endpoint_url=f"{your_endpoint_url}",
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
)
llm("What did foo say about bar?")


# ### Streaming

# In[ ]:


from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_huggingface import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    endpoint_url=f"{your_endpoint_url}",
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
    streaming=True,
)
llm("What did foo say about bar?", callbacks=[StreamingStdOutCallbackHandler()])


# This same `HuggingFaceEndpoint` class can be used with a local [HuggingFace TGI instance](https://github.com/huggingface/text-generation-inference/blob/main/docs/source/index.md) serving the LLM. Check out the TGI [repository](https://github.com/huggingface/text-generation-inference/tree/main) for details on various hardware (GPU, TPU, Gaudi...) support.
