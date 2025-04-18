#!/usr/bin/env python
# coding: utf-8

# 
# # vlite
# 
# VLite is a simple and blazing fast vector database that allows you to store and retrieve data semantically using embeddings. Made with numpy, vlite is a lightweight batteries-included database to implement RAG, similarity search, and embeddings into your projects.
# 
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration
# 
# ## Installation
# 
# To use the VLite in LangChain, you need to install the `vlite` package:
# 
# ```bash
# !pip install vlite
# ```
# 
# ## Importing VLite
# 
# ```python
# from langchain_community.vectorstores import VLite
# ```
# 
# ## Basic Example
# 
# In this basic example, we load a text document, and store them in the VLite vector database. Then, we perform a similarity search to retrieve relevant documents based on a query.
# 
# VLite handles chunking and embedding of the text for you, and you can change these parameters by pre-chunking the text and/or embeddings those chunks into the VLite database.
# 
# ```python
# from langchain.document_loaders import TextLoader
# from langchain.text_splitter import CharacterTextSplitter
# 
# # Load the document and split it into chunks
# loader = TextLoader("path/to/document.txt")
# documents = loader.load()
# 
# # Create a VLite instance
# vlite = VLite(collection="my_collection")
# 
# # Add documents to the VLite vector database
# vlite.add_documents(documents)
# 
# # Perform a similarity search
# query = "What is the main topic of the document?"
# docs = vlite.similarity_search(query)
# 
# # Print the most relevant document
# print(docs[0].page_content)
# ```
# 
# ## Adding Texts and Documents
# 
# You can add texts or documents to the VLite vector database using the `add_texts` and `add_documents` methods, respectively.
# 
# ```python
# # Add texts to the VLite vector database
# texts = ["This is the first text.", "This is the second text."]
# vlite.add_texts(texts)
# 
# # Add documents to the VLite vector database
# documents = [Document(page_content="This is a document.", metadata={"source": "example.txt"})]
# vlite.add_documents(documents)
# ```
# 
# ## Similarity Search
# 
# VLite provides methods for performing similarity search on the stored documents.
# 
# ```python
# # Perform a similarity search
# query = "What is the main topic of the document?"
# docs = vlite.similarity_search(query, k=3)
# 
# # Perform a similarity search with scores
# docs_with_scores = vlite.similarity_search_with_score(query, k=3)
# ```
# 
# ## Max Marginal Relevance Search
# 
# VLite also supports Max Marginal Relevance (MMR) search, which optimizes for both similarity to the query and diversity among the retrieved documents.
# 
# ```python
# # Perform an MMR search
# docs = vlite.max_marginal_relevance_search(query, k=3)
# ```
# 
# ## Updating and Deleting Documents
# 
# You can update or delete documents in the VLite vector database using the `update_document` and `delete` methods.
# 
# ```python
# # Update a document
# document_id = "doc_id_1"
# updated_document = Document(page_content="Updated content", metadata={"source": "updated.txt"})
# vlite.update_document(document_id, updated_document)
# 
# # Delete documents
# document_ids = ["doc_id_1", "doc_id_2"]
# vlite.delete(document_ids)
# ```
# 
# ## Retrieving Documents
# 
# You can retrieve documents from the VLite vector database based on their IDs or metadata using the `get` method.
# 
# ```python
# # Retrieve documents by IDs
# document_ids = ["doc_id_1", "doc_id_2"]
# docs = vlite.get(ids=document_ids)
# 
# # Retrieve documents by metadata
# metadata_filter = {"source": "example.txt"}
# docs = vlite.get(where=metadata_filter)
# ```
# 
# ## Creating VLite Instances
# 
# You can create VLite instances using various methods:
# 
# ```python
# # Create a VLite instance from texts
# vlite = VLite.from_texts(texts)
# 
# # Create a VLite instance from documents
# vlite = VLite.from_documents(documents)
# 
# # Create a VLite instance from an existing index
# vlite = VLite.from_existing_index(collection="existing_collection")
# ```
# 
# ## Additional Features
# 
# VLite provides additional features for managing the vector database:
# 
# ```python
# from langchain.vectorstores import VLite
# vlite = VLite(collection="my_collection")
# 
# # Get the number of items in the collection
# count = vlite.count()
# 
# # Save the collection
# vlite.save()
# 
# # Clear the collection
# vlite.clear()
# 
# # Get collection information
# vlite.info()
# 
# # Dump the collection data
# data = vlite.dump()
# ```

# 
