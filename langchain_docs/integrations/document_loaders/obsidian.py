#!/usr/bin/env python
# coding: utf-8

# # Obsidian
# 
# >[Obsidian](https://obsidian.md/) is a powerful and extensible knowledge base
# that works on top of your local folder of plain text files.
# 
# This notebook covers how to load documents from an `Obsidian` database.
# 
# Since `Obsidian` is just stored on disk as a folder of Markdown files, the loader just takes a path to this directory.
# 
# `Obsidian` files also sometimes contain [metadata](https://help.obsidian.md/Editing+and+formatting/Metadata) which is a YAML block at the top of the file. These values will be added to the document's metadata. (`ObsidianLoader` can also be passed a `collect_metadata=False` argument to disable this behavior.)

# In[1]:


from langchain_community.document_loaders import ObsidianLoader


# In[ ]:


loader = ObsidianLoader("<path-to-obsidian>")


# In[ ]:


docs = loader.load()

