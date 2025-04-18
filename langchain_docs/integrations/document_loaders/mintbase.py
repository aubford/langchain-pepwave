#!/usr/bin/env python
# coding: utf-8

# # Near Blockchain

# ## Overview

# The intention of this notebook is to provide a means of testing functionality in the Langchain Document Loader for Near Blockchain.
# 
# Initially this Loader supports:
# 
# *   Loading NFTs as Documents from NFT Smart Contracts (NEP-171 and NEP-177)
# *   Near Mainnnet, Near Testnet (default is mainnet)
# *   Mintbase's Graph API
# 
# It can be extended if the community finds value in this loader.  Specifically:
# 
# *   Additional APIs can be added (e.g. Tranction-related APIs)
# 
# This Document Loader Requires:
# 
# *   A free [Mintbase API Key](https://docs.mintbase.xyz/dev/mintbase-graph/)
# 
# The output takes the following format:
# 
# - pageContent= Individual NFT
# - metadata=\{'source': 'nft.yearofchef.near', 'blockchain': 'mainnet', 'tokenId': '1846'\}

# ## Load NFTs into Document Loader

# In[ ]:


# get MINTBASE_API_KEY from https://docs.mintbase.xyz/dev/mintbase-graph/

mintbaseApiKey = "..."


# ### Option 1: Ethereum Mainnet (default BlockchainType)

# In[ ]:


from MintbaseLoader import MintbaseDocumentLoader

contractAddress = "nft.yearofchef.near"  # Year of chef contract address


blockchainLoader = MintbaseDocumentLoader(
    contract_address=contractAddress, blockchain_type="mainnet", api_key="omni-site"
)

nfts = blockchainLoader.load()

print(nfts[:1])

for doc in blockchainLoader.lazy_load():
    print()
    print(type(doc))
    print(doc)

