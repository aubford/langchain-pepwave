#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Box
---
# # BoxRetriever
# 
# This will help you getting started with the Box [retriever](/docs/concepts/retrievers). For detailed documentation of all BoxRetriever features and configurations head to the [API reference](https://python.langchain.com/api_reference/box/retrievers/langchain_box.retrievers.box.BoxRetriever.html).
# 
# # Overview
# 
# The `BoxRetriever` class helps you get your unstructured content from Box in Langchain's `Document` format. You can do this by searching for files based on a full-text search or using Box AI to retrieve a `Document` containing the result of an AI query against files. This requires including a `List[str]` containing Box file ids, i.e. `["12345","67890"]` 
# 
# :::info
# Box AI requires an Enterprise Plus license
# :::
# 
# Files without a text representation will be skipped.
# 
# ### Integration details
# 
# 1: Bring-your-own data (i.e., index and search a custom corpus of documents):
# 
# | Retriever | Self-host | Cloud offering | Package |
# | :--- | :--- | :---: | :---: |
# [BoxRetriever](https://python.langchain.com/api_reference/box/retrievers/langchain_box.retrievers.box.BoxRetriever.html) | ❌ | ✅ | langchain-box |
# 
# ## Setup
# 
# In order to use the Box package, you will need a few things:
# 
# * A Box account — If you are not a current Box customer or want to test outside of your production Box instance, you can use a [free developer account](https://account.box.com/signup/n/developer#ty9l3).
# * [A Box app](https://developer.box.com/guides/getting-started/first-application/) — This is configured in the [developer console](https://account.box.com/developers/console), and for Box AI, must have the `Manage AI` scope enabled. Here you will also select your authentication method
# * The app must be [enabled by the administrator](https://developer.box.com/guides/authorization/custom-app-approval/#manual-approval). For free developer accounts, this is whomever signed up for the account.
# 
# ### Credentials
# 
# For these examples, we will use [token authentication](https://developer.box.com/guides/authentication/tokens/developer-tokens). This can be used with any [authentication method](https://developer.box.com/guides/authentication/). Just get the token with whatever methodology. If you want to learn more about how to use other authentication types with `langchain-box`, visit the [Box provider](/docs/integrations/providers/box) document.

# In[2]:


import getpass
import os

box_developer_token = getpass.getpass("Enter your Box Developer Token: ")


# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[3]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# This retriever lives in the `langchain-box` package:

# In[4]:


get_ipython().run_line_magic('pip', 'install -qU langchain-box')


# ## Instantiation
# 
# Now we can instantiate our retriever:
# 
# ## Search

# In[5]:


from langchain_box import BoxRetriever

retriever = BoxRetriever(box_developer_token=box_developer_token)


# For more granular search, we offer a series of options to help you filter down the results. This uses the `langchain_box.utilities.SearchOptions` in conjunction with the `langchain_box.utilities.SearchTypeFilter` and `langchain_box.utilities.DocumentFiles` enums to filter on things like created date, which part of the file to search, and even to limit the search scope to a specific folder. 
# 
# For more information, check out the [API reference](https://python.langchain.com/v0.2/api_reference/box/utilities/langchain_box.utilities.box.SearchOptions.html).

# In[6]:


from langchain_box.utilities import BoxSearchOptions, DocumentFiles, SearchTypeFilter

box_folder_id = "260931903795"

box_search_options = BoxSearchOptions(
    ancestor_folder_ids=[box_folder_id],
    search_type_filter=[SearchTypeFilter.FILE_CONTENT],
    created_date_range=["2023-01-01T00:00:00-07:00", "2024-08-01T00:00:00-07:00,"],
    k=200,
    size_range=[1, 1000000],
    updated_data_range=None,
)

retriever = BoxRetriever(
    box_developer_token=box_developer_token, box_search_options=box_search_options
)

retriever.invoke("AstroTech Solutions")


# ## Box AI

# In[7]:


from langchain_box import BoxRetriever

box_file_ids = ["1514555423624", "1514553902288"]

retriever = BoxRetriever(
    box_developer_token=box_developer_token, box_file_ids=box_file_ids
)


# ## Usage

# In[8]:


