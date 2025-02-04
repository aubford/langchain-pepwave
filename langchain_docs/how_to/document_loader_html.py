#!/usr/bin/env python
# coding: utf-8

# # How to load HTML
# 
# The HyperText Markup Language or [HTML](https://en.wikipedia.org/wiki/HTML) is the standard markup language for documents designed to be displayed in a web browser.
# 
# This covers how to load `HTML` documents into a LangChain [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html#langchain_core.documents.base.Document) objects that we can use downstream.
# 
# Parsing HTML files often requires specialized tools. Here we demonstrate parsing via [Unstructured](https://unstructured-io.github.io/unstructured/) and [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/), which can be installed via pip. Head over to the integrations page to find integrations with additional services, such as [Azure AI Document Intelligence](/docs/integrations/document_loaders/azure_document_intelligence) or [FireCrawl](/docs/integrations/document_loaders/firecrawl).
# 
# ## Loading HTML with Unstructured

# In[ ]:


get_ipython().run_line_magic('pip', 'install unstructured')


# In[2]:


from langchain_community.document_loaders import UnstructuredHTMLLoader

file_path = "../../docs/integrations/document_loaders/example_data/fake-content.html"

loader = UnstructuredHTMLLoader(file_path)
data = loader.load()

print(data)


# ## Loading HTML with BeautifulSoup4
# 
# We can also use `BeautifulSoup4` to load HTML documents using the `BSHTMLLoader`.  This will extract the text from the HTML into `page_content`, and the page title as `title` into `metadata`.

# In[ ]:


get_ipython().run_line_magic('pip', 'install bs4')


# In[4]:


from langchain_community.document_loaders import BSHTMLLoader

loader = BSHTMLLoader(file_path)
data = loader.load()

print(data)

