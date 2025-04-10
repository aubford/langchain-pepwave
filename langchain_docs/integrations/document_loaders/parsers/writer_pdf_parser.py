#!/usr/bin/env python
# coding: utf-8

# # Writer PDF Parser
# 
# This notebook provides a quick overview for getting started with the Writer `PDFParser` [document loader](/docs/concepts/document_loaders/).
# 
# Writer's [PDF Parser](https://dev.writer.com/api-guides/api-reference/tool-api/pdf-parser#parse-pdf) converts PDF documents into other formats like text or Markdown. This is particularly useful when you need to extract and process text content from PDF files for further analysis or integration into your workflow. In `langchain-writer`, we provide usage of Writer's PDF Parser as a LangChain document parser.
# 
# ## Overview
# 
# ### Integration details
# | Class                                                                                                                              | Package          | Local | Serializable | JS support |                                        Package downloads                                         |                                        Package latest                                         |
# |:-----------------------------------------------------------------------------------------------------------------------------------|:-----------------| :---: | :---: |:----------:|:------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------:|
# | [PDFParser](https://github.com/writer/langchain-writer/blob/main/langchain_writer/pdf_parser.py#L55) | [langchain-writer](https://pypi.org/project/langchain-writer/) |      ❌       |                                       ❌                                       | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-writer?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-writer?style=flat-square&label=%20) |

# ## Setup
# 
# The `PDFParser` is available in the `langchain-writer` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --quiet -U langchain-writer')


# ### Credentials
# 
# Sign up for [Writer AI Studio](https://app.writer.com/aistudio/signup?utm_campaign=devrel) to generate an API key (you can follow this [Quickstart](https://dev.writer.com/api-guides/quickstart)). Then, set the WRITER_API_KEY environment variable:

# In[ ]:


import getpass
import os

if not os.getenv("WRITER_API_KEY"):
    os.environ["WRITER_API_KEY"] = getpass.getpass("Enter your Writer API key: ")


# It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability. If you wish to do so, you can set the `LANGSMITH_TRACING` and `LANGSMITH_API_KEY` environment variables:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ### Instantiation
# 
# Next, instantiate an instance of the Writer PDF Parser with the desired output format:

# In[ ]:


from langchain_writer.pdf_parser import PDFParser

parser = PDFParser(format="markdown")


# ## Usage
# 
# There are two ways to use the PDF Parser, either synchronously or asynchronously. In either case, the PDF Parser will return a list of `Document` objects, each containing the parsed content of a page from the PDF file.
# 
# ### Synchronous usage
# 
# To invoke the PDF Parser synchronously, pass a `Blob` object to the `parse` method referencing the PDF file you want to parse:

# In[ ]:


from langchain_core.documents.base import Blob

file = Blob.from_path("../example_data/layout-parser-paper.pdf")

parsed_pages = parser.parse(blob=file)
parsed_pages


# ### Asynchronous usage
# 
# To invoke the PDF Parser asynchronously, pass a `Blob` object to the `aparse` method referencing the PDF file you want to parse:

# In[ ]:


parsed_pages_async = await parser.aparse(blob=file)
parsed_pages_async


# ## API reference
# 
# For detailed documentation of all `PDFParser` features and configurations, head to the [API reference](https://python.langchain.com/api_reference/writer/pdf_parser/langchain_writer.pdf_parser.PDFParser.html#langchain_writer.pdf_parser.PDFParser).
# 
# ## Additional resources
# You can find information about Writer's models (including costs, context windows, and supported input types) and tools in the [Writer docs](https://dev.writer.com/home).
# 
