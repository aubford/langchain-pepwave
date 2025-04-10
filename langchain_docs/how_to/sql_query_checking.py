#!/usr/bin/env python
# coding: utf-8

# # How to do query validation as part of SQL question-answering
# 
# Perhaps the most error-prone part of any SQL chain or agent is writing valid and safe SQL queries. In this guide we'll go over some strategies for validating our queries and handling invalid queries.
# 
# We will cover: 
# 
# 1. Appending a "query validator" step to the query generation;
# 2. Prompt engineering to reduce the incidence of errors.
# 
# ## Setup
# 
# First, get required packages and set environment variables:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain langchain-community langchain-openai')


# In[ ]:


# Uncomment the below to use LangSmith. Not required.
# import os
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
# os.environ["LANGSMITH_TRACING"] = "true"


# The below example will use a SQLite connection with Chinook database. Follow [these installation steps](https://database.guide/2-sample-databases-sqlite/) to create `Chinook.db` in the same directory as this notebook:
# 
# * Save [this file](https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql) as `Chinook_Sqlite.sql`
# * Run `sqlite3 Chinook.db`
# * Run `.read Chinook_Sqlite.sql`
# * Test `SELECT * FROM Artist LIMIT 10;`
# 
# Now, `Chinook.db` is in our directory and we can interface with it using the SQLAlchemy-driven `SQLDatabase` class:

# In[1]:


from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///Chinook.db")
print(db.dialect)
print(db.get_usable_table_names())
print(db.run("SELECT * FROM Artist LIMIT 10;"))


# ## Query checker
# 
# Perhaps the simplest strategy is to ask the model itself to check the original query for common mistakes. Suppose we have the following SQL query chain:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm" />
# 

# In[3]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI()


# In[4]:


from langchain.chains import create_sql_query_chain

chain = create_sql_query_chain(llm, db)


# And we want to validate its outputs. We can do so by extending the chain with a second prompt and model call:

# In[5]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

system = """Double check the user's {dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query.
If there are no mistakes, just reproduce the original query with no further commentary.

Output the final SQL query only."""
prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", "{query}")]
).partial(dialect=db.dialect)
validation_chain = prompt | llm | StrOutputParser()

full_chain = {"query": chain} | validation_chain


# In[10]:


query = full_chain.invoke(
    {
        "question": "What's the average Invoice from an American customer whose Fax is missing since 2003 but before 2010"
    }
)
print(query)


# Note how we can see both steps of the chain in the [Langsmith trace](https://smith.langchain.com/public/8a743295-a57c-4e4c-8625-bc7e36af9d74/r).

# In[38]:


db.run(query)


# The obvious downside of this approach is that we need to make two model calls instead of one to generate our query. To get around this we can try to perform the query generation and query check in a single model invocation:

# In[13]:


system = """You are a {dialect} expert. Given an input question, create a syntactically correct {dialect} query to run.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per {dialect}. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date('now') function to get the current date, if the question involves "today".

Only use the following tables:
{table_info}

Write an initial draft of the query. Then double check the {dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

Use format:

First draft: <<FIRST_DRAFT_QUERY>>
Final answer: <<FINAL_ANSWER_QUERY>>
"""
prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", "{input}")]
).partial(dialect=db.dialect)


def parse_final_answer(output: str) -> str:
    return output.split("Final answer: ")[1]


chain = create_sql_query_chain(llm, db, prompt=prompt) | parse_final_answer
prompt.pretty_print()


# In[14]:


query = chain.invoke(
    {
        "question": "What's the average Invoice from an American customer whose Fax is missing since 2003 but before 2010"
    }
)
print(query)


# In[47]:


db.run(query)


# ## Human-in-the-loop
# 
# In some cases our data is sensitive enough that we never want to execute a SQL query without a human approving it first. Head to the [Tool use: Human-in-the-loop](/docs/how_to/tools_human) page to learn how to add a human-in-the-loop to any tool, chain or agent.
# 
# ## Error handling
# 
# At some point, the model will make a mistake and craft an invalid SQL query. Or an issue will arise with our database. Or the model API will go down. We'll want to add some error handling behavior to our chains and agents so that we fail gracefully in these situations, and perhaps even automatically recover. To learn about error handling with tools, head to the [Tool use: Error handling](/docs/how_to/tools_error) page.
