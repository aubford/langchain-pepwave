#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: CDP
---
# # CDP Agentkit Toolkit
# 
# The `CDP Agentkit` toolkit contains tools that enable an LLM agent to interact with the [Coinbase Developer Platform](https://docs.cdp.coinbase.com/). The toolkit provides a wrapper around the CDP SDK, allowing agents to perform onchain operations like transfers, trades, and smart contract interactions.
# 
# ## Overview
# 
# ### Integration details
# 
# | Class | Package | Serializable | JS support |  Package latest |
# | :--- | :--- | :---: | :---: | :---: |
# | CdpToolkit | `cdp-langchain` | ❌ | ❌ |  ![PyPI - Version](https://img.shields.io/pypi/v/cdp-langchain?style=flat-square&label=%20) |
# 
# ### Tool features
# 
# The toolkit provides the following tools:
# 
# 1. **get_wallet_details** - Get details about the MPC Wallet
# 2. **get_balance** - Get balance for specific assets
# 3. **request_faucet_funds** - Request test tokens from faucet
# 4. **transfer** - Transfer assets between addresses
# 5. **trade** - Trade assets (Mainnet only)
# 6. **deploy_token** - Deploy ERC-20 token contracts
# 7. **mint_nft** - Mint NFTs from existing contracts
# 8. **deploy_nft** - Deploy new NFT contracts
# 9. **register_basename** - Register a basename for the wallet
# 
# We encourage you to add your own tools, both using CDP and web2 APIs, to create an agent that is tailored to your needs.
# 
# ## Setup
# 
# At a high-level, we will:
# 
# 1. Install the langchain package
# 2. Set up your CDP API credentials
# 3. Initialize the CDP wrapper and toolkit
# 4. Pass the tools to your agent with `toolkit.get_tools()`

# To enable automated tracing of individual tools, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# This toolkit lives in the `cdp-langchain` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU cdp-langchain')


# #### Set Environment Variables
# 
# To use this toolkit, you must first set the following environment variables to access the [CDP APIs](https://docs.cdp.coinbase.com/mpc-wallet/docs/quickstart) to create wallets and interact onchain. You can sign up for an API key for free on the [CDP Portal](https://cdp.coinbase.com/):

# In[ ]:


import getpass
import os

for env_var in [
    "CDP_API_KEY_NAME",
    "CDP_API_KEY_PRIVATE_KEY",
]:
    if not os.getenv(env_var):
        os.environ[env_var] = getpass.getpass(f"Enter your {env_var}: ")

# Optional: Set network (defaults to base-sepolia)
os.environ["NETWORK_ID"] = "base-sepolia"  # or "base-mainnet"


# ## Instantiation
# 
# Now we can instantiate our toolkit:

# In[ ]:


from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Initialize CDP wrapper
cdp = CdpAgentkitWrapper()

# Create toolkit from wrapper
toolkit = CdpToolkit.from_cdp_agentkit_wrapper(cdp)


# ## Tools
# 
# View [available tools](#tool-features):

# In[ ]:


tools = toolkit.get_tools()
for tool in tools:
    print(tool.name)


# ## Use within an agent
# 
# We will need a LLM or chat model:

# In[ ]:


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")


# Initialize the agent with the tools:

# In[ ]:


from langgraph.prebuilt import create_react_agent

tools = toolkit.get_tools()
agent_executor = create_react_agent(llm, tools)


# Example usage:

# In[ ]:


example_query = "Send 0.005 ETH to john2879.base.eth"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# Expected output:
# ```
# Transferred 0.005 of eth to john2879.base.eth.
# Transaction hash for the transfer: 0x78c7c2878659a0de216d0764fc87eff0d38b47f3315fa02ba493a83d8e782d1e
# Transaction link for the transfer: https://sepolia.basescan.org/tx/0x78c7c2878659a0de216d0764fc87eff0d38b47f3315fa02ba493a83d8e782d1
# ```

# ## CDP Toolkit Specific Features
# 
# ### Wallet Management
# 
# The toolkit maintains an MPC wallet. The wallet data can be exported and imported to persist between sessions:

# In[ ]:


# Export wallet data
wallet_data = cdp.export_wallet()

# Import wallet data
values = {"cdp_wallet_data": wallet_data}
cdp = CdpAgentkitWrapper(**values)


# ### Network Support
# 
# The toolkit supports [multiple networks](https://docs.cdp.coinbase.com/cdp-sdk/docs/networks)
# 
# ### Gasless Transactions
# 
# Some operations support gasless transactions on Base Mainnet:
# - USDC transfers
# - EURC transfers
# - cbBTC transfers

# ## API reference
# 
# For detailed documentation of all CDP features and configurations head to the [CDP docs](https://docs.cdp.coinbase.com/mpc-wallet/docs/welcome).
