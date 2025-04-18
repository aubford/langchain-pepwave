#!/usr/bin/env python
# coding: utf-8

# # Xata
# 
# >[Xata](https://xata.io) is a serverless data platform, based on `PostgreSQL` and `Elasticsearch`. It provides a Python SDK for interacting with your database, and a UI for managing your data. With the `XataChatMessageHistory` class, you can use Xata databases for longer-term persistence of chat sessions.
# 
# This notebook covers:
# 
# * A simple example showing what `XataChatMessageHistory` does.
# * A more complex example using a REACT agent that answer questions based on a knowledge based or documentation (stored in Xata as a vector store) and also having a long-term searchable history of its past messages (stored in Xata as a memory store)

# ## Setup
# 
# ### Create a database
# 
# In the [Xata UI](https://app.xata.io) create a new database. You can name it whatever you want, in this notepad we'll use `langchain`. The Langchain integration can auto-create the table used for storying the memory, and this is what we'll use in this example. If you want to pre-create the table, ensure it has the right schema and set `create_table` to `False` when creating the class. Pre-creating the table saves one round-trip to the database during each session initialization.

# Let's first install our dependencies:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  xata langchain-openai langchain langchain-community')


# Next, we need to get the environment variables for Xata. You can create a new API key by visiting your [account settings](https://app.xata.io/settings). To find the database URL, go to the Settings page of the database that you have created. The database URL should look something like this: `https://demo-uni3q8.eu-west-1.xata.sh/db/langchain`.

# In[ ]:


import getpass

api_key = getpass.getpass("Xata API key: ")
db_url = input("Xata database URL (copy it from your DB settings):")


# ## Create a simple memory store
# 
# To test the memory store functionality in isolation, let's use the following code snippet:

# In[ ]:


from langchain_community.chat_message_histories import XataChatMessageHistory

history = XataChatMessageHistory(
    session_id="session-1", api_key=api_key, db_url=db_url, table_name="memory"
)

history.add_user_message("hi!")

history.add_ai_message("whats up?")


# The above code creates a session with the ID `session-1` and stores two messages in it. After running the above, if you visit the Xata UI, you should see a table named `memory` and the two messages added to it.
# 
# You can retrieve the message history for a particular session with the following code:

# In[ ]:


history.messages


# ## Conversational Q&A chain on your data with memory
# 
# Let's now see a more complex example in which we combine OpenAI, the Xata Vector Store integration, and the Xata memory store integration to create a Q&A chat bot on your data, with follow-up questions and history.

# We're going to need to access the OpenAI API, so let's configure the API key:

# In[ ]:


import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# To store the documents that the chatbot will search for answers, add a table named `docs` to your `langchain` database using the Xata UI, and add the following columns:
# 
# * `content` of type "Text". This is used to store the `Document.pageContent` values.
# * `embedding` of type "Vector". Use the dimension used by the model you plan to use. In this notebook we use OpenAI embeddings, which have 1536 dimensions.

# Let's create the vector store and add some sample docs to it:

# In[ ]:


from langchain_community.vectorstores.xata import XataVectorStore
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

texts = [
    "Xata is a Serverless Data platform based on PostgreSQL",
    "Xata offers a built-in vector type that can be used to store and query vectors",
    "Xata includes similarity search",
]

vector_store = XataVectorStore.from_texts(
    texts, embeddings, api_key=api_key, db_url=db_url, table_name="docs"
)


# After running the above command, if you go to the Xata UI, you should see the documents loaded together with their embeddings in the `docs` table.

# Let's now create a ConversationBufferMemory to store the chat messages from both the user and the AI.

# In[ ]:


from uuid import uuid4

from langchain.memory import ConversationBufferMemory

chat_memory = XataChatMessageHistory(
    session_id=str(uuid4()),  # needs to be unique per user session
    api_key=api_key,
    db_url=db_url,
    table_name="memory",
)
memory = ConversationBufferMemory(
    memory_key="chat_history", chat_memory=chat_memory, return_messages=True
)


# Now it's time to create an Agent to use both the vector store and the chat memory together.

# In[ ]:


from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_openai import ChatOpenAI

tool = create_retriever_tool(
    vector_store.as_retriever(),
    "search_docs",
    "Searches and returns documents from the Xata manual. Useful when you need to answer questions about Xata.",
)
tools = [tool]

llm = ChatOpenAI(temperature=0)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)


# To test, let's tell the agent our name:

# In[ ]:


agent.run(input="My name is bob")


# Now, let's now ask the agent some questions about Xata:

# In[ ]:


agent.run(input="What is xata?")


# Notice that it answers based on the data stored in the document store. And now, let's ask a follow up question:

# In[ ]:


agent.run(input="Does it support similarity search?")


# And now let's test its memory:

# In[ ]:


agent.run(input="Did I tell you my name? What is it?")

