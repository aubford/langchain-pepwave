#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 3
keywords: [RunnableLambda, LCEL]
---
# # How to run custom functions
# 
# :::info Prerequisites
# 
# This guide assumes familiarity with the following concepts:
# - [LangChain Expression Language (LCEL)](/docs/concepts/lcel)
# - [Chaining runnables](/docs/how_to/sequence/)
# 
# :::
# 
# You can use arbitrary functions as [Runnables](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.Runnable.html#langchain_core.runnables.base.Runnable). This is useful for formatting or when you need functionality not provided by other LangChain components, and custom functions used as Runnables are called [`RunnableLambdas`](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableLambda.html).
# 
# Note that all inputs to these functions need to be a SINGLE argument. If you have a function that accepts multiple arguments, you should write a wrapper that accepts a single dict input and unpacks it into multiple arguments.
# 
# This guide will cover:
# 
# - How to explicitly create a runnable from a custom function using the `RunnableLambda` constructor and the convenience `@chain` decorator
# - Coercion of custom functions into runnables when used in chains
# - How to accept and use run metadata in your custom function
# - How to stream with custom functions by having them return generators
# 
# ## Using the constructor
# 
# Below, we explicitly wrap our custom logic using the `RunnableLambda` constructor:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain_openai')

import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()


# In[2]:


from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI


def length_function(text):
    return len(text)


def _multiple_length_function(text1, text2):
    return len(text1) * len(text2)


def multiple_length_function(_dict):
    return _multiple_length_function(_dict["text1"], _dict["text2"])


model = ChatOpenAI()

prompt = ChatPromptTemplate.from_template("what is {a} + {b}")

chain = (
    {
        "a": itemgetter("foo") | RunnableLambda(length_function),
        "b": {"text1": itemgetter("foo"), "text2": itemgetter("bar")}
        | RunnableLambda(multiple_length_function),
    }
    | prompt
    | model
)

chain.invoke({"foo": "bar", "bar": "gah"})


# ## The convenience `@chain` decorator
# 
# You can also turn an arbitrary function into a chain by adding a `@chain` decorator. This is functionally equivalent to wrapping the function in a `RunnableLambda` constructor as shown above. Here's an example:

# In[3]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain

prompt1 = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
prompt2 = ChatPromptTemplate.from_template("What is the subject of this joke: {joke}")


@chain
def custom_chain(text):
    prompt_val1 = prompt1.invoke({"topic": text})
    output1 = ChatOpenAI().invoke(prompt_val1)
    parsed_output1 = StrOutputParser().invoke(output1)
    chain2 = prompt2 | ChatOpenAI() | StrOutputParser()
    return chain2.invoke({"joke": parsed_output1})


custom_chain.invoke("bears")


# Above, the `@chain` decorator is used to convert `custom_chain` into a runnable, which we invoke with the `.invoke()` method.
# 
# If you are using a tracing with [LangSmith](https://docs.smith.langchain.com/), you should see a `custom_chain` trace in there, with the calls to OpenAI nested underneath.
# 
# ## Automatic coercion in chains
# 
# When using custom functions in chains with the pipe operator (`|`), you can omit the `RunnableLambda` or `@chain` constructor and rely on coercion. Here's a simple example with a function that takes the output from the model and returns the first five letters of it:

# In[4]:


prompt = ChatPromptTemplate.from_template("tell me a story about {topic}")

model = ChatOpenAI()

chain_with_coerced_function = prompt | model | (lambda x: x.content[:5])

chain_with_coerced_function.invoke({"topic": "bears"})


# Note that we didn't need to wrap the custom function `(lambda x: x.content[:5])` in a `RunnableLambda` constructor because the `model` on the left of the pipe operator is already a Runnable. The custom function is **coerced** into a runnable. See [this section](/docs/how_to/sequence/#coercion) for more information.
# 
# ## Passing run metadata
# 
# Runnable lambdas can optionally accept a [RunnableConfig](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.config.RunnableConfig.html#langchain_core.runnables.config.RunnableConfig) parameter, which they can use to pass callbacks, tags, and other configuration information to nested runs.

# In[5]:


import json

from langchain_core.runnables import RunnableConfig


