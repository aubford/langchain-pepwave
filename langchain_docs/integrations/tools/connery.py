#!/usr/bin/env python
# coding: utf-8

# # Connery Toolkit and Tools
# 
# Using the Connery toolkit and tools, you can integrate Connery Actions into your LangChain agent.
# 
# ## What is Connery?
# 
# Connery is an open-source plugin infrastructure for AI.
# 
# With Connery, you can easily create a custom plugin with a set of actions and seamlessly integrate them into your LangChain agent.
# Connery will take care of critical aspects such as runtime, authorization, secret management, access management, audit logs, and other vital features.
# 
# Furthermore, Connery, supported by our community, provides a diverse collection of ready-to-use open-source plugins for added convenience.
# 
# Learn more about Connery:
# 
# - GitHub: https://github.com/connery-io/connery
# - Documentation: https://docs.connery.io
# 
# ## Setup
# 
# ### Installation
# 
# You need to install the `langchain_community` package to use the Connery tools.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# ### Credentials
# 
# To use Connery Actions in your LangChain agent, you need to do some preparation:
# 
# 1. Set up the Connery runner using the [Quickstart](https://docs.connery.io/docs/runner/quick-start/) guide.
# 2. Install all the plugins with the actions you want to use in your agent.
# 3. Set environment variables `CONNERY_RUNNER_URL` and `CONNERY_RUNNER_API_KEY` so the toolkit can communicate with the Connery Runner.

# In[ ]:


import getpass
import os

for key in ["CONNERY_RUNNER_URL", "CONNERY_RUNNER_API_KEY"]:
    if key not in os.environ:
        os.environ[key] = getpass.getpass(f"Please enter the value for {key}: ")


# ## Toolkit
# 
# In the example below, we create an agent that uses two Connery Actions to summarize a public webpage and send the summary by email:
# 
# 1. **Summarize public webpage** action from the [Summarization](https://github.com/connery-io/summarization-plugin) plugin.
# 2. **Send email** action from the [Gmail](https://github.com/connery-io/gmail) plugin.
# 
# You can see a LangSmith trace of this example [here](https://smith.langchain.com/public/4af5385a-afe9-46f6-8a53-57fe2d63c5bc/r).

# In[1]:


import os

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.connery import ConneryToolkit
from langchain_community.tools.connery import ConneryService
from langchain_openai import ChatOpenAI

# Specify your Connery Runner credentials.
os.environ["CONNERY_RUNNER_URL"] = ""
os.environ["CONNERY_RUNNER_API_KEY"] = ""

# Specify OpenAI API key.
os.environ["OPENAI_API_KEY"] = ""

# Specify your email address to receive the email with the summary from example below.
recepient_email = "test@example.com"

# Create a Connery Toolkit with all the available actions from the Connery Runner.
connery_service = ConneryService()
connery_toolkit = ConneryToolkit.create_instance(connery_service)

# Use OpenAI Functions agent to execute the prompt using actions from the Connery Toolkit.
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    connery_toolkit.get_tools(), llm, AgentType.OPENAI_FUNCTIONS, verbose=True
)
result = agent.run(
    f"""Make a short summary of the webpage http://www.paulgraham.com/vb.html in three sentences
and send it to {recepient_email}. Include the link to the webpage into the body of the email."""
)
print(result)


# NOTE: Connery Action is a structured tool, so you can only use it in the agents supporting structured tools.
# 
# ## Tool

# In[ ]:


import os

from langchain.agents import AgentType, initialize_agent
from langchain_community.tools.connery import ConneryService
from langchain_openai import ChatOpenAI

# Specify your Connery Runner credentials.
os.environ["CONNERY_RUNNER_URL"] = ""
os.environ["CONNERY_RUNNER_API_KEY"] = ""

# Specify OpenAI API key.
os.environ["OPENAI_API_KEY"] = ""

# Specify your email address to receive the emails from examples below.
recepient_email = "test@example.com"

# Get the SendEmail action from the Connery Runner by ID.
connery_service = ConneryService()
send_email_action = connery_service.get_action("CABC80BB79C15067CA983495324AE709")


# Run the action manually.

# In[ ]:


manual_run_result = send_email_action.run(
    {
        "recipient": recepient_email,
        "subject": "Test email",
        "body": "This is a test email sent from Connery.",
    }
)
print(manual_run_result)


# Run the action using the OpenAI Functions agent.
# 
# You can see a LangSmith trace of this example [here](https://smith.langchain.com/public/a37d216f-c121-46da-a428-0e09dc19b1dc/r).

# In[ ]:


llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    [send_email_action], llm, AgentType.OPENAI_FUNCTIONS, verbose=True
)
agent_run_result = agent.run(
    f"Send an email to the {recepient_email} and say that I will be late for the meeting."
)
print(agent_run_result)


# NOTE: Connery Action is a structured tool, so you can only use it in the agents supporting structured tools.

# ## API reference
# 
# For detailed documentation of all Connery features and configurations head to the API reference:
# 
# - Toolkit: https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.connery.toolkit.ConneryToolkit.html
# - Tool: https://python.langchain.com/api_reference/community/tools/langchain_community.tools.connery.service.ConneryService.html
