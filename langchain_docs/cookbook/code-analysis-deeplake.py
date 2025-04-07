#!/usr/bin/env python
# coding: utf-8

# # Use LangChain, GPT and Activeloop's Deep Lake to work with code base
# In this tutorial, we are going to use Langchain + Activeloop's Deep Lake with GPT to analyze the code base of the LangChain itself. 

# ## Design

# 1. Prepare data:
#    1. Upload all python project files using the `langchain_community.document_loaders.TextLoader`. We will call these files the **documents**.
#    2. Split all documents to chunks using the `langchain_text_splitters.CharacterTextSplitter`.
#    3. Embed chunks and upload them into the DeepLake using `langchain.embeddings.openai.OpenAIEmbeddings` and `langchain_community.vectorstores.DeepLake`
# 2. Question-Answering:
#    1. Build a chain from `langchain.chat_models.ChatOpenAI` and `langchain.chains.ConversationalRetrievalChain`
#    2. Prepare questions.
#    3. Get answers running the chain.
# 

# ## Implementation

# ### Integration preparations

# We need to set up keys for external services and install necessary python libraries.

# In[ ]:


#!python3 -m pip install --upgrade langchain langchain-deeplake openai


# Set up OpenAI embeddings, Deep Lake multi-modal vector store api and authenticate. 
# 
# For full documentation of Deep Lake please follow https://docs.activeloop.ai/ and API reference https://docs.deeplake.ai/en/latest/

# In[1]:


import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()
# Please manually enter OpenAI Key


# Authenticate into Deep Lake if you want to create your own dataset and publish it. You can get an API key from the platform at [app.activeloop.ai](https://app.activeloop.ai)

# In[2]:


activeloop_token = getpass("Activeloop Token:")
os.environ["ACTIVELOOP_TOKEN"] = activeloop_token


# ### Prepare data 

# Load all repository files. Here we assume this notebook is downloaded as the part of the langchain fork and we work with the python files of the `langchain` repo.
# 
# If you want to use files from different repo, change `root_dir` to the root dir of your repo.

# In[10]:


get_ipython().system('ls "../../../../../../libs"')


# In[11]:


from langchain_community.document_loaders import TextLoader

root_dir = "../../../../../../libs"

docs = []
for dirpath, dirnames, filenames in os.walk(root_dir):
    for file in filenames:
        if file.endswith(".py") and "*venv/" not in dirpath:
            try:
                loader = TextLoader(os.path.join(dirpath, file), encoding="utf-8")
                docs.extend(loader.load_and_split())
            except Exception:
                pass
print(f"{len(docs)}")


# Then, chunk the files

# In[12]:


from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(docs)
print(f"{len(texts)}")


# Then embed chunks and upload them to the DeepLake.
# 
# This can take several minutes. 

# In[13]:


from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
embeddings


# In[ ]:


from langchain_deeplake.vectorstores import DeeplakeVectorStore

username = "<USERNAME_OR_ORG>"


db = DeeplakeVectorStore.from_documents(
    documents=texts,
    embedding=embeddings,
    dataset_path=f"hub://{username}/langchain-code",
    overwrite=True,
)
db


# ### Question Answering
# First load the dataset, construct the retriever, then construct the Conversational Chain

# In[ ]:


db = DeeplakeVectorStore(
    dataset_path=f"hub://{username}/langchain-code",
    read_only=True,
    embedding_function=embeddings,
)


# In[18]:


retriever = db.as_retriever()
retriever.search_kwargs["distance_metric"] = "cos"
retriever.search_kwargs["fetch_k"] = 20
retriever.search_kwargs["maximal_marginal_relevance"] = True
retriever.search_kwargs["k"] = 20


# In[20]:


from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-3.5-turbo-0613")  # 'ada' 'gpt-3.5-turbo-0613' 'gpt-4',
qa = RetrievalQA.from_llm(model, retriever=retriever)


# In[32]:


questions = [
    "What is the class hierarchy?",
    "What classes are derived from the Chain class?",
    "What kind of retrievers does LangChain have?",
]
chat_history = []
qa_dict = {}

for question in questions:
    result = qa({"question": question, "chat_history": chat_history})
    chat_history.append((question, result["answer"]))
    qa_dict[question] = result["answer"]
    print(f"-> **Question**: {question} \n")
    print(f"**Answer**: {result['answer']} \n")


# In[31]:


qa_dict


# In[33]:


print(qa_dict["What is the class hierarchy?"])


# In[34]:


print(qa_dict["What classes are derived from the Chain class?"])


# In[35]:


print(qa_dict["What kind of retrievers does LangChain have?"])

