#!/usr/bin/env python
# coding: utf-8

# # Google Cloud SQL for MySQL
# 
# > [Cloud SQL](https://cloud.google.com/sql) is a fully managed relational database service that offers high performance, seamless integration, and impressive scalability. It offers [MySQL](https://cloud.google.com/sql/mysql), [PostgreSQL](https://cloud.google.com/sql/postgresql), and [SQL Server](https://cloud.google.com/sql/sqlserver) database engines. Extend your database application to build AI-powered experiences leveraging Cloud SQL's Langchain integrations.
# 
# This notebook goes over how to use [Cloud SQL for MySQL](https://cloud.google.com/sql/mysql) to [save, load and delete langchain documents](/docs/how_to#document-loaders) with `MySQLLoader` and `MySQLDocumentSaver`.
# 
# Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-cloud-sql-mysql-python/).
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-cloud-sql-mysql-python/blob/main/docs/document_loader.ipynb)

# ## Before You Begin
# 
# To run this notebook, you will need to do the following:
# 
# * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
# * [Enable the Cloud SQL Admin API.](https://console.cloud.google.com/marketplace/product/google/sqladmin.googleapis.com)
# * [Create a Cloud SQL for MySQL instance](https://cloud.google.com/sql/docs/mysql/create-instance)
# * [Create a Cloud SQL database](https://cloud.google.com/sql/docs/mysql/create-manage-databases)
# * [Add an IAM database user to the database](https://cloud.google.com/sql/docs/mysql/add-manage-iam-users#creating-a-database-user) (Optional)
# 
# After confirmed access to database in the runtime environment of this notebook, filling the following values and run the cell before running example scripts.

# In[ ]:


# @markdown Please fill in the both the Google Cloud region and name of your Cloud SQL instance.
REGION = "us-central1"  # @param {type:"string"}
INSTANCE = "test-instance"  # @param {type:"string"}

# @markdown Please specify a database and a table for demo purpose.
DATABASE = "test"  # @param {type:"string"}
TABLE_NAME = "test-default"  # @param {type:"string"}


# ### 🦜🔗 Library Installation
# 
# The integration lives in its own `langchain-google-cloud-sql-mysql` package, so we need to install it.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -upgrade --quiet langchain-google-cloud-sql-mysql')


# **Colab only**: Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

# In[ ]:


# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)


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


# ### 🔐 Authentication
# 
# Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
# 
# - If you are using Colab to run this notebook, use the cell below and continue.
# - If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

# In[ ]:


from google.colab import auth

auth.authenticate_user()


# ## Basic Usage

# ### MySQLEngine Connection Pool
# 
# Before saving or loading documents from MySQL table, we need first configures a connection pool to Cloud SQL database. The `MySQLEngine` configures a connection pool to your Cloud SQL database, enabling successful connections from your application and following industry best practices.
# 
# To create a `MySQLEngine` using `MySQLEngine.from_instance()` you need to provide only 4 things:
# 
# 1. `project_id` : Project ID of the Google Cloud Project where the Cloud SQL instance is located.
# 2. `region` : Region where the Cloud SQL instance is located.
# 3. `instance` : The name of the Cloud SQL instance.
# 4. `database` : The name of the database to connect to on the Cloud SQL instance.
# 
# By default, [IAM database authentication](https://cloud.google.com/sql/docs/mysql/iam-authentication#iam-db-auth) will be used as the method of database authentication. This library uses the IAM principal belonging to the [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) sourced from the envionment.
# 
# For more informatin on IAM database authentication please see:
# 
# * [Configure an instance for IAM database authentication](https://cloud.google.com/sql/docs/mysql/create-edit-iam-instances)
# * [Manage users with IAM database authentication](https://cloud.google.com/sql/docs/mysql/add-manage-iam-users)
# 
# Optionally, [built-in database authentication](https://cloud.google.com/sql/docs/mysql/built-in-authentication) using a username and password to access the Cloud SQL database can also be used. Just provide the optional `user` and `password` arguments to `MySQLEngine.from_instance()`:
# 
# * `user` : Database user to use for built-in database authentication and login
# * `password` : Database password to use for built-in database authentication and login.

# In[ ]:


from langchain_google_cloud_sql_mysql import MySQLEngine

engine = MySQLEngine.from_instance(
    project_id=PROJECT_ID, region=REGION, instance=INSTANCE, database=DATABASE
)