def parse_or_fix(text: str, config: RunnableConfig):
    fixing_chain = (
        ChatPromptTemplate.from_template(
            "Fix the following text:\n\n```text\n{input}\n```\nError: {error}"
            " Don't narrate, just respond with the fixed data."
        )
        | model
        | StrOutputParser()
    )
    for _ in range(3):
        try:
            return json.loads(text)
        except Exception as e:
            text = fixing_chain.invoke({"input": text, "error": e}, config)
    return "Failed to parse"


from langchain_community.callbacks import get_openai_callback

with get_openai_callback() as cb:
    output = RunnableLambda(parse_or_fix).invoke(
        "{foo: bar}", {"tags": ["my-tag"], "callbacks": [cb]}
    )
    print(output)
    print(cb)


# In[6]:


from langchain_community.callbacks import get_openai_callback

with get_openai_callback() as cb:
    output = RunnableLambda(parse_or_fix).invoke(
        "{foo: bar}", {"tags": ["my-tag"], "callbacks": [cb]}
    )
    print(output)
    print(cb)


# ## Streaming
# 
# :::note
# [RunnableLambda](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableLambda.html) is best suited for code that does not need to support streaming. If you need to support streaming (i.e., be able to operate on chunks of inputs and yield chunks of outputs), use [RunnableGenerator](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableGenerator.html) instead as in the example below.
# :::
# 
# You can use generator functions (ie. functions that use the `yield` keyword, and behave like iterators) in a chain.
# 
# The signature of these generators should be `Iterator[Input] -> Iterator[Output]`. Or for async generators: `AsyncIterator[Input] -> AsyncIterator[Output]`.
# 
# These are useful for:
# - implementing a custom output parser
# - modifying the output of a previous step, while preserving streaming capabilities
# 
# Here's an example of a custom output parser for comma-separated lists. First, we create a chain that generates such a list as text:

# In[7]:


from typing import Iterator, List

prompt = ChatPromptTemplate.from_template(
    "Write a comma-separated list of 5 animals similar to: {animal}. Do not include numbers"
)

str_chain = prompt | model | StrOutputParser()

for chunk in str_chain.stream({"animal": "bear"}):
    print(chunk, end="", flush=True)


# Next, we define a custom function that will aggregate the currently streamed output and yield it when the model generates the next comma in the list:

# In[8]:


# This is a custom parser that splits an iterator of llm tokens
# into a list of strings separated by commas
def split_into_list(input: Iterator[str]) -> Iterator[List[str]]:
    # hold partial input until we get a comma
    buffer = ""
    for chunk in input:
        # add current chunk to buffer
        buffer += chunk
        # while there are commas in the buffer
        while "," in buffer:
            # split buffer on comma
            comma_index = buffer.index(",")
            # yield everything before the comma
            yield [buffer[:comma_index].strip()]
            # save the rest for the next iteration
            buffer = buffer[comma_index + 1 :]
    # yield the last chunk
    yield [buffer.strip()]


list_chain = str_chain | split_into_list

for chunk in list_chain.stream({"animal": "bear"}):
    print(chunk, flush=True)


# Invoking it gives a full array of values:

# In[9]:


list_chain.invoke({"animal": "bear"})


# ## Async version
# 
# If you are working in an `async` environment, here is an `async` version of the above example:

# In[10]:


from typing import AsyncIterator


async def asplit_into_list(
    input: AsyncIterator[str],
) -> AsyncIterator[List[str]]:  # async def
    buffer = ""
    async for (
        chunk
    ) in input:  # `input` is a `async_generator` object, so use `async for`
        buffer += chunk
        while "," in buffer:
            comma_index = buffer.index(",")
            yield [buffer[:comma_index].strip()]
            buffer = buffer[comma_index + 1 :]
    yield [buffer.strip()]


list_chain = str_chain | asplit_into_list

async for chunk in list_chain.astream({"animal": "bear"}):
    print(chunk, flush=True)


# In[11]:


await list_chain.ainvoke({"animal": "bear"})


# ## Next steps
# 
# Now you've learned a few different ways to use custom logic within your chains, and how to implement streaming.
# 
# To learn more, see the other how-to guides on runnables in this section.
