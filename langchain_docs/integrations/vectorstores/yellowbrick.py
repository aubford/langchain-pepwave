#!/usr/bin/env python
# coding: utf-8

# # Yellowbrick
# 
# [Yellowbrick](https://yellowbrick.com/yellowbrick-data-warehouse/) is an elastic, massively parallel processing (MPP) SQL database that runs in the cloud and on-premises, using kubernetes for scale, resilience and cloud portability. Yellowbrick is designed to address the largest and most complex business-critical data warehousing use cases. The efficiency at scale that Yellowbrick provides also enables it to be used as a high performance and scalable vector database to store and search vectors with SQL. 
# 

# ## Using Yellowbrick as the vector store for ChatGpt
# 
# This tutorial demonstrates how to create a simple chatbot backed by ChatGpt that uses Yellowbrick as a vector store to support Retrieval Augmented Generation (RAG). What you'll need:
# 
# 1. An account on the [Yellowbrick sandbox](https://cloudlabs.yellowbrick.com/)
# 2. An api key from [OpenAI](https://platform.openai.com/)
# 
# The tutorial is divided into five parts. First we'll use langchain to create a baseline chatbot to interact with ChatGpt without a vector store. Second, we'll create an embeddings table in Yellowbrick that will represent the vector store. Third, we'll load a series of documents (the Administration chapter of the Yellowbrick Manual). Fourth, we'll create the vector representation of those documents and store in a Yellowbrick table.  Lastly, we'll send the same queries to the improved chatbox to see the results.
# 

# In[ ]:


# Install all needed libraries
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-openai langchain-community')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  psycopg2-binary')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  tiktoken')


# ## Setup: Enter the information used to connect to Yellowbrick and OpenAI API
# 
# Our chatbot integrates with ChatGpt via the langchain library, so you'll need an API key from OpenAI first:
# 
# To get an api key for OpenAI:
# 1. Register at https://platform.openai.com/
# 2. Add a payment method - You're unlikely to go over free quota
# 3. Create an API key
# 
# You'll also need your Username, Password, and Database name from the welcome email when you sign up for the Yellowbrick Sandbox Account.
# 

# The following should be modified to include the information for your Yellowbrick database and OpenAPI Key

# In[ ]:


# Modify these values to match your Yellowbrick Sandbox and OpenAI API Key
YBUSER = "[SANDBOX USER]"
YBPASSWORD = "[SANDBOX PASSWORD]"
YBDATABASE = "[SANDBOX_DATABASE]"
YBHOST = "trialsandbox.sandbox.aws.yellowbrickcloud.com"

OPENAI_API_KEY = "[OPENAI API KEY]"


# In[ ]:


# Import libraries and setup keys / login info
import os
import pathlib
import re
import sys
import urllib.parse as urlparse
from getpass import getpass

import psycopg2
from IPython.display import Markdown, display
from langchain.chains import LLMChain, RetrievalQAWithSourcesChain
from langchain_community.vectorstores import Yellowbrick
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Establish connection parameters to Yellowbrick.  If you've signed up for Sandbox, fill in the information from your welcome mail here:
yellowbrick_connection_string = (
    f"postgres://{urlparse.quote(YBUSER)}:{YBPASSWORD}@{YBHOST}:5432/{YBDATABASE}"
)

YB_DOC_DATABASE = "sample_data"
YB_DOC_TABLE = "yellowbrick_documentation"
embedding_table = "my_embeddings"

# API Key for OpenAI.  Signup at https://platform.openai.com
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


# ## Part 1: Creating a baseline chatbot backed by ChatGpt without a Vector Store
# 
# We will use langchain to query ChatGPT.  As there is no Vector Store, ChatGPT will have no context in which to answer the question.
# 

# In[ ]:


# Set up the chat model and specific prompt
system_template = """If you don't know the answer, Make up your best guess."""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)

chain_type_kwargs = {"prompt": prompt}
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # Modify model_name if you have access to GPT-4
    temperature=0,
    max_tokens=256,
)

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=False,
)


