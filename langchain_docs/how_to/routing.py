#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 3
keywords: [RunnableBranch, LCEL]
---
# # How to route between sub-chains
# 
# :::info Prerequisites
# 
# This guide assumes familiarity with the following concepts:
# - [LangChain Expression Language (LCEL)](/docs/concepts/lcel)
# - [Chaining runnables](/docs/how_to/sequence/)
# - [Configuring chain parameters at runtime](/docs/how_to/configure)
# - [Prompt templates](/docs/concepts/prompt_templates)
# - [Chat Messages](/docs/concepts/messages)
# 
# :::
# 
# Routing allows you to create non-deterministic chains where the output of a previous step defines the next step. Routing can help provide structure and consistency around interactions with models by allowing you to define states and use information related to those states as context to model calls.
# 
# There are two ways to perform routing:
# 
# 1. Conditionally return runnables from a [`RunnableLambda`](/docs/how_to/functions) (recommended)
# 2. Using a `RunnableBranch` (legacy)
# 
# We'll illustrate both methods using a two step sequence where the first step classifies an input question as being about `LangChain`, `Anthropic`, or `Other`, then routes to a corresponding prompt chain.

# ## Example Setup
# First, let's create a chain that will identify incoming questions as being about `LangChain`, `Anthropic`, or `Other`:

# In[1]:


from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

chain = (
    PromptTemplate.from_template(
        """Given the user question below, classify it as either being about `LangChain`, `Anthropic`, or `Other`.

Do not respond with more than one word.

<question>
{question}
</question>

Classification:"""
    )
    | ChatAnthropic(model_name="claude-3-haiku-20240307")
    | StrOutputParser()
)

chain.invoke({"question": "how do I call Anthropic?"})


# Now, let's create three sub chains:

# In[3]:


langchain_chain = PromptTemplate.from_template(
    """You are an expert in langchain. \
Always answer questions starting with "As Harrison Chase told me". \
Respond to the following question:

Question: {question}
Answer:"""
) | ChatAnthropic(model_name="claude-3-haiku-20240307")
anthropic_chain = PromptTemplate.from_template(
    """You are an expert in anthropic. \
Always answer questions starting with "As Dario Amodei told me". \
Respond to the following question:

Question: {question}
Answer:"""
) | ChatAnthropic(model_name="claude-3-haiku-20240307")
general_chain = PromptTemplate.from_template(
    """Respond to the following question:

Question: {question}
Answer:"""
) | ChatAnthropic(model_name="claude-3-haiku-20240307")


# ## Using a custom function (Recommended)
# 
# You can also use a custom function to route between different outputs. Here's an example:

# In[4]:


def route(info):
    if "anthropic" in info["topic"].lower():
        return anthropic_chain
    elif "langchain" in info["topic"].lower():
        return langchain_chain
    else:
        return general_chain


# In[5]:


from langchain_core.runnables import RunnableLambda

full_chain = {"topic": chain, "question": lambda x: x["question"]} | RunnableLambda(
    route
)


# In[6]:


full_chain.invoke({"question": "how do I use Anthropic?"})


# In[7]:


full_chain.invoke({"question": "how do I use LangChain?"})


# In[8]:


full_chain.invoke({"question": "whats 2 + 2"})


# ## Using a RunnableBranch
# 
# A `RunnableBranch` is a special type of runnable that allows you to define a set of conditions and runnables to execute based on the input. It does **not** offer anything that you can't achieve in a custom function as described above, so we recommend using a custom function instead.
# 
# A `RunnableBranch` is initialized with a list of (condition, runnable) pairs and a default runnable. It selects which branch by passing each condition the input it's invoked with. It selects the first condition to evaluate to True, and runs the corresponding runnable to that condition with the input. 
# 
# If no provided conditions match, it runs the default runnable.
# 
# Here's an example of what it looks like in action:

# In[9]:


from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: "anthropic" in x["topic"].lower(), anthropic_chain),
    (lambda x: "langchain" in x["topic"].lower(), langchain_chain),
    general_chain,
)
full_chain = {"topic": chain, "question": lambda x: x["question"]} | branch
full_chain.invoke({"question": "how do I use Anthropic?"})


# In[10]:


full_chain.invoke({"question": "how do I use LangChain?"})


# In[11]:


full_chain.invoke({"question": "whats 2 + 2"})


# ## Routing by semantic similarity
# 
# One especially useful technique is to use embeddings to route a query to the most relevant prompt. Here's an example.

# In[12]:


from langchain_community.utils.math import cosine_similarity
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import OpenAIEmbeddings

physics_template = """You are a very smart physics professor. \
You are great at answering questions about physics in a concise and easy to understand manner. \
When you don't know the answer to a question you admit that you don't know.

Here is a question:
{query}"""

math_template = """You are a very good mathematician. You are great at answering math questions. \
You are so good because you are able to break down hard problems into their component parts, \
answer the component parts, and then put them together to answer the broader question.

Here is a question:
{query}"""

embeddings = OpenAIEmbeddings()
prompt_templates = [physics_template, math_template]
prompt_embeddings = embeddings.embed_documents(prompt_templates)


def prompt_router(input):
    query_embedding = embeddings.embed_query(input["query"])
    similarity = cosine_similarity([query_embedding], prompt_embeddings)[0]
    most_similar = prompt_templates[similarity.argmax()]
    print("Using MATH" if most_similar == math_template else "Using PHYSICS")
    return PromptTemplate.from_template(most_similar)


chain = (
    {"query": RunnablePassthrough()}
    | RunnableLambda(prompt_router)
    | ChatAnthropic(model="claude-3-haiku-20240307")
    | StrOutputParser()
)


# In[13]:


print(chain.invoke("What's a black hole"))


# In[14]:


print(chain.invoke("What's a path integral"))


# ## Next steps
# 
# You've now learned how to add routing to your composed LCEL chains.
# 
# Next, check out the other how-to guides on runnables in this section.

# 
