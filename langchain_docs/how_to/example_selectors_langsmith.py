#!/usr/bin/env python
# coding: utf-8

# # How to select examples from a LangSmith dataset
# 
# import Prerequisites from "@theme/Prerequisites";
# import Compatibility from "@theme/Compatibility";
# 
# <Prerequisites titlesAndLinks={[
#   ["Chat models", "/docs/concepts/chat_models"],
#   ["Few-shot-prompting", "/docs/concepts/few-shot-prompting"],
#   ["LangSmith", "https://docs.smith.langchain.com/"],
# ]} />
# 
# 
# <Compatibility packagesAndVersions={[
#   ["langsmith", "0.1.101"],
#   ["langchain-core", "0.2.34"],
# ]} />
# 
# 
# [LangSmith](https://docs.smith.langchain.com/) datasets have built-in support for similarity search, making them a great tool for building and querying few-shot examples.
# 
# In this guide we'll see how to use an indexed LangSmith dataset as a few-shot example selector.
# 
# ## Setup
# 
# Before getting started make sure you've [created a LangSmith account](https://smith.langchain.com/) and set your credentials:

# In[2]:


import getpass
import os

if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Set LangSmith API key:\n\n")

os.environ["LANGSMITH_TRACING"] = "true"


# We'll need to install the `langsmith` SDK. In this example we'll also make use of `langchain`, `langchain-openai`, and `langchain-benchmarks`:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU "langsmith>=0.1.101" "langchain-core>=0.2.34" langchain langchain-openai langchain-benchmarks')


# Now we'll clone a public dataset and turn on indexing for the dataset. We can also turn on indexing via the [LangSmith UI](https://docs.smith.langchain.com/how_to_guides/datasets/index_datasets_for_dynamic_few_shot_example_selection).
# 
# We'll clone the [Multiverse math few shot example dataset](https://blog.langchain.dev/few-shot-prompting-to-improve-tool-calling-performance/).
# 
# This enables searching over the dataset and will make sure that anytime we update/add examples they are also indexed.

# In[ ]:


from langsmith import Client as LangSmith

ls_client = LangSmith()

dataset_name = "multiverse-math-few-shot-examples-v2"
dataset_public_url = (
    "https://smith.langchain.com/public/620596ee-570b-4d2b-8c8f-f828adbe5242/d"
)

ls_client.clone_public_dataset(dataset_public_url)

dataset_id = ls_client.read_dataset(dataset_name=dataset_name).id

ls_client.index_dataset(dataset_id=dataset_id)


# ## Querying dataset
# 
# Indexing can take a few seconds. Once the dataset is indexed, we can search for similar examples. Note that the input to the `similar_examples` method must have the same schema as the examples inputs. In this case our example inputs are a dictionary with a "question" key:

# In[12]:


examples = ls_client.similar_examples(
    {"question": "whats the negation of the negation of the negation of 3"},
    limit=3,
    dataset_id=dataset_id,
)
len(examples)


# In[13]:


examples[0].inputs["question"]


# For this dataset, the outputs are the conversation that followed the question in OpenAI message format:

# In[14]:


examples[0].outputs["conversation"]


# ## Creating dynamic few-shot prompts
# 
# The search returns the examples whose inputs are most similar to the query input. We can use this for few-shot prompting a model like so:

# In[20]:


from langchain.chat_models import init_chat_model
from langchain_benchmarks.tool_usage.tasks.multiverse_math import (
    add,
    cos,
    divide,
    log,
    multiply,
    negate,
    pi,
    power,
    sin,
    subtract,
)
from langchain_core.runnables import RunnableLambda
from langsmith import AsyncClient as AsyncLangSmith

async_ls_client = AsyncLangSmith()


def similar_examples(input_: dict) -> dict:
    examples = ls_client.similar_examples(input_, limit=5, dataset_id=dataset_id)
    return {**input_, "examples": examples}


async def asimilar_examples(input_: dict) -> dict:
    examples = await async_ls_client.similar_examples(
        input_, limit=5, dataset_id=dataset_id
    )
    return {**input_, "examples": examples}


def construct_prompt(input_: dict) -> list:
    instructions = """You are great at using mathematical tools."""
    examples = []
    for ex in input_["examples"]:
        examples.append({"role": "user", "content": ex.inputs["question"]})
        for msg in ex.outputs["conversation"]:
            if msg["role"] == "assistant":
                msg["name"] = "example_assistant"
            if msg["role"] == "user":
                msg["name"] = "example_user"
            examples.append(msg)
    return [
        {"role": "system", "content": instructions},
        *examples,
        {"role": "user", "content": input_["question"]},
    ]


tools = [add, cos, divide, log, multiply, negate, pi, power, sin, subtract]
llm = init_chat_model("gpt-4o-2024-08-06")
llm_with_tools = llm.bind_tools(tools)

example_selector = RunnableLambda(func=similar_examples, afunc=asimilar_examples)

chain = example_selector | construct_prompt | llm_with_tools


# In[21]:


ai_msg = await chain.ainvoke({"question": "whats the negation of the negation of 3"})
ai_msg.tool_calls


# Looking at the LangSmith trace, we can see that relevant examples were pulled in in the `similar_examples` step and passed as messages to ChatOpenAI: https://smith.langchain.com/public/9585e30f-765a-4ed9-b964-2211420cd2f8/r/fdea98d6-e90f-49d4-ac22-dfd012e9e0d9.
