#!/usr/bin/env python
# coding: utf-8

# # NASA Toolkit
# 
# This notebook shows how to use agents to interact with the NASA toolkit. The toolkit provides access to the NASA Image and Video Library API, with potential to expand and include other accessible NASA APIs in future iterations.
# 
# **Note: NASA Image and Video Library search queries can result in large responses when the number of desired media results is not specified. Consider this prior to using the agent with LLM token credits.**

# ## Example Use:
# ---
# ### Initializing the agent

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# In[ ]:


from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.nasa.toolkit import NasaToolkit
from langchain_community.utilities.nasa import NasaAPIWrapper
from langchain_openai import OpenAI

llm = OpenAI(temperature=0, openai_api_key="")
nasa = NasaAPIWrapper()
toolkit = NasaToolkit.from_nasa_api_wrapper(nasa)
agent = initialize_agent(
    toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)


# ### Querying media assets

# In[ ]:


agent.run(
    "Can you find three pictures of the moon published between the years 2014 and 2020?"
)


# ### Querying details about media assets

# In[ ]:


output = agent.run(
    "I've just queried an image of the moon with the NASA id NHQ_2019_0311_Go Forward to the Moon."
    " Where can I find the metadata manifest for this asset?"
)