query = "What was the most expensive item purchased"

retriever.invoke(query)


# ## Citations
# 
# With Box AI and the `BoxRetriever`, you can return the answer to your prompt, return the citations used by Box to get that answer, or both. No matter how you choose to use Box AI, the retriever returns a `List[Document]` object. We offer this flexibility with two `bool` arguments, `answer` and `citations`. Answer defaults to `True` and citations defaults to `False`, do you can omit both if you just want the answer. If you want both, you can just include `citations=True` and if you only want citations, you would include `answer=False` and `citations=True`
# 
# ### Get both

# In[11]:


retriever = BoxRetriever(
    box_developer_token=box_developer_token, box_file_ids=box_file_ids, citations=True
)

retriever.invoke(query)


# ### Citations only

# In[12]:


retriever = BoxRetriever(
    box_developer_token=box_developer_token,
    box_file_ids=box_file_ids,
    answer=False,
    citations=True,
)

retriever.invoke(query)


# ## Use within a chain
# 
# Like other retrievers, BoxRetriever can be incorporated into LLM applications via [chains](/docs/how_to/sequence/).
# 
# We will need a LLM or chat model:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm" />
# 

# In[7]:


openai_key = getpass.getpass("Enter your OpenAI key: ")


# In[8]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_key)


# In[42]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

box_search_options = BoxSearchOptions(
    ancestor_folder_ids=[box_folder_id],
    search_type_filter=[SearchTypeFilter.FILE_CONTENT],
    created_date_range=["2023-01-01T00:00:00-07:00", "2024-08-01T00:00:00-07:00,"],
    k=200,
    size_range=[1, 1000000],
    updated_data_range=None,
)

retriever = BoxRetriever(
    box_developer_token=box_developer_token, box_search_options=box_search_options
)

context = "You are a finance professional that handles invoices and purchase orders."
question = "Show me all the items purchased from AstroTech Solutions"

prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided.

    Context: {context}

    Question: {question}"""
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# In[43]:


chain.invoke(question)


# ## Use as an agent tool
# 
# Like other retrievers, BoxRetriever can be also be added to a LangGraph agent as a tool.

# In[ ]:


pip install -U langsmith


# In[27]:


from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool


# In[34]:


box_search_options = BoxSearchOptions(
    ancestor_folder_ids=[box_folder_id],
    search_type_filter=[SearchTypeFilter.FILE_CONTENT],
    created_date_range=["2023-01-01T00:00:00-07:00", "2024-08-01T00:00:00-07:00,"],
    k=200,
    size_range=[1, 1000000],
    updated_data_range=None,
)

retriever = BoxRetriever(
    box_developer_token=box_developer_token, box_search_options=box_search_options
)

box_search_tool = create_retriever_tool(
    retriever,
    "box_search_tool",
    "This tool is used to search Box and retrieve documents that match the search criteria",
)
tools = [box_search_tool]


# In[35]:


prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages

llm = ChatOpenAI(temperature=0, openai_api_key=openai_key)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)


# In[36]:


result = agent_executor.invoke(
    {
        "input": "list the items I purchased from AstroTech Solutions from most expensive to least expensive"
    }
)


# In[37]:


print(f"result {result['output']}")


# ## Extra fields
# 
# All Box connectors offer the ability to select additional fields from the Box `FileFull` object to return as custom LangChain metadata. Each object accepts an optional `List[str]` called `extra_fields` containing the json key from the return object, like `extra_fields=["shared_link"]`. 
# 
# The connector will add this field to the list of fields the integration needs to function and then add the results to the metadata returned in the `Document` or `Blob`, like `"metadata" : { "source" : "source, "shared_link" : "shared_link" }`. If the field is unavailable for that file, it will be returned as an empty string, like `"shared_link" : ""`.

# ## API reference
# 
# For detailed documentation of all BoxRetriever features and configurations head to the [API reference](https://python.langchain.com/api_reference/box/retrievers/langchain_box.retrievers.box.BoxRetriever.html).
# 
# 
# ## Help
# 
# If you have questions, you can check out our [developer documentation](https://developer.box.com) or reach out to use in our [developer community](https://community.box.com).
