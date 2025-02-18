#!/usr/bin/env python
# coding: utf-8

# # Etherscan
#
# >[Etherscan](https://docs.etherscan.io/)  is the leading blockchain explorer, search, API and analytics platform for Ethereum,
# a decentralized smart contracts platform.
#
#
# ## Overview
#
# The `Etherscan` loader use `Etherscan API` to load transactions histories under specific account on `Ethereum Mainnet`.
#
# You will need a `Etherscan api key` to proceed. The free api key has 5 calls per seconds quota.
#
# The loader supports the following six functionalities:
#
# * Retrieve normal transactions under specific account on Ethereum Mainet
# * Retrieve internal transactions under specific account on Ethereum Mainet
# * Retrieve erc20 transactions under specific account on Ethereum Mainet
# * Retrieve erc721 transactions under specific account on Ethereum Mainet
# * Retrieve erc1155 transactions under specific account on Ethereum Mainet
# * Retrieve ethereum balance in wei under specific account on Ethereum Mainet
#
#
# If the account does not have corresponding transactions, the loader will a list with one document. The content of document is ''.
#
# You can pass different filters to loader to access different functionalities we mentioned above:
#
# * "normal_transaction"
# * "internal_transaction"
# * "erc20_transaction"
# * "eth_balance"
# * "erc721_transaction"
# * "erc1155_transaction"
# The filter is default to normal_transaction
#
# If you have any questions, you can access [Etherscan API Doc](https://etherscan.io/tx/0x0ffa32c787b1398f44303f731cb06678e086e4f82ce07cebf75e99bb7c079c77) or contact me via i@inevitable.tech.
#
# All functions related to transactions histories are restricted 1000 histories maximum because of Etherscan limit. You can use the following parameters to find the transaction histories you need:
#
# * offset: default to 20. Shows 20 transactions for one time
# * page: default to 1. This controls pagination.
# * start_block: Default to 0. The transaction histories starts from 0 block.
# * end_block: Default to 99999999. The transaction histories starts from 99999999 block
# * sort: "desc" or "asc". Set default to "desc" to get latest transactions.

# ## Setup

# In[ ]:


get_ipython().run_line_magic("pip", "install --upgrade --quiet  langchain -q")


# In[ ]:


etherscanAPIKey = "..."


# In[1]:


import os

from langchain_community.document_loaders import EtherscanLoader


# In[6]:


os.environ["ETHERSCAN_API_KEY"] = etherscanAPIKey


# ## Create a ERC20 transaction loader

# In[9]:


account_address = "0x9dd134d14d1e65f84b706d6f205cd5b1cd03a46b"
loader = EtherscanLoader(account_address, filter="erc20_transaction")
result = loader.load()
eval(result[0].page_content)


# ## Create a normal transaction loader with customized parameters

# In[10]:


loader = EtherscanLoader(
    account_address,
    page=2,
    offset=20,
    start_block=10000,
    end_block=8888888888,
    sort="asc",
)
result = loader.load()
result
