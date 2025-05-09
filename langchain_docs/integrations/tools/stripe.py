#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Stripe
---
# # StripeAgentToolkit
# 
# This notebook provides a quick overview for getting started with Stripe's agent toolkit.
# 
# You can read more about `StripeAgentToolkit` in [Stripe's launch blog](https://stripe.dev/blog/adding-payments-to-your-agentic-workflows) or on the project's [PyPi page](https://pypi.org/project/stripe-agent-toolkit/).
# 
# ## Overview
# 
# ### Integration details
# 
# | Class | Package | Serializable | [JS Support](https://github.com/stripe/agent-toolkit?tab=readme-ov-file#typescript) |  Package latest |
# | :--- | :--- | :---: | :---: | :---: |
# | StripeAgentToolkit | [stripe-agent-toolkit](https://pypi.org/project/stripe-agent-toolkit) | ❌ | ✅ |  ![PyPI - Version](https://img.shields.io/pypi/v/stripe-agent-toolkit?style=flat-square&label=%20) |
# 
# 
# ## Setup
# 
# This externally-managed package is hosted out of the `stripe-agent-toolkit` project, which is managed by Stripe's team.
# 
# You can install it, along with langgraph for the following examples, with `pip`:

# In[1]:


get_ipython().run_line_magic('pip', 'install --quiet -U langgraph stripe-agent-toolkit')


# ### Credentials
# 
# In addition to installing the package, you will need to configure the integration with your Stripe account's secret key, which is available in your [Stripe Dashboard](https://dashboard.stripe.com/account/apikeys).

# In[ ]:


import getpass
import os

if not os.environ.get("STRIPE_SECRET_KEY"):
    os.environ["STRIPE_SECRET_KEY"] = getpass.getpass("STRIPE API key:\n")


# It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability:

# In[3]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ## Instantiation
# 
# Here we show how to create an instance of the Stripe Toolkit

# In[ ]:


from stripe_agent_toolkit.crewai.toolkit import StripeAgentToolkit

stripe_agent_toolkit = StripeAgentToolkit(
    secret_key=os.getenv("STRIPE_SECRET_KEY"),
    configuration={
        "actions": {
            "payment_links": {
                "create": True,
            },
        }
    },
)


# ## Agent
# 
# Here's how to use the toolkit to create a basic agent in langgraph:

# In[ ]:


from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
)

langgraph_agent_executor = create_react_agent(llm, stripe_agent_toolkit.get_tools())

input_state = {
    "messages": """
        Create a payment link for a new product called 'test' with a price
        of $100. Come up with a funny description about buy bots,
        maybe a haiku.
    """,
}

output_state = langgraph_agent_executor.invoke(input_state)

print(output_state["messages"][-1].content)