# ### Initialize a table
# 
# Initialize a table of default schema via `MySQLEngine.init_document_table(<table_name>)`. Table Columns:
# 
# - page_content (type: text)
# - langchain_metadata (type: JSON)
# 
# `overwrite_existing=True` flag means the newly initialized table will replace any existing table of the same name.

# In[ ]:


engine.init_document_table(TABLE_NAME, overwrite_existing=True)


# ### Save documents
# 
# Save langchain documents with `MySQLDocumentSaver.add_documents(<documents>)`. To initialize `MySQLDocumentSaver` class you need to provide 2 things:
# 
# 1. `engine` - An instance of a `MySQLEngine` engine.
# 2. `table_name` - The name of the table within the Cloud SQL database to store langchain documents.

# In[ ]:


from langchain_core.documents import Document
from langchain_google_cloud_sql_mysql import MySQLDocumentSaver

test_docs = [
    Document(
        page_content="Apple Granny Smith 150 0.99 1",
        metadata={"fruit_id": 1},
    ),
    Document(
        page_content="Banana Cavendish 200 0.59 0",
        metadata={"fruit_id": 2},
    ),
    Document(
        page_content="Orange Navel 80 1.29 1",
        metadata={"fruit_id": 3},
    ),
]
saver = MySQLDocumentSaver(engine=engine, table_name=TABLE_NAME)
saver.add_documents(test_docs)


# ### Load documents

# Load langchain documents with `MySQLLoader.load()` or `MySQLLoader.lazy_load()`. `lazy_load` returns a generator that only queries database during the iteration. To initialize `MySQLLoader` class you need to provide:
# 
# 1. `engine` - An instance of a `MySQLEngine` engine.
# 2. `table_name` - The name of the table within the Cloud SQL database to store langchain documents.

# In[ ]:


from langchain_google_cloud_sql_mysql import MySQLLoader

loader = MySQLLoader(engine=engine, table_name=TABLE_NAME)
docs = loader.lazy_load()
for doc in docs:
    print("Loaded documents:", doc)


# ### Load documents via query

# Other than loading documents from a table, we can also choose to load documents from a view generated from a SQL query. For example:

# In[ ]:


from langchain_google_cloud_sql_mysql import MySQLLoader

loader = MySQLLoader(
    engine=engine,
    query=f"select * from `{TABLE_NAME}` where JSON_EXTRACT(langchain_metadata, '$.fruit_id') = 1;",
)
onedoc = loader.load()
onedoc


# The view generated from SQL query can have different schema than default table. In such cases, the behavior of MySQLLoader is the same as loading from table with non-default schema. Please refer to section [Load documents with customized document page content & metadata](#load-documents-with-customized-document-page-content--metadata).

# ### Delete documents

# Delete a list of langchain documents from MySQL table with `MySQLDocumentSaver.delete(<documents>)`.
# 
# For table with default schema (page_content, langchain_metadata), the deletion criteria is:
# 
# A `row` should be deleted if there exists a `document` in the list, such that
# 
# - `document.page_content` equals `row[page_content]`
# - `document.metadata` equals `row[langchain_metadata]`

# In[ ]:


from langchain_google_cloud_sql_mysql import MySQLLoader

loader = MySQLLoader(engine=engine, table_name=TABLE_NAME)
docs = loader.load()
print("Documents before delete:", docs)
saver.delete(onedoc)
print("Documents after delete:", loader.load())


# ## Advanced Usage

# ### Load documents with customized document page content & metadata

# First we prepare an example table with non-default schema, and populate it with some arbitrary data.

# In[ ]:


import sqlalchemy

with engine.connect() as conn:
    conn.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS `{TABLE_NAME}`"))
    conn.commit()
    conn.execute(
        sqlalchemy.text(
            f"""
            CREATE TABLE IF NOT EXISTS `{TABLE_NAME}`(
                fruit_id INT AUTO_INCREMENT PRIMARY KEY,
                fruit_name VARCHAR(100) NOT NULL,
                variety VARCHAR(50),
                quantity_in_stock INT NOT NULL,
                price_per_unit DECIMAL(6,2) NOT NULL,
                organic TINYINT(1) NOT NULL
            )
            """
        )
    )
    conn.execute(
        sqlalchemy.text(
            f"""
            INSERT INTO `{TABLE_NAME}` (fruit_name, variety, quantity_in_stock, price_per_unit, organic)
            VALUES
                ('Apple', 'Granny Smith', 150, 0.99, 1),
                ('Banana', 'Cavendish', 200, 0.59, 0),
                ('Orange', 'Navel', 80, 1.29, 1);
            """
        )
    )
    conn.commit()


