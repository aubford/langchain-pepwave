#!/usr/bin/env python
# coding: utf-8

# # Dria
# 
# >[Dria](https://dria.co/) is a hub of public RAG models for developers to both contribute and utilize a shared embedding lake. This notebook demonstrates how to use the `Dria API` for data retrieval tasks.

# # Installation
# 
# Ensure you have the `dria` package installed. You can install it using pip:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet dria')


# # Configure API Key
# 
# Set up your Dria API key for access.

# In[1]:


import os

os.environ["DRIA_API_KEY"] = "DRIA_API_KEY"


# # Initialize Dria Retriever
# 
# Create an instance of `DriaRetriever`.

# In[ ]:


from langchain_community.retrievers import DriaRetriever

api_key = os.getenv("DRIA_API_KEY")
retriever = DriaRetriever(api_key=api_key)


# # **Create Knowledge Base**
# 
# Create a knowledge on [Dria's Knowledge Hub](https://dria.co/knowledge)

# In[ ]:


contract_id = retriever.create_knowledge_base(
    name="France's AI Development",
    embedding=DriaRetriever.models.jina_embeddings_v2_base_en.value,
    category="Artificial Intelligence",
    description="Explore the growth and contributions of France in the field of Artificial Intelligence.",
)


# # Add Data
# 
# Load data into your Dria knowledge base.

# In[ ]:


texts = [
    "The first text to add to Dria.",
    "Another piece of information to store.",
    "More data to include in the Dria knowledge base.",
]

ids = retriever.add_texts(texts)
print("Data added with IDs:", ids)


# # Retrieve Data
# 
# Use the retriever to find relevant documents given a query.

# In[ ]:


query = "Find information about Dria."
result = retriever.invoke(query)
for doc in result:
    print(doc)

