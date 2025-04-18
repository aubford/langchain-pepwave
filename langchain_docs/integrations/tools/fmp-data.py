#!/usr/bin/env python
# coding: utf-8

# # FMP Data
# 
# Access financial market data through natural language queries.
# 
# ## Overview
# 
# The FMP (Financial Modeling Prep) LangChain integration provides a seamless way to access financial market data through natural language queries. This integration offers two main components:
# 
# - `FMPDataToolkit`: Creates collections of tools based on natural language queries
# - `FMPDataTool`: A single unified tool that automatically selects and uses the appropriate endpoints
# 
# The integration leverages LangChain's semantic search capabilities to match user queries with the most relevant FMP API endpoints, making financial data access more intuitive and efficient.
# ## Setup

# In[ ]:


get_ipython().system('pip install -U langchain-fmp-data')


# In[ ]:


import os

# Replace with your actual API keys
os.environ["FMP_API_KEY"] = "your-fmp-api-key"  # pragma: allowlist secret
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"  # pragma: allowlist secret


# It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ## Instantiation
# There are two main ways to instantiate the FMP LangChain integration:
# 1. Using FMPDataToolkit

# In[ ]:


from langchain_fmp_data import FMPDataToolkit

query = "Get stock market prices and technical indicators"
# Basic instantiation
toolkit = FMPDataToolkit(query=query)

# Instantiation with specific query focus
market_toolkit = FMPDataToolkit(
    query=query,
    num_results=5,
)

# Instantiation with custom configuration
custom_toolkit = FMPDataToolkit(
    query="Financial analysis",
    num_results=3,
    similarity_threshold=0.4,
    cache_dir="/custom/cache/path",
)


# 2. Using FMPDataTool

# In[ ]:


from langchain_fmp_data import FMPDataTool
from langchain_fmp_data.tools import ResponseFormat

# Basic instantiation
tool = FMPDataTool()

# Advanced instantiation with custom settings
advanced_tool = FMPDataTool(
    max_iterations=50,
    temperature=0.2,
)


# ## Invocation
# The tools can be invoked in several ways:
# 
# ### Direct Invocation

# In[ ]:


# Using FMPDataTool
tool_direct = FMPDataTool()

# Basic query
# fmt: off
result = tool.invoke({"query": "What's Apple's current stock price?"})
# fmt: on

# Advanced query with specific format
# fmt: off
detailed_result = tool_direct.invoke(
    {
        "query": "Compare Tesla and Ford's profit margins",
        "response_format": ResponseFormat.BOTH,
    }
)
# fmt: on


# ### Using with LangChain Agents

# In[ ]:


from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

# Setup
llm = ChatOpenAI(temperature=0)
toolkit = FMPDataToolkit(
    query="Stock analysis",
    num_results=3,
)
tools = toolkit.get_tools()

# Create agent
prompt = "You are a helpful assistant. Answer the user's questions based on the provided context."
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
)

# Run query
# fmt: off
response = agent_executor.invoke({"input": "What's the PE ratio of Microsoft?"})
# fmt: on


# ## Advanced Usage
# You can customize the tool's behavior:
# 
# 

# In[ ]:


# Initialize with custom settings
advanced_tool = FMPDataTool(
    max_iterations=50,  # Increase max iterations for complex queries
    temperature=0.2,  # Adjust temperature for more/less focused responses
)

# Example of a complex multi-part analysis
query = """
Analyze Apple's financial health by:
1. Examining current ratios and debt levels
2. Comparing profit margins to industry average
3. Looking at cash flow trends
4. Assessing growth metrics
"""
# fmt: off
response = advanced_tool.invoke(
    {
        "query": query,
        "response_format": ResponseFormat.BOTH}
)
# fmt: on
print("Detailed Financial Analysis:")
print(response)


# ## Chaining
# You can chain the tool similar to other tools simply by creating a chain with desired model.

# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Setup
llm = ChatOpenAI(temperature=0)
toolkit = FMPDataToolkit(query="Stock analysis", num_results=3)
tools = toolkit.get_tools()

llm_with_tools = llm.bind(functions=tools)
output_parser = StrOutputParser()
# Create chain
runner = llm_with_tools | output_parser

# Run chain
# fmt: off
response = runner.invoke(
    {
        "input": "What's the PE ratio of Microsoft?"
    }
)
# fmt: on


# ## API reference
# 
# ### FMPDataToolkit
# Main class for creating collections of FMP API tools:

# In[ ]:


from typing import Any

from langchain.tools import Tool


class FMPDataToolkit:
    """Creates a collection of FMP data tools based on queries."""

    def __init__(
        self,
        query: str | None = None,
        num_results: int = 3,
        similarity_threshold: float = 0.3,
        cache_dir: str | None = None,
    ): ...

    def get_tools(self) -> list[Tool]:
        """Returns a list of relevant FMP API tools based on the query."""
        ...


# ### FMPDataTool
# Unified tool that automatically selects appropriate FMP endpoints:

# In[ ]:


# fmt: off
class FMPDataTool:
    """Single unified tool for accessing FMP data through natural language."""

    def __init__(
            self,
            max_iterations: int = 3,
            temperature: float = 0.0,
    ): ...

    def invoke(
            self,
            input: dict[str, Any],
    ) -> str | dict[str, Any]:
        """Execute a natural language query against FMP API."""
        ...

# fmt: on


# ### ResponseFormat
# Enum for controlling response format:

# In[ ]:


from enum import Enum


class ResponseFormat(str, Enum):
    RAW = "raw"  # Raw API response
    ANALYSIS = "text"  # Natural language analysis
    BOTH = "both"  # Both raw data and analysis