def print_result_simple(query):
    result = chain(query)
    output_text = f"""### Question:
  {query}
  ### Answer: 
  {result['text']}
    """
    display(Markdown(output_text))


# Use the chain to query
print_result_simple("How many databases can be in a Yellowbrick Instance?")

print_result_simple("What's an easy way to add users in bulk to Yellowbrick?")


# ## Part 2: Connect to Yellowbrick and create the embedding tables
# 
# To load your document embeddings into Yellowbrick, you should create your own table for storing them in. Note that the 
# Yellowbrick database that the table is in has to be UTF-8 encoded. 
# 
# Create a table in a UTF-8 database with the following schema, providing a table name of your choice:
# 

# In[ ]:


# Establish a connection to the Yellowbrick database
try:
    conn = psycopg2.connect(yellowbrick_connection_string)
except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

# Create a cursor object using the connection
cursor = conn.cursor()

# Define the SQL statement to create a table
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {embedding_table} (
    doc_id uuid NOT NULL,
    embedding_id smallint NOT NULL,
    embedding double precision NOT NULL
)
DISTRIBUTE ON (doc_id);
truncate table {embedding_table};
"""

# Execute the SQL query to create a table
try:
    cursor.execute(create_table_query)
    print(f"Table '{embedding_table}' created successfully!")
except psycopg2.Error as e:
    print(f"Error creating table: {e}")
    conn.rollback()

# Commit changes and close the cursor and connection
conn.commit()
cursor.close()
conn.close()


# ## Part 3: Extract the documents to index from an existing table in Yellowbrick
# Extract document paths and contents from an existing Yellowbrick table. We'll use these documents to create embeddings from in the next step.
# 
# 
# 
# 

# In[ ]:


yellowbrick_doc_connection_string = (
    f"postgres://{urlparse.quote(YBUSER)}:{YBPASSWORD}@{YBHOST}:5432/{YB_DOC_DATABASE}"
)

print(yellowbrick_doc_connection_string)

# Establish a connection to the Yellowbrick database
conn = psycopg2.connect(yellowbrick_doc_connection_string)

# Create a cursor object
cursor = conn.cursor()

# Query to select all documents from the table
query = f"SELECT path, document FROM {YB_DOC_TABLE}"

# Execute the query
cursor.execute(query)

# Fetch all documents
yellowbrick_documents = cursor.fetchall()

print(f"Extracted {len(yellowbrick_documents)} documents successfully!")

# Close the cursor and connection
cursor.close()
conn.close()


# ## Part 4: Load the Yellowbrick Vector Store with Documents
# Go through documents, split them into digestable chunks, create the embedding and insert into the Yellowbrick table. This takes around 5 minutes.
# 

# In[ ]:


# Split documents into chunks for conversion to embeddings
DOCUMENT_BASE_URL = "https://docs.yellowbrick.com/6.7.1/"  # Actual URL


separator = "\n## "  # This separator assumes Markdown docs from the repo uses ### as logical main header most of the time
chunk_size_limit = 2000
max_chunk_overlap = 200

documents = [
    Document(
        page_content=document[1],
        metadata={"source": DOCUMENT_BASE_URL + document[0].replace(".md", ".html")},
    )
    for document in yellowbrick_documents
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size_limit,
    chunk_overlap=max_chunk_overlap,
    separators=[separator, "\nn", "\n", ",", " ", ""],
)
split_docs = text_splitter.split_documents(documents)

docs_text = [doc.page_content for doc in split_docs]

embeddings = OpenAIEmbeddings()
vector_store = Yellowbrick.from_documents(
    documents=split_docs,
    embedding=embeddings,
    connection_string=yellowbrick_connection_string,
    table=embedding_table,
)

print(f"Created vector store with {len(documents)} documents")


# ## Part 5: Creating a chatbot that uses Yellowbrick as the vector store
# 
# Next, we add Yellowbrick as a vector store. The vector store has been populated with embeddings representing the administrative chapter of the Yellowbrick product documentation.
# 
# We'll send the same queries as above to see the impoved responses.
# 

# In[ ]:


system_template = """Use the following pieces of context to answer the users question.
Take note of the sources and include them in the answer in the format: "SOURCES: source1 source2", use "SOURCES" in capital letters regardless of the number of sources.
If you don't know the answer, just say that "I don't know", don't try to make up an answer.
----------------
{summaries}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)

