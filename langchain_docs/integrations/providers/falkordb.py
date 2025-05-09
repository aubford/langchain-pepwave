#!/usr/bin/env python
# coding: utf-8

# # FalkorDB
# 
# >What is `FalkorDB`?
# 
# >- FalkorDB is an `open-source database management system` that specializes in graph database technology.
# >- FalkorDB allows you to represent and store data in nodes and edges, making it ideal for handling connected data and relationships.
# >- FalkorDB Supports OpenCypher query language with proprietary extensions, making it easy to interact with and query your graph data.
# >- With FalkorDB, you can achieve high-performance `graph traversals and queries`, suitable for production-level systems.
# 
# >Get started with FalkorDB by visiting [their website](https://docs.falkordb.com/).

# ## Installation and Setup
# 
# - Install the Python SDK with `pip install falkordb langchain-falkordb`

# ## VectorStore
# 
# The FalkorDB vector index is used as a vectorstore,
# whether for semantic search or example selection.
# 
# ```python
# from langchain_community.vectorstores.falkordb_vector import FalkorDBVector
# ```
# or 
# 
# ```python
# from langchain_falkordb.vectorstore import FalkorDBVector
# ```
# 
# See a [usage example](/docs/integrations/vectorstores/falkordbvector.ipynb)

# ## Memory
# 
# See a [usage example](/docs/integrations/memory/falkordb_chat_message_history.ipynb).
# 
# ```python
# from langchain_falkordb.message_history import (
#     FalkorDBChatMessageHistory,
# )
# ```
