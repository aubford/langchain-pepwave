#!/usr/bin/env python
# coding: utf-8

# # acreom

# [acreom](https://acreom.com) is a dev-first knowledge base with tasks running on local markdown files.
# 
# Below is an example on how to load a local acreom vault into Langchain. As the local vault in acreom is a folder of plain text .md files, the loader requires the path to the directory. 
# 
# Vault files may contain some metadata which is stored as a YAML header. These values will be added to the document’s metadata if `collect_metadata` is set to true. 

# In[ ]:


from langchain_community.document_loaders import AcreomLoader


# In[ ]:


loader = AcreomLoader("<path-to-acreom-vault>", collect_metadata=False)


# In[ ]:


docs = loader.load()