vector_store = Yellowbrick(
    OpenAIEmbeddings(),
    yellowbrick_connection_string,
    embedding_table,  # Change the table name to reflect your embeddings
)

chain_type_kwargs = {"prompt": prompt}
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # Modify model_name if you have access to GPT-4
    temperature=0,
    max_tokens=256,
)
chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs,
)


def print_result_sources(query):
    result = chain(query)
    output_text = f"""### Question: 
  {query}
  ### Answer: 
  {result['answer']}
  ### Sources: 
  {result['sources']}
  ### All relevant sources:
  {', '.join(list(set([doc.metadata['source'] for doc in result['source_documents']])))}
    """
    display(Markdown(output_text))


# Use the chain to query

print_result_sources("How many databases can be in a Yellowbrick Instance?")

print_result_sources("Whats an easy way to add users in bulk to Yellowbrick?")


# ## Part 6: Introducing an Index to Increase Performance
# 
# Yellowbrick also supports indexing using the Locality-Sensitive Hashing approach. This is an approximate nearest-neighbor search technique, and allows one to trade off similarity search time at the expense of accuracy. The index introduces two new tunable parameters:
# 
# - The number of hyperplanes, which is provided as an argument to `create_lsh_index(num_hyperplanes)`. The more documents, the more hyperplanes are needed. LSH is a form of dimensionality reduction. The original embeddings are transformed into lower dimensional vectors where the number of components is the same as the number of hyperplanes.
# - The Hamming distance, an integer representing the breadth of the search. Smaller Hamming distances result in faster retreival but lower accuracy.
# 
# Here's how you can create an index on the embeddings we loaded into Yellowbrick. We'll also re-run the previous chat session, but this time the retrieval will use the index. Note that for such a small number of documents, you won't see the benefit of indexing in terms of performance.

# In[ ]:


system_template = """Use the following pieces of context to answer the users question.
Take note of the sources and include them in the answer in the format: "SOURCES: source1 source2", use "SOURCES" in capital letters regardless of the number of sources.
If you don't know the answer, just say that "I don't know", don't try to make up an answer.
----------------
{summaries}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)

vector_store = Yellowbrick(
    OpenAIEmbeddings(),
    yellowbrick_connection_string,
    embedding_table,  # Change the table name to reflect your embeddings
)

lsh_params = Yellowbrick.IndexParams(
    Yellowbrick.IndexType.LSH, {"num_hyperplanes": 8, "hamming_distance": 2}
)
vector_store.create_index(lsh_params)

chain_type_kwargs = {"prompt": prompt}
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # Modify model_name if you have access to GPT-4
    temperature=0,
    max_tokens=256,
)
chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(
        k=5, search_kwargs={"index_params": lsh_params}
    ),
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs,
)


def print_result_sources(query):
    result = chain(query)
    output_text = f"""### Question: 
  {query}
  ### Answer: 
  {result['answer']}
  ### Sources: 
  {result['sources']}
  ### All relevant sources:
  {', '.join(list(set([doc.metadata['source'] for doc in result['source_documents']])))}
    """
    display(Markdown(output_text))


# Use the chain to query

print_result_sources("How many databases can be in a Yellowbrick Instance?")

print_result_sources("Whats an easy way to add users in bulk to Yellowbrick?")


# ## Next Steps:
# 
# This code can be modified to ask different questions. You can also load your own documents into the vector store. The langchain module is very flexible and can parse a large variety of files (including HTML, PDF, etc).
# 
# You can also modify this to use Huggingface embeddings models and Meta's Llama 2 LLM for a completely private chatbox experience.
