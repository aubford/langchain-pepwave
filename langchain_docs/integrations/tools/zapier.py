#!/usr/bin/env python
# coding: utf-8

# # Zapier Natural Language Actions
# 
# **Deprecated** This API will be sunset on 2023-11-17: https://nla.zapier.com/start/
#  
# >[Zapier Natural Language Actions](https://nla.zapier.com/start/) gives you access to the 5k+ apps, 20k+ actions on Zapier's platform through a natural language API interface.
# >
# >NLA supports apps like `Gmail`, `Salesforce`, `Trello`, `Slack`, `Asana`, `HubSpot`, `Google Sheets`, `Microsoft Teams`, and thousands more apps: https://zapier.com/apps
# >`Zapier NLA` handles ALL the underlying API auth and translation from natural language --> underlying API call --> return simplified output for LLMs. The key idea is you, or your users, expose a set of actions via an oauth-like setup window, which you can then query and execute via a REST API.
# 
# NLA offers both API Key and OAuth for signing NLA API requests.
# 
# 1. Server-side (API Key): for quickly getting started, testing, and production scenarios where LangChain will only use actions exposed in the developer's Zapier account (and will use the developer's connected accounts on Zapier.com)
# 
# 2. User-facing (Oauth): for production scenarios where you are deploying an end-user facing application and LangChain needs access to end-user's exposed actions and connected accounts on Zapier.com
# 
# This quick start focus mostly on the server-side use case for brevity. Jump to [Example Using OAuth Access Token](#oauth) to see a short example how to set up Zapier for user-facing situations. Review [full docs](https://nla.zapier.com/start/) for full user-facing oauth developer support.
# 
# This example goes over how to use the Zapier integration with a `SimpleSequentialChain`, then an `Agent`.
# In code, below:

# In[2]:


import os

# get from https://platform.openai.com/
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")

# get from https://nla.zapier.com/docs/authentication/ after logging in):
os.environ["ZAPIER_NLA_API_KEY"] = os.environ.get("ZAPIER_NLA_API_KEY", "")


# ## Example with Agent
# Zapier tools can be used with an agent. See the example below.

# In[3]:


from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits import ZapierToolkit
from langchain_community.utilities.zapier import ZapierNLAWrapper
from langchain_openai import OpenAI


# In[4]:


## step 0. expose gmail 'find email' and slack 'send channel message' actions

# first go here, log in, expose (enable) the two actions: https://nla.zapier.com/demo/start -- for this example, can leave all fields "Have AI guess"
# in an oauth scenario, you'd get your own <provider> id (instead of 'demo') which you route your users through first


# In[5]:


llm = OpenAI(temperature=0)
zapier = ZapierNLAWrapper()
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
agent = initialize_agent(
    toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)


# In[6]:


agent.run(
    "Summarize the last email I received regarding Silicon Valley Bank. Send the summary to the #test-zapier channel in slack."
)


# ## Example with SimpleSequentialChain
# If you need more explicit control, use a chain, like below.

# In[7]:


from langchain.chains import LLMChain, SimpleSequentialChain, TransformChain
from langchain_community.tools.zapier.tool import ZapierNLARunAction
from langchain_community.utilities.zapier import ZapierNLAWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI


# In[8]:


## step 0. expose gmail 'find email' and slack 'send direct message' actions

# first go here, log in, expose (enable) the two actions: https://nla.zapier.com/demo/start -- for this example, can leave all fields "Have AI guess"
# in an oauth scenario, you'd get your own <provider> id (instead of 'demo') which you route your users through first

actions = ZapierNLAWrapper().list()


# In[9]:


## step 1. gmail find email

GMAIL_SEARCH_INSTRUCTIONS = "Grab the latest email from Silicon Valley Bank"


def nla_gmail(inputs):
    action = next(
        (a for a in actions if a["description"].startswith("Gmail: Find Email")), None
    )
    return {
        "email_data": ZapierNLARunAction(
            action_id=action["id"],
            zapier_description=action["description"],
            params_schema=action["params"],
        ).run(inputs["instructions"])
    }


gmail_chain = TransformChain(
    input_variables=["instructions"],
    output_variables=["email_data"],
    transform=nla_gmail,
)


# In[10]:


## step 2. generate draft reply

template = """You are an assisstant who drafts replies to an incoming email. Output draft reply in plain text (not JSON).

Incoming email:
{email_data}

Draft email reply:"""

prompt_template = PromptTemplate(input_variables=["email_data"], template=template)
reply_chain = LLMChain(llm=OpenAI(temperature=0.7), prompt=prompt_template)


# In[11]:


## step 3. send draft reply via a slack direct message

SLACK_HANDLE = "@Ankush Gola"


def nla_slack(inputs):
    action = next(
        (
            a
            for a in actions
            if a["description"].startswith("Slack: Send Direct Message")
        ),
        None,
    )
    instructions = f'Send this to {SLACK_HANDLE} in Slack: {inputs["draft_reply"]}'
    return {
        "slack_data": ZapierNLARunAction(
            action_id=action["id"],
            zapier_description=action["description"],
            params_schema=action["params"],
        ).run(instructions)
    }


slack_chain = TransformChain(
    input_variables=["draft_reply"],
    output_variables=["slack_data"],
    transform=nla_slack,
)


# In[12]:


## finally, execute

overall_chain = SimpleSequentialChain(
    chains=[gmail_chain, reply_chain, slack_chain], verbose=True
)
overall_chain.run(GMAIL_SEARCH_INSTRUCTIONS)


# ## Example Using OAuth Access Token{#oauth}
# The below snippet shows how to initialize the wrapper with a procured OAuth access token. Note the argument being passed in as opposed to setting an environment variable. Review the [authentication docs](https://nla.zapier.com/docs/authentication/#oauth-credentials) for full user-facing oauth developer support.
# 
# The developer is tasked with handling the OAuth handshaking to procure and refresh the access token.

# In[ ]:


llm = OpenAI(temperature=0)
zapier = ZapierNLAWrapper(zapier_nla_oauth_access_token="<fill in access token here>")
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
agent = initialize_agent(
    toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run(
    "Summarize the last email I received regarding Silicon Valley Bank. Send the summary to the #test-zapier channel in slack."
)

