#!/usr/bin/env python
# coding: utf-8

# # TextGen
# 
# [GitHub:oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui) A gradio web UI for running Large Language Models like LLaMA, llama.cpp, GPT-J, Pythia, OPT, and GALACTICA.
# 
# This example goes over how to use LangChain to interact with LLM models via the `text-generation-webui` API integration.
# 
# Please ensure that you have `text-generation-webui` configured and an LLM installed.  Recommended installation via the [one-click installer appropriate](https://github.com/oobabooga/text-generation-webui#one-click-installers) for your OS.
# 
# Once `text-generation-webui` is installed and confirmed working via the web interface, please enable the `api` option either through the web model configuration tab, or by adding the run-time arg `--api` to your start command.

# ## Set model_url and run the example

# In[ ]:


model_url = "http://localhost:5000"


# In[ ]:


from langchain.chains import LLMChain
from langchain.globals import set_debug
from langchain_community.llms import TextGen
from langchain_core.prompts import PromptTemplate

set_debug(True)

template = """Question: {question}

Answer: Let's think step by step."""


prompt = PromptTemplate.from_template(template)
llm = TextGen(model_url=model_url)
llm_chain = LLMChain(prompt=prompt, llm=llm)
question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"

llm_chain.run(question)


# ### Streaming Version

# You should install websocket-client to use this feature.
# `pip install websocket-client`

# In[ ]:


model_url = "ws://localhost:5005"


# In[ ]:


from langchain.chains import LLMChain
from langchain.globals import set_debug
from langchain_community.llms import TextGen
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

set_debug(True)

template = """Question: {question}

Answer: Let's think step by step."""


prompt = PromptTemplate.from_template(template)
llm = TextGen(
    model_url=model_url, streaming=True, callbacks=[StreamingStdOutCallbackHandler()]
)
llm_chain = LLMChain(prompt=prompt, llm=llm)
question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"

llm_chain.run(question)


# In[ ]:


llm = TextGen(model_url=model_url, streaming=True)
for chunk in llm.stream("Ask 'Hi, how are you?' like a pirate:'", stop=["'", "\n"]):
    print(chunk, end="", flush=True)

