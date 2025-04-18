#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: GOAT
---
# # GOAT
# 
# [GOAT](https://github.com/goat-sdk/goat) is the finance toolkit for AI agents.
# 
# ## Overview
# 
# Create agents that can:
# 
# - Send and receive payments
# - Purchase physical and digital goods and services
# - Engage in various investment strategies:
#   - Earn yield
#   - Bet on prediction markets
# - Purchase crypto assets
# - Tokenize any asset
# - Get financial insights
# 
# ### How it works
# GOAT leverages blockchains, cryptocurrencies (such as stablecoins), and wallets as the infrastructure to enable agents to become economic actors:
# 
# 1. Give your agent a [wallet](https://github.com/goat-sdk/goat/tree/main#chains-and-wallets)
# 2. Allow it to transact [anywhere](https://github.com/goat-sdk/goat/tree/main#chains-and-wallets)
# 3. Use more than [+200 tools](https://github.com/goat-sdk/goat/tree/main#tools)
# 
# See everything GOAT supports [here](https://github.com/goat-sdk/goat/tree/main#chains-and-wallets).
# 
# **Lightweight and extendable**
# Different from other toolkits, GOAT is designed to be lightweight and extendable by keeping its core minimal and allowing you to install only the tools you need.
# 
# If you don't find what you need on our more than 200 integrations you can easily:
# 
# - Create your own plugin
# - Integrate a new chain
# - Integrate a new wallet
# - Integrate a new agent framework
# 
# See how to do it [here](https://github.com/goat-sdk/goat/tree/main#-contributing).

# ### Quickstarts
# 
# The best way to get started is by using the quickstarts below. See how you can configure GOAT to achieve any of the use cases below.
# 
# - **By use case**
#   - **Money transmission**
#     - Send and receive payments [[EVM](https://github.com/goat-sdk/goat/tree/main/python/examples/by-use-case/evm-send-and-receive-tokens), [Solana](https://github.com/goat-sdk/goat/tree/main/python/examples/by-use-case/solana-send-and-receive-tokens)]
#   - **Investing**
#     - Generate yield [[Solana](https://github.com/goat-sdk/goat/tree/main/python/examples/by-use-case/solana-usdc-yield-deposit)]
#     - Purchase crypto assets [[EVM](https://github.com/goat-sdk/goat/tree/main/python/examples/by-use-case/evm-swap-tokens), [Solana](https://github.com/goat-sdk/goat/tree/main/python/examples/by-use-case/solana-swap-tokens)]
# - **By wallet**
#   - [Crossmint](https://github.com/goat-sdk/goat/tree/main/python/examples/by-wallet/crossmint)
# - **See all python quickstarts [here](https://github.com/goat-sdk/goat/tree/main/python/examples).**
# 

# ## Setup
# 
# 1. Install the core package and langchain adapter:
# 
# ```bash
# pip install goat-sdk goat-sdk-adapter-langchain
# ```
# 
# 2. Install the type of wallet you want to use (e.g solana):
# 
# ```bash
# pip install goat-sdk-wallet-solana
# ```
# 
# 3. Install the plugins you want to use in that chain:
# 
# ```bash
# pip install goat-sdk-plugin-spl-token
# ```
# 
# ## Instantiation
# 
# Now we can instantiate our toolkit:
# 
# ```python
# from goat_adapters.langchain import get_on_chain_tools
# from goat_wallets.solana import solana, send_solana
# from goat_plugins.spl_token import spl_token, SplTokenPluginOptions
# from goat_plugins.spl_token.tokens import SPL_TOKENS
# 
# # Initialize Solana client
# client = SolanaClient(os.getenv("SOLANA_RPC_ENDPOINT"))
# 
# # Initialize regular Solana wallet
# keypair = Keypair.from_base58_string(os.getenv("SOLANA_WALLET_SEED") or "")
# wallet = solana(client, keypair)
# 
# tools = get_on_chain_tools(
#         wallet=wallet,
#         plugins=[
#             send_solana(),
#             spl_token(SplTokenPluginOptions(
#                 network="mainnet",  # Using devnet as specified in .env
#                 tokens=SPL_TOKENS
#             )),
#         ],
#     )
# ```
# 
# ## Invocation
# ```python
# tools["get_balance"].invoke({ "address": "0x1234567890123456789012345678901234567890" })
# ```
# 
# ## Use within an agent
# 
# ```python
# import os
# import asyncio
# from dotenv import load_dotenv
# 
# # Load environment variables
# load_dotenv()
# 
# from solana.rpc.api import Client as SolanaClient
# from solders.keypair import Keypair
# 
# from goat_adapters.langchain import get_on_chain_tools
# from goat_wallets.solana import solana, send_solana
# from goat_plugins.spl_token import spl_token, SplTokenPluginOptions
# from goat_plugins.spl_token.tokens import SPL_TOKENS
# 
# # Initialize Solana client
# client = SolanaClient(os.getenv("SOLANA_RPC_ENDPOINT"))
# 
# # Initialize regular Solana wallet
# keypair = Keypair.from_base58_string(os.getenv("SOLANA_WALLET_SEED") or "")
# wallet = solana(client, keypair)
# 
# # Initialize LLM
# llm = ChatOpenAI(model="gpt-4o-mini")
# 
# def main():
#     # Initialize tools with Solana wallet
#     tools = get_on_chain_tools(
#         wallet=wallet,
#         plugins=[
#             send_solana(),
#             spl_token(SplTokenPluginOptions(
#                 network="mainnet",  # Using devnet as specified in .env
#                 tokens=SPL_TOKENS
#             )),
#         ],
#     )
# 
#     # Initialize agent
#     # Your agent code here
# 
# 
# if __name__ == "__main__":
#     main()
# ```
# 
# ## API reference
# 
# - For a complete list of tools, see the [GOAT SDK documentation](https://github.com/goat-sdk/goat).
# 
# 
