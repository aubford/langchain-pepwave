#!/usr/bin/env python
# coding: utf-8
---
keywords: [Runnable, Runnables, RunnableSequence, LCEL, chain, chains, chaining]
---
# # How to chain runnables
# 
# :::info Prerequisites
# 
# This guide assumes familiarity with the following concepts:
# - [LangChain Expression Language (LCEL)](/docs/concepts/lcel)
# - [Prompt templates](/docs/concepts/prompt_templates)
# - [Chat models](/docs/concepts/chat_models)
# - [Output parser](/docs/concepts/output_parsers)
# 
# :::
# 
# One point about [LangChain Expression Language](/docs/concepts/lcel) is that any two runnables can be "chained" together into sequences. The output of the previous runnable's `.invoke()` call is passed as input to the next runnable. This can be done using the pipe operator (`|`), or the more explicit `.pipe()` method, which does the same thing.
# 
# The resulting [`RunnableSequence`](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableSequence.html) is itself a runnable, which means it can be invoked, streamed, or further chained just like any other runnable. Advantages of chaining runnables in this way are efficient streaming (the sequence will stream output as soon as it is available), and debugging and tracing with tools like [LangSmith](/docs/how_to/debugging).
# 
# ## The pipe operator: `|`
# 
# To show off how this works, let's go through an example. We'll walk through a common pattern in LangChain: using a [prompt template](/docs/how_to#prompt-templates) to format input into a [chat model](/docs/how_to#chat-models), and finally converting the chat message output into a string with an [output parser](/docs/how_to#output-parsers).
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs
#   customVarName="model"
# />
# 

# In[1]:


# | output: false
# | echo: false

import os
from getpass import getpass

from langchain_anthropic import ChatAnthropic

if "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = getpass()

model = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)


# In[2]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")

chain = prompt | model | StrOutputParser()


# Prompts and models are both runnable, and the output type from the prompt call is the same as the input type of the chat model, so we can chain them together. We can then invoke the resulting sequence like any other runnable:

# In[3]:


chain.invoke({"topic": "bears"})


# ### Coercion
# 
# We can even combine this chain with more runnables to create another chain. This may involve some input/output formatting using other types of runnables, depending on the required inputs and outputs of the chain components.
# 
# For example, let's say we wanted to compose the joke generating chain with another chain that evaluates whether or not the generated joke was funny.
# 
# We would need to be careful with how we format the input into the next chain. In the below example, the dict in the chain is automatically parsed and converted into a [`RunnableParallel`](/docs/how_to/parallel), which runs all of its values in parallel and returns a dict with the results.
# 
# This happens to be the same format the next prompt template expects. Here it is in action:

# In[4]:


from langchain_core.output_parsers import StrOutputParser

analysis_prompt = ChatPromptTemplate.from_template("is this a funny joke? {joke}")

composed_chain = {"joke": chain} | analysis_prompt | model | StrOutputParser()

composed_chain.invoke({"topic": "bears"})


# Functions will also be coerced into runnables, so you can add custom logic to your chains too. The below chain results in the same logical flow as before:

# In[5]:


composed_chain_with_lambda = (
    chain
    | (lambda input: {"joke": input})
    | analysis_prompt
    | model
    | StrOutputParser()
)

composed_chain_with_lambda.invoke({"topic": "beets"})


# However, keep in mind that using functions like this may interfere with operations like streaming. See [this section](/docs/how_to/functions) for more information.

# ## The `.pipe()` method
# 
# We could also compose the same sequence using the `.pipe()` method. Here's what that looks like:

# In[6]:


from langchain_core.runnables import RunnableParallel

composed_chain_with_pipe = (
    RunnableParallel({"joke": chain})
    .pipe(analysis_prompt)
    .pipe(model)
    .pipe(StrOutputParser())
)

composed_chain_with_pipe.invoke({"topic": "battlestar galactica"})


# Or the abbreviated:

# In[ ]:


composed_chain_with_pipe = RunnableParallel({"joke": chain}).pipe(
    analysis_prompt, model, StrOutputParser()
)


# ## Related
# 
# - [Streaming](/docs/how_to/streaming/): Check out the streaming guide to understand the streaming behavior of a chain
# 
