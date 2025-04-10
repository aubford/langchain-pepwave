#!/usr/bin/env python
# coding: utf-8

# # Open Document Format (ODT)
# 
# >The [Open Document Format for Office Applications (ODF)](https://en.wikipedia.org/wiki/OpenDocument), also known as `OpenDocument`, is an open file format for word processing documents, spreadsheets, presentations and graphics and using ZIP-compressed XML files. It was developed with the aim of providing an open, XML-based file format specification for office applications.
# 
# >The standard is developed and maintained by a technical committee in the Organization for the Advancement of Structured Information Standards (`OASIS`) consortium. It was based on the Sun Microsystems specification for OpenOffice.org XML, the default format for `OpenOffice.org` and `LibreOffice`. It was originally developed for `StarOffice` "to provide an open standard for office documents."
# 
# The `UnstructuredODTLoader` is used to load `Open Office ODT` files.

# In[1]:


from langchain_community.document_loaders import UnstructuredODTLoader

loader = UnstructuredODTLoader("example_data/fake.odt", mode="elements")
docs = loader.load()
docs[0]


# In[ ]:




