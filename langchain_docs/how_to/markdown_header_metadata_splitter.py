#!/usr/bin/env python
# coding: utf-8

# # How to split Markdown by Headers
# 
# ### Motivation
# 
# Many chat or Q+A applications involve chunking input documents prior to embedding and vector storage.
# 
# [These notes](https://www.pinecone.io/learn/chunking-strategies/) from Pinecone provide some useful tips:
# 
# ```
# When a full paragraph or document is embedded, the embedding process considers both the overall context and the relationships between the sentences and phrases within the text. This can result in a more comprehensive vector representation that captures the broader meaning and themes of the text.
# ```
#  
# As mentioned, chunking often aims to keep text with common context together. With this in mind, we might want to specifically honor the structure of the document itself. For example, a markdown file is organized by headers. Creating chunks within specific header groups is an intuitive idea. To address this challenge, we can use [MarkdownHeaderTextSplitter](https://python.langchain.com/api_reference/text_splitters/markdown/langchain_text_splitters.markdown.MarkdownHeaderTextSplitter.html). This will split a markdown file by a specified set of headers. 
# 
# For example, if we want to split this markdown:
# ```
# md = '# Foo\n\n ## Bar\n\nHi this is Jim  \nHi this is Joe\n\n ## Baz\n\n Hi this is Molly' 
# ```
#  
# We can specify the headers to split on:
# ```
# [("#", "Header 1"),("##", "Header 2")]
# ```
# 
# And content is grouped or split by common headers:
# ```
# {'content': 'Hi this is Jim  \nHi this is Joe', 'metadata': {'Header 1': 'Foo', 'Header 2': 'Bar'}}
# {'content': 'Hi this is Molly', 'metadata': {'Header 1': 'Foo', 'Header 2': 'Baz'}}
# ```
# 
# Let's have a look at some examples below.
# 
# ### Basic usage:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-text-splitters')


# In[1]:


from langchain_text_splitters import MarkdownHeaderTextSplitter


# In[2]:


markdown_document = "# Foo\n\n    ## Bar\n\nHi this is Jim\n\nHi this is Joe\n\n ### Boo \n\n Hi this is Lance \n\n ## Baz\n\n Hi this is Molly"

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
md_header_splits = markdown_splitter.split_text(markdown_document)
md_header_splits


# In[3]:


type(md_header_splits[0])


# By default, `MarkdownHeaderTextSplitter` strips headers being split on from the output chunk's content. This can be disabled by setting `strip_headers = False`.

# In[4]:


markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
md_header_splits = markdown_splitter.split_text(markdown_document)
md_header_splits


# :::note
# 
# The default `MarkdownHeaderTextSplitter` strips white spaces and new lines. To preserve the original formatting of your Markdown documents, check out [ExperimentalMarkdownSyntaxTextSplitter](https://python.langchain.com/api_reference/text_splitters/markdown/langchain_text_splitters.markdown.ExperimentalMarkdownSyntaxTextSplitter.html).
# 
# :::

# ### How to return Markdown lines as separate documents
# 
# By default, `MarkdownHeaderTextSplitter` aggregates lines based on the headers specified in `headers_to_split_on`. We can disable this by specifying `return_each_line`:

# In[5]:


markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on,
    return_each_line=True,
)
md_header_splits = markdown_splitter.split_text(markdown_document)
md_header_splits


# Note that here header information is retained in the `metadata` for each document.
# 
# ### How to constrain chunk size:
# 
# Within each markdown group we can then apply any text splitter we want, such as `RecursiveCharacterTextSplitter`, which allows for further control of the chunk size.

# In[6]:


markdown_document = "# Intro \n\n    ## History \n\n Markdown[9] is a lightweight markup language for creating formatted text using a plain-text editor. John Gruber created Markdown in 2004 as a markup language that is appealing to human readers in its source code form.[9] \n\n Markdown is widely used in blogging, instant messaging, online forums, collaborative software, documentation pages, and readme files. \n\n ## Rise and divergence \n\n As Markdown popularity grew rapidly, many Markdown implementations appeared, driven mostly by the need for \n\n additional features such as tables, footnotes, definition lists,[note 1] and Markdown inside HTML blocks. \n\n #### Standardization \n\n From 2012, a group of people, including Jeff Atwood and John MacFarlane, launched what Atwood characterised as a standardisation effort. \n\n ## Implementations \n\n Implementations of Markdown are available for over a dozen programming languages."

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
]

# MD splits
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
)
md_header_splits = markdown_splitter.split_text(markdown_document)

# Char-level splits
from langchain_text_splitters import RecursiveCharacterTextSplitter

chunk_size = 250
chunk_overlap = 30
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)

# Split
splits = text_splitter.split_documents(md_header_splits)
splits

