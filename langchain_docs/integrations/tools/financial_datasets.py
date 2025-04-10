#!/usr/bin/env python
# coding: utf-8

# # FinancialDatasets Toolkit
# 
# The [financial datasets](https://financialdatasets.ai/) stock market API provides REST endpoints that let you get financial data for 16,000+ tickers spanning 30+ years.
# 
# ## Setup
# 
# To use this toolkit, you need two API keys:
# 
# `FINANCIAL_DATASETS_API_KEY`: Get it from [financialdatasets.ai](https://financialdatasets.ai/).
# `OPENAI_API_KEY`: Get it from [OpenAI](https://platform.openai.com/).

# In[ ]:


import getpass
import os

os.environ["FINANCIAL_DATASETS_API_KEY"] = getpass.getpass()


# In[ ]:


os.environ["OPENAI_API_KEY"] = getpass.getpass()


# ### Installation
# 
# This toolkit lives in the `langchain-community` package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# ## Instantiation
# 
# Now we can instantiate our toolkit:

# In[ ]:


from langchain_community.agent_toolkits.financial_datasets.toolkit import (
    FinancialDatasetsToolkit,
)
from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper

api_wrapper = FinancialDatasetsAPIWrapper(
    financial_datasets_api_key=os.environ["FINANCIAL_DATASETS_API_KEY"]
)
toolkit = FinancialDatasetsToolkit(api_wrapper=api_wrapper)


# ## Tools
# 
# View available tools:

# In[ ]:


tools = toolkit.get_tools()


# ## Use within an agent
# 
# Let's equip our agent with the FinancialDatasetsToolkit and ask financial questions.

# In[ ]:


system_prompt = """
You are an advanced financial analysis AI assistant equipped with specialized tools
to access and analyze financial data. Your primary function is to help users with
financial analysis by retrieving and interpreting income statements, balance sheets,
and cash flow statements for publicly traded companies.

You have access to the following tools from the FinancialDatasetsToolkit:

1. Balance Sheets: Retrieves balance sheet data for a given ticker symbol.
2. Income Statements: Fetches income statement data for a specified company.
3. Cash Flow Statements: Accesses cash flow statement information for a particular ticker.

Your capabilities include:

1. Retrieving financial statements for any publicly traded company using its ticker symbol.
2. Analyzing financial ratios and metrics based on the data from these statements.
3. Comparing financial performance across different time periods (e.g., year-over-year or quarter-over-quarter).
4. Identifying trends in a company's financial health and performance.
5. Providing insights on a company's liquidity, solvency, profitability, and efficiency.
6. Explaining complex financial concepts in simple terms.

When responding to queries:

1. Always specify which financial statement(s) you're using for your analysis.
2. Provide context for the numbers you're referencing (e.g., fiscal year, quarter).
3. Explain your reasoning and calculations clearly.
4. If you need more information to provide a complete answer, ask for clarification.
5. When appropriate, suggest additional analyses that might be helpful.

Remember, your goal is to provide accurate, insightful financial analysis to
help users make informed decisions. Always maintain a professional and objective tone in your responses.
"""


# Instantiate the LLM.

# In[ ]:


from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o")


# Define a user query.

# In[ ]:


query = "What was AAPL's revenue in 2023? What about it's total debt in Q1 2024?"


# Create the agent.

# In[ ]:


from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
        # Placeholders fill up a **list** of messages
        ("placeholder", "{agent_scratchpad}"),
    ]
)


agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)


# Query the agent.

# In[ ]:


agent_executor.invoke({"input": query})


# ## API reference
# 
# For detailed documentation of all `FinancialDatasetsToolkit` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.financial_datasets.toolkit.FinancialDatasetsToolkit.html).

# 
