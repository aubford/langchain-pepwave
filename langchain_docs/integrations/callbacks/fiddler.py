#!/usr/bin/env python
# coding: utf-8

# # Fiddler
# 
# >[Fiddler](https://www.fiddler.ai/) is the pioneer in enterprise Generative and Predictive system ops, offering a unified platform that enables Data Science, MLOps, Risk, Compliance, Analytics, and other LOB teams to monitor, explain, analyze, and improve ML deployments at enterprise scale. 

# ## 1. Installation and Setup

# In[ ]:


#!pip install langchain langchain-community langchain-openai fiddler-client


# ## 2. Fiddler connection details 

# *Before you can add information about your model with Fiddler*
# 
# 1. The URL you're using to connect to Fiddler
# 2. Your organization ID
# 3. Your authorization token
# 
# These can be found by navigating to the *Settings* page of your Fiddler environment.

# In[ ]:


URL = ""  # Your Fiddler instance URL, Make sure to include the full URL (including https://). For example: https://demo.fiddler.ai
ORG_NAME = ""
AUTH_TOKEN = ""  # Your Fiddler instance auth token

# Fiddler project and model names, used for model registration
PROJECT_NAME = ""
MODEL_NAME = ""  # Model name in Fiddler


# ## 3. Create a fiddler callback handler instance

# In[ ]:


from langchain_community.callbacks.fiddler_callback import FiddlerCallbackHandler

fiddler_handler = FiddlerCallbackHandler(
    url=URL,
    org=ORG_NAME,
    project=PROJECT_NAME,
    model=MODEL_NAME,
    api_key=AUTH_TOKEN,
)


# ## Example 1 : Basic Chain

# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI

# Note : Make sure openai API key is set in the environment variable OPENAI_API_KEY
llm = OpenAI(temperature=0, streaming=True, callbacks=[fiddler_handler])
output_parser = StrOutputParser()

chain = llm | output_parser

# Invoke the chain. Invocation will be logged to Fiddler, and metrics automatically generated
chain.invoke("How far is moon from earth?")


# In[ ]:


# Few more invocations
chain.invoke("What is the temperature on Mars?")
chain.invoke("How much is 2 + 200000?")
chain.invoke("Which movie won the oscars this year?")
chain.invoke("Can you write me a poem about insomnia?")
chain.invoke("How are you doing today?")
chain.invoke("What is the meaning of life?")


# ## Example 2 : Chain with prompt templates

# In[ ]:


from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

examples = [
    {"input": "2+2", "output": "4"},
    {"input": "2+3", "output": "5"},
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a wondrous wizard of math."),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)

# Note : Make sure openai API key is set in the environment variable OPENAI_API_KEY
llm = OpenAI(temperature=0, streaming=True, callbacks=[fiddler_handler])

chain = final_prompt | llm

# Invoke the chain. Invocation will be logged to Fiddler, and metrics automatically generated
chain.invoke({"input": "What's the square of a triangle?"})

