#!/usr/bin/env python
# coding: utf-8

# # Clarifai
# 
# >[Clarifai](https://www.clarifai.com/) is an AI Platform that provides the full AI lifecycle ranging from data exploration, data labeling, model training, evaluation, and inference. A Clarifai application can be used as a vector database after uploading inputs. 
# 
# This notebook shows how to use functionality related to the `Clarifai` vector database. Examples are shown to demonstrate text semantic search capabilities. Clarifai also supports semantic search with images, video frames, and localized search (see [Rank](https://docs.clarifai.com/api-guide/search/rank)) and attribute search (see [Filter](https://docs.clarifai.com/api-guide/search/filter)).
# 
# To use Clarifai, you must have an account and a Personal Access Token (PAT) key. 
# [Check here](https://clarifai.com/settings/security) to get or create a PAT.

# # Dependencies

# In[ ]:


# Install required dependencies
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  clarifai langchain-community')


# # Imports
# Here we will be setting the personal access token. You can find your PAT under settings/security on the platform.

# In[1]:


# Please login and get your API key from  https://clarifai.com/settings/security
from getpass import getpass

CLARIFAI_PAT = getpass()


# In[3]:


# Import the required modules
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Clarifai
from langchain_text_splitters import CharacterTextSplitter


# # Setup
# Setup the user id and app id where the text data will be uploaded. Note: when creating that application please select an appropriate base workflow for indexing your text documents such as the Language-Understanding workflow.
# 
# You will have to first create an account on [Clarifai](https://clarifai.com/login) and then create an application.

# In[24]:


USER_ID = "USERNAME_ID"
APP_ID = "APPLICATION_ID"
NUMBER_OF_DOCS = 2


# ## From Texts
# Create a Clarifai vectorstore from a list of texts. This section will upload each text with its respective metadata to a Clarifai Application. The Clarifai Application can then be used for semantic search to find relevant texts.

# In[16]:


texts = [
    "I really enjoy spending time with you",
    "I hate spending time with my dog",
    "I want to go for a run",
    "I went to the movies yesterday",
    "I love playing soccer with my friends",
]

metadatas = [
    {"id": i, "text": text, "source": "book 1", "category": ["books", "modern"]}
    for i, text in enumerate(texts)
]


# Alternatively you have an option to give custom input ids to the inputs.

# In[17]:


idlist = ["text1", "text2", "text3", "text4", "text5"]
metadatas = [
    {"id": idlist[i], "text": text, "source": "book 1", "category": ["books", "modern"]}
    for i, text in enumerate(texts)
]


# In[27]:


# There is an option to initialize clarifai vector store with pat as argument!
clarifai_vector_db = Clarifai(
    user_id=USER_ID,
    app_id=APP_ID,
    number_of_docs=NUMBER_OF_DOCS,
)


# Upload data into clarifai app.

# In[ ]:


# upload with metadata and custom input ids.
response = clarifai_vector_db.add_texts(texts=texts, ids=idlist, metadatas=metadatas)

# upload without metadata (Not recommended)- Since you will not be able to perform Search operation with respect to metadata.
# custom input_id (optional)
response = clarifai_vector_db.add_texts(texts=texts)


# You can create a clarifai vector DB store and ingest all the inputs into your app directly by,

# In[ ]:


clarifai_vector_db = Clarifai.from_texts(
    user_id=USER_ID,
    app_id=APP_ID,
    texts=texts,
    metadatas=metadatas,
)


# Search similar texts using similarity search function.

# In[31]:


docs = clarifai_vector_db.similarity_search("I would like to see you")
docs


# Further you can filter your search results by metadata.

# In[29]:


# There is lots powerful filtering you can do within an app by leveraging metadata filters.
# This one will limit the similarity query to only the texts that have key of "source" matching value of "book 1"
book1_similar_docs = clarifai_vector_db.similarity_search(
    "I would love to see you", filter={"source": "book 1"}
)

# you can also use lists in the input's metadata and then select things that match an item in the list. This is useful for categories like below:
book_category_similar_docs = clarifai_vector_db.similarity_search(
    "I would love to see you", filter={"category": ["books"]}
)


# ## From Documents
# Create a Clarifai vectorstore from a list of Documents. This section will upload each document with its respective metadata to a Clarifai Application. The Clarifai Application can then be used for semantic search to find relevant documents.

# In[ ]:


loader = TextLoader("your_local_file_path.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)


# In[10]:


USER_ID = "USERNAME_ID"
APP_ID = "APPLICATION_ID"
NUMBER_OF_DOCS = 4


# Create a clarifai vector DB class and ingest all your documents into clarifai App.

# In[ ]:


clarifai_vector_db = Clarifai.from_documents(
    user_id=USER_ID,
    app_id=APP_ID,
    documents=docs,
    number_of_docs=NUMBER_OF_DOCS,
)


# In[ ]:


docs = clarifai_vector_db.similarity_search("Texts related to population")
docs


# ## From existing App
# Within Clarifai we have great tools for adding data to applications (essentially projects) via API or UI. Most users will already have done that before interacting with LangChain so this example will use the data in an existing app to perform searches. Check out our [API docs](https://docs.clarifai.com/api-guide/data/create-get-update-delete) and [UI docs](https://docs.clarifai.com/portal-guide/data). The Clarifai Application can then be used for semantic search to find relevant documents.

# In[7]:


USER_ID = "USERNAME_ID"
APP_ID = "APPLICATION_ID"
NUMBER_OF_DOCS = 4


# In[9]:


clarifai_vector_db = Clarifai(
    user_id=USER_ID,
    app_id=APP_ID,
    number_of_docs=NUMBER_OF_DOCS,
)


# In[ ]:


docs = clarifai_vector_db.similarity_search(
    "Texts related to ammuniction and president wilson"
)


# In[51]:


docs[0].page_content


# In[ ]:




