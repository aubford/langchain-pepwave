#!/usr/bin/env python
# coding: utf-8

# # Snowflake
# 
# This notebooks goes over how to load documents from Snowflake

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  snowflake-connector-python')


# In[3]:


import settings as s
from langchain_community.document_loaders import SnowflakeLoader


# In[ ]:


QUERY = "select text, survey_id from CLOUD_DATA_SOLUTIONS.HAPPY_OR_NOT.OPEN_FEEDBACK limit 10"
snowflake_loader = SnowflakeLoader(
    query=QUERY,
    user=s.SNOWFLAKE_USER,
    password=s.SNOWFLAKE_PASS,
    account=s.SNOWFLAKE_ACCOUNT,
    warehouse=s.SNOWFLAKE_WAREHOUSE,
    role=s.SNOWFLAKE_ROLE,
    database=s.SNOWFLAKE_DATABASE,
    schema=s.SNOWFLAKE_SCHEMA,
)
snowflake_documents = snowflake_loader.load()
print(snowflake_documents)


# In[ ]:


import settings as s
from snowflakeLoader import SnowflakeLoader

QUERY = "select text, survey_id as source from CLOUD_DATA_SOLUTIONS.HAPPY_OR_NOT.OPEN_FEEDBACK limit 10"
snowflake_loader = SnowflakeLoader(
    query=QUERY,
    user=s.SNOWFLAKE_USER,
    password=s.SNOWFLAKE_PASS,
    account=s.SNOWFLAKE_ACCOUNT,
    warehouse=s.SNOWFLAKE_WAREHOUSE,
    role=s.SNOWFLAKE_ROLE,
    database=s.SNOWFLAKE_DATABASE,
    schema=s.SNOWFLAKE_SCHEMA,
    metadata_columns=["source"],
)
snowflake_documents = snowflake_loader.load()
print(snowflake_documents)

