#!/usr/bin/env python
# coding: utf-8

# # GPT4All
# 
# [GitHub:nomic-ai/gpt4all](https://github.com/nomic-ai/gpt4all) an ecosystem of open-source chatbots trained on a massive collections of clean assistant data including code, stories and dialogue.
# 
# This example goes over how to use LangChain to interact with `GPT4All` models.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-community gpt4all')


# ### Import GPT4All

# In[2]:


from langchain_community.llms import GPT4All
from langchain_core.prompts import PromptTemplate


# ### Set Up Question to pass to LLM

# In[3]:


template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# ### Specify Model
# 
# To run locally, download a compatible ggml-formatted model. 
#  
# The [gpt4all page](https://gpt4all.io/index.html) has a useful `Model Explorer` section:
# 
# * Select a model of interest
# * Download using the UI and move the `.bin` to the `local_path` (noted below)
# 
# For more info, visit https://github.com/nomic-ai/gpt4all.
# 
# ---
# 
# This integration does not yet support streaming in chunks via the [`.stream()`](https://python.langchain.com/docs/how_to/streaming/) method. The below example uses a callback handler with `streaming=True`:

# In[4]:


local_path = (
    "./models/Meta-Llama-3-8B-Instruct.Q4_0.gguf"  # replace with your local file path
)


# In[10]:


from langchain_core.callbacks import BaseCallbackHandler

count = 0


class MyCustomHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        global count
        if count < 10:
            print(f"Token: {token}")
            count += 1


# Verbose is required to pass to the callback manager
llm = GPT4All(model=local_path, callbacks=[MyCustomHandler()], streaming=True)

# If you want to use a custom model add the backend parameter
# Check https://docs.gpt4all.io/gpt4all_python.html for supported backends
# llm = GPT4All(model=local_path, backend="gptj", callbacks=callbacks, streaming=True)

chain = prompt | llm

question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"

# Streamed tokens will be logged/aggregated via the passed callback
res = chain.invoke({"question": question})


# In[ ]:




