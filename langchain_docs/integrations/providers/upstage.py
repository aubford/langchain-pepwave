#!/usr/bin/env python
# coding: utf-8

# # Upstage
# 
# >[Upstage](https://upstage.ai) is a leading artificial intelligence (AI) company specializing in delivering above-human-grade performance LLM components.
# >
# >**Solar Pro** is an enterprise-grade LLM optimized for single-GPU deployment, excelling in instruction-following and processing structured formats like HTML and Markdown. It supports English, Korean, and Japanese with top multilingual performance and offers domain expertise in finance, healthcare, and legal.
# 
# >Other than Solar, Upstage also offers features for real-world RAG (retrieval-augmented generation), such as **Document Parse** and **Groundedness Check**. 
# 

# ### Upstage LangChain integrations
# 
# | API | Description | Import | Example usage |
# | --- | --- | --- | --- |
# | Chat | Build assistants using Solar Chat | `from langchain_upstage import ChatUpstage` | [Go](../../chat/upstage) |
# | Text Embedding | Embed strings to vectors | `from langchain_upstage import UpstageEmbeddings` | [Go](../../text_embedding/upstage) |
# | Groundedness Check | Verify groundedness of assistant's response | `from langchain_upstage import UpstageGroundednessCheck` | [Go](../../tools/upstage_groundedness_check) |
# | Document Parse | Serialize documents with tables and figures | `from langchain_upstage import UpstageDocumentParseLoader` | [Go](../../document_loaders/upstage) |
# 
# See [documentations](https://console.upstage.ai/docs/getting-started/overview) for more details about the models and features.

# ## Installation and Setup
# 
# Install `langchain-upstage` package:
# 
# ```bash
# pip install -qU langchain-core langchain-upstage
# ```
# 

# Get [API Keys](https://console.upstage.ai) and set environment variable `UPSTAGE_API_KEY`.

# In[ ]:


import os

os.environ["UPSTAGE_API_KEY"] = "YOUR_API_KEY"


# ## Chat models
# 
# ### Solar LLM
# 
# See [a usage example](/docs/integrations/chat/upstage).

# In[ ]:


from langchain_upstage import ChatUpstage

chat = ChatUpstage()
response = chat.invoke("Hello, how are you?")
print(response)


# ## Embedding models
# 
# See [a usage example](/docs/integrations/text_embedding/upstage).

# In[ ]:


from langchain_upstage import UpstageEmbeddings

embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
doc_result = embeddings.embed_documents(
    ["Sung is a professor.", "This is another document"]
)
print(doc_result)

query_result = embeddings.embed_query("What does Sung do?")
print(query_result)


# ## Document loader
# 
# ### Document Parse
# 
# See [a usage example](/docs/integrations/document_loaders/upstage).

# In[ ]:


from langchain_upstage import UpstageDocumentParseLoader

file_path = "/PATH/TO/YOUR/FILE.pdf"
layzer = UpstageDocumentParseLoader(file_path, split="page")

# For improved memory efficiency, consider using the lazy_load method to load documents page by page.
docs = layzer.load()  # or layzer.lazy_load()

for doc in docs[:3]:
    print(doc)


# ## Tools
# 
# ### Groundedness Check
# 
# See [a usage example](/docs/integrations/tools/upstage_groundedness_check).

# In[ ]:


from langchain_upstage import UpstageGroundednessCheck

groundedness_check = UpstageGroundednessCheck()

request_input = {
    "context": "Mauna Kea is an inactive volcano on the island of Hawaii. Its peak is 4,207.3 m above sea level, making it the highest point in Hawaii and second-highest peak of an island on Earth.",
    "answer": "Mauna Kea is 5,207.3 meters tall.",
}
response = groundedness_check.invoke(request_input)
print(response)

