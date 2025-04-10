#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: OpenGradient
---
# # OpenGradientToolkit
# 
# This notebook shows how to build tools using the OpenGradient toolkit. This toolkit gives users the ability to create custom tools based on models and workflows on the [OpenGradient network](https://www.opengradient.ai/).
# 
# ## Setup
# 
# Ensure that you have an OpenGradient API key in order to access the OpenGradient network. If you already have an API key, simply set the environment variable:

# In[ ]:


get_ipython().system('export OPENGRADIENT_PRIVATE_KEY="your-api-key"')


# If you need to set up a new API key, download the opengradient SDK and follow the instructions to initialize a new configuration.

# In[ ]:


get_ipython().system('pip install opengradient')
get_ipython().system('opengradient config init')


# ### Installation
# 
# This toolkit lives in the `langchain-opengradient` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-opengradient')


# ## Instantiation
# 
# Now we can instantiate our toolkit with the API key from before.

# In[ ]:


from langchain_opengradient import OpenGradientToolkit

toolkit = OpenGradientToolkit(
    # Not required if you have already set the environment variable OPENGRADIENT_PRIVATE_KEY
    private_key="your-api-key"
)


# ## Build your own tools
# The OpenGradientToolkit offers two main methods for creating custom tools:
# 
# ### 1. Create a tool to run ML models
# You can create tools that leverage ML models deployed on the [OpenGradient model hub](https://hub.opengradient.ai/). User-created models can be uploaded, inferenced, and shared to the model hub through the [OpenGradient SDK](https://docs.opengradient.ai/developers/sdk/model_management.html).
# 

# In[ ]:


import opengradient as og
from pydantic import BaseModel, Field


# Example 1: Simple tool with no input schema
def price_data_provider():
    """Function that provides input data to the model."""
    return {
        "open_high_low_close": [
            [2535.79, 2535.79, 2505.37, 2515.36],
            [2515.37, 2516.37, 2497.27, 2506.94],
            [2506.94, 2515, 2506.35, 2508.77],
            [2508.77, 2519, 2507.55, 2518.79],
            [2518.79, 2522.1, 2513.79, 2517.92],
            [2517.92, 2521.4, 2514.65, 2518.13],
            [2518.13, 2525.4, 2517.2, 2522.6],
            [2522.59, 2528.81, 2519.49, 2526.12],
            [2526.12, 2530, 2524.11, 2529.99],
            [2529.99, 2530.66, 2525.29, 2526],
        ]
    }


def format_volatility(inference_result):
    """Function that formats the model output."""
    return format(float(inference_result.model_output["Y"].item()), ".3%")


# Create the tool
volatility_tool = toolkit.create_run_model_tool(
    model_cid="QmRhcpDXfYCKsimTmJYrAVM4Bbvck59Zb2onj3MHv9Kw5N",
    tool_name="eth_volatility",
    model_input_provider=price_data_provider,
    model_output_formatter=format_volatility,
    tool_description="Generates volatility measurement for ETH/USDT trading pair",
    inference_mode=og.InferenceMode.VANILLA,
)


# Example 2: Tool with input schema from the agent
class TokenInputSchema(BaseModel):
    token: str = Field(description="Token name (ethereum or bitcoin)")


def token_data_provider(**inputs):
    """Dynamic function that changes behavior based on agent input."""
    token = inputs.get("token")
    if token == "bitcoin":
        return {"price_series": [100001.1, 100013.2, 100149.2, 99998.1]}
    else:  # ethereum
        return {"price_series": [2010.1, 2012.3, 2020.1, 2019.2]}


# Create the tool with schema
token_tool = toolkit.create_run_model_tool(
    model_cid="QmZdSfHWGJyzBiB2K98egzu3MypPcv4R1ASypUxwZ1MFUG",
    tool_name="token_volatility",
    model_input_provider=token_data_provider,
    model_output_formatter=lambda x: format(float(x.model_output["std"].item()), ".3%"),
    tool_input_schema=TokenInputSchema,
    tool_description="Measures return volatility for a specified token",
)

# Add tools to the toolkit
toolkit.add_tool(volatility_tool)
toolkit.add_tool(token_tool)


# ### 2. Create a tool to read workflow results
# 
# Read workflows are scheduled inferences that regularly run models stored on smart-contracts with live oracle data. More information on these can be [found here](https://docs.opengradient.ai/developers/sdk/ml_workflows.html).
# 
# You can create tools that read results from workflow smart contracts:

# In[ ]:


# Create a tool to read from a workflow
forecast_tool = toolkit.create_read_workflow_tool(
    workflow_contract_address="0x58826c6dc9A608238d9d57a65bDd50EcaE27FE99",
    tool_name="ETH_Price_Forecast",
    tool_description="Reads latest forecast for ETH price from deployed workflow",
    output_formatter=lambda x: f"Price change forecast: {format(float(x.numbers['regression_output'].item()), '.2%')}",
)

# Add the tool to the toolkit
toolkit.add_tool(forecast_tool)


# ## Tools
# 
# Use the built in `get_tools()` method to view a list of the available tools within the OpenGradient toolkit.

# In[ ]:


tools = toolkit.get_tools()

# View tools
for tool in tools:
    print(tool)


# ## Use within an agent
# Here's how to use your OpenGradient tools with a LangChain agent:

# In[ ]:


from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o")

# Create tools from the toolkit
tools = toolkit.get_tools()

# Create agent
agent_executor = create_react_agent(llm, tools)

# Example query for the agent
example_query = "What's the current volatility of ETH?"

# Execute the agent
events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# Here's a sample output of everything put together:
# 
# ```
# ================================ Human Message =================================
# 
# What's the current volatility of ETH?
# ================================== Ai Message ==================================
# Tool Calls:
#   eth_volatility (chatcmpl-tool-d66ab9ee8f2c40e5a2634d90c7aeb17d)
#  Call ID: chatcmpl-tool-d66ab9ee8f2c40e5a2634d90c7aeb17d
#   Args:
# ================================= Tool Message =================================
# Name: eth_volatility
# 
# 0.038%
# ================================== Ai Message ==================================
# 
# The current volatility of the ETH/USDT trading pair is 0.038%.
# ```

# ## API reference
# 
# See the [Github page](https://github.com/OpenGradient/og-langchain) for more detail.
