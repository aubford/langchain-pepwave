#!/usr/bin/env python
# coding: utf-8

# # Memorize
# 
# Fine-tuning LLM itself to memorize information using unsupervised learning.
# 
# This tool requires LLMs that support fine-tuning. Currently, only `langchain.llms import GradientLLM` is supported.

# ## Imports

# In[16]:


import os

from langchain.agents import AgentExecutor, AgentType, initialize_agent, load_tools
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import GradientLLM


# ## Set the Environment API Key
# Make sure to get your API key from Gradient AI. You are given $10 in free credits to test and fine-tune different models.

# In[17]:


from getpass import getpass

if not os.environ.get("GRADIENT_ACCESS_TOKEN", None):
    # Access token under https://auth.gradient.ai/select-workspace
    os.environ["GRADIENT_ACCESS_TOKEN"] = getpass("gradient.ai access token:")
if not os.environ.get("GRADIENT_WORKSPACE_ID", None):
    # `ID` listed in `$ gradient workspace list`
    # also displayed after login at at https://auth.gradient.ai/select-workspace
    os.environ["GRADIENT_WORKSPACE_ID"] = getpass("gradient.ai workspace id:")
if not os.environ.get("GRADIENT_MODEL_ADAPTER_ID", None):
    # `ID` listed in `$ gradient model list --workspace-id "$GRADIENT_WORKSPACE_ID"`
    os.environ["GRADIENT_MODEL_ID"] = getpass("gradient.ai model id:")


# Optional: Validate your Environment variables ```GRADIENT_ACCESS_TOKEN``` and ```GRADIENT_WORKSPACE_ID``` to get currently deployed models.

# ## Create the `GradientLLM` instance
# You can specify different parameters such as the model name, max tokens generated, temperature, etc.

# In[18]:


llm = GradientLLM(
    model_id=os.environ["GRADIENT_MODEL_ID"],
    # # optional: set new credentials, they default to environment variables
    # gradient_workspace_id=os.environ["GRADIENT_WORKSPACE_ID"],
    # gradient_access_token=os.environ["GRADIENT_ACCESS_TOKEN"],
)


# ## Load tools

# In[19]:


tools = load_tools(["memorize"], llm=llm)


# ## Initiate the Agent

# In[20]:


agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    # memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
)


# ## Run the agent
# Ask the agent to memorize a piece of text.

# In[21]:


agent.run(
    "Please remember the fact in detail:\nWith astonishing dexterity, Zara Tubikova set a world record by solving a 4x4 Rubik's Cube variation blindfolded in under 20 seconds, employing only their feet."
)

