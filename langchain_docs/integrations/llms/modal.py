#!/usr/bin/env python
# coding: utf-8

# # Modal
# 
# The [Modal cloud platform](https://modal.com/docs/guide) provides convenient, on-demand access to serverless cloud compute from Python scripts on your local computer. 
# Use `modal` to run your own custom LLM models instead of depending on LLM APIs.
# 
# This example goes over how to use LangChain to interact with a `modal` HTTPS [web endpoint](https://modal.com/docs/guide/webhooks).
# 
# [_Question-answering with LangChain_](https://modal.com/docs/guide/ex/potus_speech_qanda) is another example of how to use LangChain alonside `Modal`. In that example, Modal runs the LangChain application end-to-end and uses OpenAI as its LLM API.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  modal')


# In[2]:


# Register an account with Modal and get a new token.

get_ipython().system('modal token new')


# The [`langchain.llms.modal.Modal`](https://github.com/langchain-ai/langchain/blame/master/langchain/llms/modal.py) integration class requires that you deploy a Modal application with a web endpoint that complies with the following JSON interface:
# 
# 1. The LLM prompt is accepted as a `str` value under the key `"prompt"`
# 2. The LLM response returned as a `str` value under the key `"prompt"`
# 
# **Example request JSON:**
# 
# ```json
# {
#     "prompt": "Identify yourself, bot!",
#     "extra": "args are allowed",
# }
# ```
# 
# **Example response JSON:**
# 
# ```json
# {
#     "prompt": "This is the LLM speaking",
# }
# ```
# 
# An example 'dummy' Modal web endpoint function fulfilling this interface would be
# 
# ```python
# ...
# ...
# 
# class Request(BaseModel):
#     prompt: str
# 
# @stub.function()
# @modal.web_endpoint(method="POST")
# def web(request: Request):
#     _ = request  # ignore input
#     return {"prompt": "hello world"}
# ```
# 
# * See Modal's [web endpoints](https://modal.com/docs/guide/webhooks#passing-arguments-to-web-endpoints) guide for the basics of setting up an endpoint that fulfils this interface.
# * See Modal's ['Run Falcon-40B with AutoGPTQ'](https://modal.com/docs/guide/ex/falcon_gptq) open-source LLM example as a starting point for your custom LLM!

# Once you have a deployed Modal web endpoint, you can pass its URL into the `langchain.llms.modal.Modal` LLM class. This class can then function as a building block in your chain.

# In[ ]:


from langchain.chains import LLMChain
from langchain_community.llms import Modal
from langchain_core.prompts import PromptTemplate


# In[ ]:


template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# In[ ]:


endpoint_url = "https://ecorp--custom-llm-endpoint.modal.run"  # REPLACE ME with your deployed Modal web endpoint's URL
llm = Modal(endpoint_url=endpoint_url)


# In[ ]:


llm_chain = LLMChain(prompt=prompt, llm=llm)


# In[ ]:


question = "What NFL team won the Super Bowl in the year Justin Beiber was born?"

llm_chain.run(question)

