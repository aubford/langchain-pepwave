#!/usr/bin/env python
# coding: utf-8

# # Jupyter Notebook
# 
# >[Jupyter Notebook](https://en.wikipedia.org/wiki/Project_Jupyter#Applications) (formerly `IPython Notebook`) is a web-based interactive computational environment for creating notebook documents.
# 
# This notebook covers how to load data from a `Jupyter notebook (.ipynb)` into a format suitable by LangChain.

# In[1]:


from langchain_community.document_loaders import NotebookLoader


# In[2]:


loader = NotebookLoader(
    "example_data/notebook.ipynb",
    include_outputs=True,
    max_output_length=20,
    remove_newline=True,
)


# `NotebookLoader.load()` loads the `.ipynb` notebook file into a `Document` object.
# 
# **Parameters**:
# 
# * `include_outputs` (bool): whether to include cell outputs in the resulting document (default is False).
# * `max_output_length` (int): the maximum number of characters to include from each cell output (default is 10).
# * `remove_newline` (bool): whether to remove newline characters from the cell sources and outputs (default is False).
# * `traceback` (bool): whether to include full traceback (default is False).

# In[3]:


loader.load()

