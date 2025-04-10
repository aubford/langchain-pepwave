#!/usr/bin/env python
# coding: utf-8

# # How to pass run time values to tools
# 
# import Prerequisites from "@theme/Prerequisites";
# import Compatibility from "@theme/Compatibility";
# 
# <Prerequisites titlesAndLinks={[
#   ["Chat models", "/docs/concepts/chat_models"],
#   ["LangChain Tools", "/docs/concepts/tools"],
#   ["How to create tools", "/docs/how_to/custom_tools"],
#   ["How to use a model to call tools", "/docs/how_to/tool_calling"],
# ]} />
# 
# 
# <Compatibility packagesAndVersions={[
#   ["langchain-core", "0.2.21"],
# ]} />
# 
# You may need to bind values to a [tool](/docs/concepts/tools/) that are only known at runtime. For example, the tool logic may require using the ID of the user who made the request.
# 
# Most of the time, such values should not be controlled by the LLM. In fact, allowing the LLM to control the user ID may lead to a security risk.
# 
# Instead, the LLM should only control the parameters of the tool that are meant to be controlled by the LLM, while other parameters (such as user ID) should be fixed by the application logic.
# 
# This how-to guide shows you how to prevent the model from generating certain tool arguments and injecting them in directly at runtime.
# 
# :::info Using with LangGraph
# 
# If you're using LangGraph, please refer to [this how-to guide](https://langchain-ai.github.io/langgraph/how-tos/pass-run-time-values-to-tools/)
# which shows how to create an agent that keeps track of a given user's favorite pets.
# :::

# We can bind them to chat models as follows:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs
#   customVarName="llm"
#   overrideParams={{fireworks: {model: "accounts/fireworks/models/firefunction-v1", kwargs: "temperature=0"}}}
# />
# 

# In[1]:


# | output: false
# | echo: false

import os
from getpass import getpass

from langchain_openai import ChatOpenAI

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ## Hiding arguments from the model
# 
# We can use the InjectedToolArg annotation to mark certain parameters of our Tool, like `user_id` as being injected at runtime, meaning they shouldn't be generated by the model

# In[2]:


from typing import List

from langchain_core.tools import InjectedToolArg, tool
from typing_extensions import Annotated

user_to_pets = {}


@tool(parse_docstring=True)
def update_favorite_pets(
    pets: List[str], user_id: Annotated[str, InjectedToolArg]
) -> None:
    """Add the list of favorite pets.

    Args:
        pets: List of favorite pets to set.
        user_id: User's ID.
    """
    user_to_pets[user_id] = pets


@tool(parse_docstring=True)
def delete_favorite_pets(user_id: Annotated[str, InjectedToolArg]) -> None:
    """Delete the list of favorite pets.

    Args:
        user_id: User's ID.
    """
    if user_id in user_to_pets:
        del user_to_pets[user_id]


@tool(parse_docstring=True)
def list_favorite_pets(user_id: Annotated[str, InjectedToolArg]) -> None:
    """List favorite pets if any.

    Args:
        user_id: User's ID.
    """
    return user_to_pets.get(user_id, [])


# If we look at the input schemas for these tools, we'll see that user_id is still listed:

# In[3]:


update_favorite_pets.get_input_schema().schema()


# But if we look at the tool call schema, which is what is passed to the model for tool-calling, user_id has been removed:

# In[4]:


update_favorite_pets.tool_call_schema.schema()


# So when we invoke our tool, we need to pass in user_id:

# In[5]:


user_id = "123"
update_favorite_pets.invoke({"pets": ["lizard", "dog"], "user_id": user_id})
print(user_to_pets)
print(list_favorite_pets.invoke({"user_id": user_id}))


# But when the model calls the tool, no user_id argument will be generated:

# In[6]:


tools = [
    update_favorite_pets,
    delete_favorite_pets,
    list_favorite_pets,
]
llm_with_tools = llm.bind_tools(tools)
ai_msg = llm_with_tools.invoke("my favorite animals are cats and parrots")
ai_msg.tool_calls


# ## Injecting arguments at runtime

# If we want to actually execute our tools using the model-generated tool call, we'll need to inject the user_id ourselves:

# In[7]:


from copy import deepcopy

from langchain_core.runnables import chain


@chain
def inject_user_id(ai_msg):
    tool_calls = []
    for tool_call in ai_msg.tool_calls:
        tool_call_copy = deepcopy(tool_call)
        tool_call_copy["args"]["user_id"] = user_id
        tool_calls.append(tool_call_copy)
    return tool_calls


inject_user_id.invoke(ai_msg)


# And now we can chain together our model, injection code, and the actual tools to create a tool-executing chain:

# In[8]:


tool_map = {tool.name: tool for tool in tools}


@chain
def tool_router(tool_call):
    return tool_map[tool_call["name"]]


chain = llm_with_tools | inject_user_id | tool_router.map()
chain.invoke("my favorite animals are cats and parrots")


# Looking at the user_to_pets dict, we can see that it's been updated to include cats and parrots:

# In[9]:


user_to_pets


# ## Other ways of annotating args
# 
# Here are a few other ways of annotating our tool args:

# In[10]:


from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class UpdateFavoritePetsSchema(BaseModel):
    """Update list of favorite pets"""

    pets: List[str] = Field(..., description="List of favorite pets to set.")
    user_id: Annotated[str, InjectedToolArg] = Field(..., description="User's ID.")


@tool(args_schema=UpdateFavoritePetsSchema)
def update_favorite_pets(pets, user_id):
    user_to_pets[user_id] = pets


update_favorite_pets.get_input_schema().schema()


# In[11]:


update_favorite_pets.tool_call_schema.schema()


# In[12]:


from typing import Optional, Type


class UpdateFavoritePets(BaseTool):
    name: str = "update_favorite_pets"
    description: str = "Update list of favorite pets"
    args_schema: Optional[Type[BaseModel]] = UpdateFavoritePetsSchema

    def _run(self, pets, user_id):
        user_to_pets[user_id] = pets


UpdateFavoritePets().get_input_schema().schema()


# In[13]:


UpdateFavoritePets().tool_call_schema.schema()


# In[14]:


class UpdateFavoritePets2(BaseTool):
    name: str = "update_favorite_pets"
    description: str = "Update list of favorite pets"

    def _run(self, pets: List[str], user_id: Annotated[str, InjectedToolArg]) -> None:
        user_to_pets[user_id] = pets


UpdateFavoritePets2().get_input_schema().schema()


# In[15]:


UpdateFavoritePets2().tool_call_schema.schema()