# If we still load langchain documents with default parameters of `MySQLLoader` from this example table, the `page_content` of loaded documents will be the first column of the table, and `metadata` will be consisting of key-value pairs of all the other columns.

# In[ ]:


loader = MySQLLoader(
    engine=engine,
    table_name=TABLE_NAME,
)
loader.load()


# We can specify the content and metadata we want to load by setting the `content_columns` and `metadata_columns` when initializing the `MySQLLoader`.
# 
# 1. `content_columns`: The columns to write into the `page_content` of the document.
# 2. `metadata_columns`: The columns to write into the `metadata` of the document.
# 
# For example here, the values of columns in `content_columns` will be joined together into a space-separated string, as `page_content` of loaded documents, and `metadata` of loaded documents will only contain key-value pairs of columns specified in `metadata_columns`.

# In[ ]:


loader = MySQLLoader(
    engine=engine,
    table_name=TABLE_NAME,
    content_columns=[
        "variety",
        "quantity_in_stock",
        "price_per_unit",
        "organic",
    ],
    metadata_columns=["fruit_id", "fruit_name"],
)
loader.load()


# ### Save document with customized page content & metadata

# In order to save langchain document into table with customized metadata fields. We need first create such a table via `MySQLEngine.init_document_table()`, and specify the list of `metadata_columns` we want it to have. In this example, the created table will have table columns:
# 
# - description (type: text): for storing fruit description.
# - fruit_name (type text): for storing fruit name.
# - organic (type tinyint(1)): to tell if the fruit is organic.
# - other_metadata (type: JSON): for storing other metadata information of the fruit.
# 
# We can use the following parameters with `MySQLEngine.init_document_table()` to create the table:
# 
# 1. `table_name`: The name of the table within the Cloud SQL database to store langchain documents.
# 2. `metadata_columns`: A list of `sqlalchemy.Column` indicating the list of metadata columns we need.
# 3. `content_column`: The name of column to store `page_content` of langchain document. Default: `page_content`.
# 4. `metadata_json_column`: The name of JSON column to store extra `metadata` of langchain document. Default: `langchain_metadata`.

# In[ ]:


engine.init_document_table(
    TABLE_NAME,
    metadata_columns=[
        sqlalchemy.Column(
            "fruit_name",
            sqlalchemy.UnicodeText,
            primary_key=False,
            nullable=True,
        ),
        sqlalchemy.Column(
            "organic",
            sqlalchemy.Boolean,
            primary_key=False,
            nullable=True,
        ),
    ],
    content_column="description",
    metadata_json_column="other_metadata",
    overwrite_existing=True,
)


# Save documents with `MySQLDocumentSaver.add_documents(<documents>)`. As you can see in this example, 
# 
# - `document.page_content` will be saved into `description` column.
# - `document.metadata.fruit_name` will be saved into `fruit_name` column.
# - `document.metadata.organic` will be saved into `organic` column.
# - `document.metadata.fruit_id` will be saved into `other_metadata` column in JSON format.

# In[ ]:


test_docs = [
    Document(
        page_content="Granny Smith 150 0.99",
        metadata={"fruit_id": 1, "fruit_name": "Apple", "organic": 1},
    ),
]
saver = MySQLDocumentSaver(
    engine=engine,
    table_name=TABLE_NAME,
    content_column="description",
    metadata_json_column="other_metadata",
)
saver.add_documents(test_docs)


# In[ ]:


with engine.connect() as conn:
    result = conn.execute(sqlalchemy.text(f"select * from `{TABLE_NAME}`;"))
    print(result.keys())
    print(result.fetchall())


# ### Delete documents with customized page content & metadata

# We can also delete documents from table with customized metadata columns via `MySQLDocumentSaver.delete(<documents>)`. The deletion criteria is:
# 
# A `row` should be deleted if there exists a `document` in the list, such that
# 
# - `document.page_content` equals `row[page_content]`
# - For every metadata field `k` in `document.metadata`
#     - `document.metadata[k]` equals `row[k]` or `document.metadata[k]` equals `row[langchain_metadata][k]`
# - There no extra metadata field presents in `row` but not in `document.metadata`.
# 
# 

# In[ ]:


loader = MySQLLoader(engine=engine, table_name=TABLE_NAME)
docs = loader.load()
print("Documents before delete:", docs)
saver.delete(docs)
print("Documents after delete:", loader.load())

