#!/usr/bin/env python
# coding: utf-8

# # RST
# 
# >A [reStructured Text (RST)](https://en.wikipedia.org/wiki/ReStructuredText) file is a file format for textual data used primarily in the Python programming language community for technical documentation.

# ## `UnstructuredRSTLoader`
# 
# You can load data from RST files with `UnstructuredRSTLoader` using the following workflow.

# In[1]:


from langchain_community.document_loaders import UnstructuredRSTLoader

loader = UnstructuredRSTLoader(file_path="./example_data/README.rst", mode="elements")
docs = loader.load()

print(docs[0])


# In[ ]:




