#!/usr/bin/env python
# coding: utf-8

# # How to handle long text when doing extraction
# 
# When working with files, like PDFs, you're likely to encounter text that exceeds your language model's context window. To process this text, consider these strategies:
# 
# 1. **Change LLM** Choose a different LLM that supports a larger context window.
# 2. **Brute Force** Chunk the document, and extract content from each chunk.
# 3. **RAG** Chunk the document, index the chunks, and only extract content from a subset of chunks that look "relevant".
# 
# Keep in mind that these strategies have different trade off and the best strategy likely depends on the application that you're designing!
# 
# This guide demonstrates how to implement strategies 2 and 3.

# ## Setup
# 
# First we'll install the dependencies needed for this guide:

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community lxml faiss-cpu langchain-openai')


# Now we need some example data! Let's download an article about [cars from wikipedia](https://en.wikipedia.org/wiki/Car) and load it as a LangChain [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html).

# In[1]:


import re

import requests
from langchain_community.document_loaders import BSHTMLLoader

# Download the content
response = requests.get("https://en.wikipedia.org/wiki/Car")
# Write it to a file
with open("car.html", "w", encoding="utf-8") as f:
    f.write(response.text)
# Load it with an HTML parser
loader = BSHTMLLoader("car.html")
document = loader.load()[0]
# Clean up code
# Replace consecutive new lines with a single new line
document.page_content = re.sub("\n\n+", "\n", document.page_content)


# In[2]:


print(len(document.page_content))


# ## Define the schema
# 
# Following the [extraction tutorial](/docs/tutorials/extraction), we will use Pydantic to define the schema of information we wish to extract. In this case, we will extract a list of "key developments" (e.g., important historical events) that include a year and description.
# 
# Note that we also include an `evidence` key and instruct the model to provide in verbatim the relevant sentences of text from the article. This allows us to compare the extraction results to (the model's reconstruction of) text from the original document.

# In[3]:


from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field


class KeyDevelopment(BaseModel):
    """Information about a development in the history of cars."""

    year: int = Field(
        ..., description="The year when there was an important historic development."
    )
    description: str = Field(
        ..., description="What happened in this year? What was the development?"
    )
    evidence: str = Field(
        ...,
        description="Repeat in verbatim the sentence(s) from which the year and description information were extracted",
    )


class ExtractionData(BaseModel):
    """Extracted information about key developments in the history of cars."""

    key_developments: List[KeyDevelopment]


# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert at identifying key historic development in text. "
            "Only extract important historic developments. Extract nothing if no important information can be found in the text.",
        ),
        ("human", "{text}"),
    ]
)


# ## Create an extractor
# 
# Let's select an LLM. Because we are using tool-calling, we will need a model that supports a tool-calling feature. See [this table](/docs/integrations/chat) for available LLMs.
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs
#   customVarName="llm"
#   overrideParams={{openai: {model: "gpt-4o", kwargs: "temperature=0"}}}
# />
# 

# In[4]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)


# In[5]:


extractor = prompt | llm.with_structured_output(
    schema=ExtractionData,
    include_raw=False,
)


# ## Brute force approach
# 
# Split the documents into chunks such that each chunk fits into the context window of the LLMs.

# In[6]:


from langchain_text_splitters import TokenTextSplitter

text_splitter = TokenTextSplitter(
    # Controls the size of each chunk
    chunk_size=2000,
    # Controls overlap between chunks
    chunk_overlap=20,
)

texts = text_splitter.split_text(document.page_content)


# Use [batch](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.Runnable.html) functionality to run the extraction in **parallel** across each chunk! 
# 
# :::tip
# You can often use .batch() to parallelize the extractions! `.batch` uses a threadpool under the hood to help you parallelize workloads.
# 
# If your model is exposed via an API, this will likely speed up your extraction flow!
# :::

# In[7]:


# Limit just to the first 3 chunks
# so the code can be re-run quickly
first_few = texts[:3]

extractions = extractor.batch(
    [{"text": text} for text in first_few],
    {"max_concurrency": 5},  # limit the concurrency by passing max concurrency!
)


# ### Merge results
# 
# After extracting data from across the chunks, we'll want to merge the extractions together.

# In[8]:


key_developments = []

for extraction in extractions:
    key_developments.extend(extraction.key_developments)

key_developments[:10]


# ## RAG based approach
# 
# Another simple idea is to chunk up the text, but instead of extracting information from every chunk, just focus on the the most relevant chunks.
# 
# :::caution
# It can be difficult to identify which chunks are relevant.
# 
# For example, in the `car` article we're using here, most of the article contains key development information. So by using
# **RAG**, we'll likely be throwing out a lot of relevant information.
# 
# We suggest experimenting with your use case and determining whether this approach works or not.
# :::
# 
# To implement the RAG based approach: 
# 
# 1. Chunk up your document(s) and index them (e.g., in a vectorstore);
# 2. Prepend the `extractor` chain with a retrieval step using the vectorstore.
# 
# Here's a simple example that relies on the `FAISS` vectorstore.

# In[9]:


from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

texts = text_splitter.split_text(document.page_content)
vectorstore = FAISS.from_texts(texts, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 1}
)  # Only extract from first document


# In this case the RAG extractor is only looking at the top document.

# In[10]:


rag_extractor = {
    "text": retriever | (lambda docs: docs[0].page_content)  # fetch content of top doc
} | extractor


# In[11]:


results = rag_extractor.invoke("Key developments associated with cars")


# In[13]:


for key_development in results.key_developments:
    print(key_development)


# ## Common issues
# 
# Different methods have their own pros and cons related to cost, speed, and accuracy.
# 
# Watch out for these issues:
# 
# * Chunking content means that the LLM can fail to extract information if the information is spread across multiple chunks.
# * Large chunk overlap may cause the same information to be extracted twice, so be prepared to de-duplicate!
# * LLMs can make up data. If looking for a single fact across a large text and using a brute force approach, you may end up getting more made up data.
