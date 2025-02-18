#!/usr/bin/env python
# coding: utf-8

# # Migrating from LLMRouterChain
#
# The [`LLMRouterChain`](https://python.langchain.com/api_reference/langchain/chains/langchain.chains.router.llm_router.LLMRouterChain.html) routed an input query to one of multiple destinations-- that is, given an input query, it used a LLM to select from a list of destination chains, and passed its inputs to the selected chain.
#
# `LLMRouterChain` does not support common [chat model](/docs/concepts/chat_models) features, such as message roles and [tool calling](/docs/concepts/tool_calling). Under the hood, `LLMRouterChain` routes a query by instructing the LLM to generate JSON-formatted text, and parsing out the intended destination.
#
# Consider an example from a [MultiPromptChain](/docs/versions/migrating_chains/multi_prompt_chain), which uses `LLMRouterChain`. Below is an (example) default prompt:

# In[1]:


from langchain.chains.router.multi_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

destinations = """
animals: prompt for animal expert
vegetables: prompt for a vegetable expert
"""

router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations)

print(router_template.replace("`", "'"))  # for rendering purposes


# Most of the behavior is determined via a single natural language prompt. Chat models that support [tool calling](/docs/how_to/tool_calling/) features confer a number of advantages for this task:
#
# - Supports chat prompt templates, including messages with `system` and other roles;
# - Tool-calling models are fine-tuned to generate structured output;
# - Support for runnable methods like streaming and async operations.
#
# Now let's look at `LLMRouterChain` side-by-side with an LCEL implementation that uses tool-calling. Note that for this guide we will `langchain-openai >= 0.1.20`:

# In[ ]:


get_ipython().run_line_magic("pip", "install -qU langchain-core langchain-openai")


# In[ ]:


import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()


# ## Legacy
#
# <details open>

# In[2]:


from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

router_prompt = PromptTemplate(
    # Note: here we use the prompt template from above. Generally this would need
    # to be customized.
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)

chain = LLMRouterChain.from_llm(llm, router_prompt)


# In[3]:


result = chain.invoke({"input": "What color are carrots?"})

print(result["destination"])


# </details>
#
# ## LCEL
#
# <details open>

# In[4]:


from operator import itemgetter
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

llm = ChatOpenAI(model="gpt-4o-mini")

route_system = "Route the user's query to either the animal or vegetable expert."
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", route_system),
        ("human", "{input}"),
    ]
)


# Define schema for output:
class RouteQuery(TypedDict):
    """Route query to destination expert."""

    destination: Literal["animal", "vegetable"]


# Instead of writing formatting instructions into the prompt, we
# leverage .with_structured_output to coerce the output into a simple
# schema.
chain = route_prompt | llm.with_structured_output(RouteQuery)


# In[5]:


result = chain.invoke({"input": "What color are carrots?"})

print(result["destination"])


# </details>
#
# ## Next steps
#
# See [this tutorial](/docs/tutorials/llm_chain) for more detail on building with prompt templates, LLMs, and output parsers.
#
# Check out the [LCEL conceptual docs](/docs/concepts/lcel) for more background information.

# In[ ]:
