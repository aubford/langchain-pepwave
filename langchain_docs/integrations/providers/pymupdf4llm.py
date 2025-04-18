#!/usr/bin/env python
# coding: utf-8

# # PyMuPDF4LLM
# 
# [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm) is aimed to make it easier to extract PDF content in Markdown format, needed for LLM & RAG applications.
# 
# [langchain-pymupdf4llm](https://github.com/lakinduboteju/langchain-pymupdf4llm) integrates PyMuPDF4LLM to LangChain as a Document Loader.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-pymupdf4llm')


# In[ ]:


from langchain_pymupdf4llm import PyMuPDF4LLMLoader, PyMuPDF4LLMParser

