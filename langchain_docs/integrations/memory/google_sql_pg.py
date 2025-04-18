#!/usr/bin/env python
# coding: utf-8

# # Google SQL for PostgreSQL
# 
# > [Google Cloud SQL](https://cloud.google.com/sql) is a fully managed relational database service that offers high performance, seamless integration, and impressive scalability. It offers `MySQL`, `PostgreSQL`, and `SQL Server` database engines. Extend your database application to build AI-powered experiences leveraging Cloud SQL's Langchain integrations.
# 
# This notebook goes over how to use `Google Cloud SQL for PostgreSQL` to store chat message history with the `PostgresChatMessageHistory` class.
# 
# Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-cloud-sql-pg-python/).
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-cloud-sql-pg-python/blob/main/docs/chat_message_history.ipynb)

# ## Before You Begin
# 
# To run this notebook, you will need to do the following:
# 
#  * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
#  * [Enable the Cloud SQL Admin API.](https://console.cloud.google.com/marketplace/product/google/sqladmin.googleapis.com)
#  * [Create a Cloud SQL for PostgreSQL instance](https://cloud.google.com/sql/docs/postgres/create-instance)
#  * [Create a Cloud SQL database](https://cloud.google.com/sql/docs/mysql/create-manage-databases)
#  * [Add an IAM database user to the database](https://cloud.google.com/sql/docs/postgres/add-manage-iam-users#creating-a-database-user) (Optional)

# ### 🦜🔗 Library Installation
# The integration lives in its own `langchain-google-cloud-sql-pg` package, so we need to install it.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-google-cloud-sql-pg langchain-google-vertexai')


# **Colab only:** Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

# In[ ]:


# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)


# ### 🔐 Authentication
# Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
# 
# * If you are using Colab to run this notebook, use the cell below and continue.
# * If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

# In[1]:


from google.colab import auth

auth.authenticate_user()


# ### ☁ Set Your Google Cloud Project
# Set your Google Cloud project so that you can leverage Google Cloud resources within this notebook.
# 
# If you don't know your project ID, try the following:
# 
# * Run `gcloud config list`.
# * Run `gcloud projects list`.
# * See the support page: [Locate the project ID](https://support.google.com/googleapi/answer/7014113).

# In[ ]:


# @markdown Please fill in the value below with your Google Cloud project ID and then run the cell.

PROJECT_ID = "my-project-id"  # @param {type:"string"}

# Set the project id
get_ipython().system('gcloud config set project {PROJECT_ID}')


# ### 💡 API Enablement
# The `langchain-google-cloud-sql-pg` package requires that you [enable the Cloud SQL Admin API](https://console.cloud.google.com/flows/enableapi?apiid=sqladmin.googleapis.com) in your Google Cloud Project.

# In[3]:


# enable Cloud SQL Admin API
get_ipython().system('gcloud services enable sqladmin.googleapis.com')


# ## Basic Usage

# ### Set Cloud SQL database values
# Find your database values, in the [Cloud SQL Instances page](https://console.cloud.google.com/sql?_ga=2.223735448.2062268965.1707700487-2088871159.1707257687).

# In[4]:


# @title Set Your Values Here { display-mode: "form" }
REGION = "us-central1"  # @param {type: "string"}
INSTANCE = "my-postgresql-instance"  # @param {type: "string"}
DATABASE = "my-database"  # @param {type: "string"}
TABLE_NAME = "message_store"  # @param {type: "string"}


# ### PostgresEngine Connection Pool
# 
# One of the requirements and arguments to establish Cloud SQL as a ChatMessageHistory memory store is a `PostgresEngine` object. The `PostgresEngine`  configures a connection pool to your Cloud SQL database, enabling successful connections from your application and following industry best practices.
# 
# To create a `PostgresEngine` using `PostgresEngine.from_instance()` you need to provide only 4 things:
# 
# 1.   `project_id` : Project ID of the Google Cloud Project where the Cloud SQL instance is located.
# 1. `region` : Region where the Cloud SQL instance is located.
# 1. `instance` : The name of the Cloud SQL instance.
# 1. `database` : The name of the database to connect to on the Cloud SQL instance.
# 
# By default, [IAM database authentication](https://cloud.google.com/sql/docs/postgres/iam-authentication#iam-db-auth) will be used as the method of database authentication. This library uses the IAM principal belonging to the [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) sourced from the envionment.
# 
# For more informatin on IAM database authentication please see:
# 
# * [Configure an instance for IAM database authentication](https://cloud.google.com/sql/docs/postgres/create-edit-iam-instances)
# * [Manage users with IAM database authentication](https://cloud.google.com/sql/docs/postgres/add-manage-iam-users)
# 
# Optionally, [built-in database authentication](https://cloud.google.com/sql/docs/postgres/built-in-authentication) using a username and password to access the Cloud SQL database can also be used. Just provide the optional `user` and `password` arguments to `PostgresEngine.from_instance()`:
# 
# * `user` : Database user to use for built-in database authentication and login
# * `password` : Database password to use for built-in database authentication and login.
# 

# In[5]:


from langchain_google_cloud_sql_pg import PostgresEngine

engine = PostgresEngine.from_instance(
    project_id=PROJECT_ID, region=REGION, instance=INSTANCE, database=DATABASE
)


# ### Initialize a table
# The `PostgresChatMessageHistory` class requires a database table with a specific schema in order to store the chat message history.
# 
# The `PostgresEngine` engine has a helper method `init_chat_history_table()` that can be used to create a table with the proper schema for you.

# In[ ]:


engine.init_chat_history_table(table_name=TABLE_NAME)


# ### PostgresChatMessageHistory
# 
# To initialize the `PostgresChatMessageHistory` class you need to provide only 3 things:
# 
# 1. `engine` - An instance of a `PostgresEngine` engine.
# 1. `session_id` - A unique identifier string that specifies an id for the session.
# 1. `table_name` : The name of the table within the Cloud SQL database to store the chat message history.

# In[10]:


from langchain_google_cloud_sql_pg import PostgresChatMessageHistory

history = PostgresChatMessageHistory.create_sync(
    engine, session_id="test_session", table_name=TABLE_NAME
)
history.add_user_message("hi!")
history.add_ai_message("whats up?")


# In[11]:


history.messages


# #### Cleaning up
# When the history of a specific session is obsolete and can be deleted, it can be done the following way.
# 
# **Note:** Once deleted, the data is no longer stored in Cloud SQL and is gone forever.

# In[12]:


history.clear()


# ## 🔗 Chaining
# 
# We can easily combine this message history class with [LCEL Runnables](/docs/how_to/message_history)
# 
# To do this we will use one of [Google's Vertex AI chat models](/docs/integrations/chat/google_vertex_ai_palm) which requires that you [enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com) in your Google Cloud Project.
# 

# In[13]:


# enable Vertex AI API
get_ipython().system('gcloud services enable aiplatform.googleapis.com')


# In[14]:


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_vertexai import ChatVertexAI


# In[15]:


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatVertexAI(project=PROJECT_ID)


# In[16]:


chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: PostgresChatMessageHistory.create_sync(
        engine,
        session_id=session_id,
        table_name=TABLE_NAME,
    ),
    input_messages_key="question",
    history_messages_key="history",
)


# In[17]:


# This is where we configure the session id
config = {"configurable": {"session_id": "test_session"}}


# In[18]:


chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config)


# In[19]:


chain_with_history.invoke({"question": "Whats my name"}, config=config)

