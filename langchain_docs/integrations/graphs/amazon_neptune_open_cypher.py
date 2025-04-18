#!/usr/bin/env python
# coding: utf-8

# # Amazon Neptune with Cypher
# 
# >[Amazon Neptune](https://aws.amazon.com/neptune/) is a high-performance graph analytics and serverless database for superior scalability and availability.
# >
# >This example shows the QA chain that queries the `Neptune` graph database using `openCypher` and returns a human-readable response.
# >
# >[Cypher](https://en.wikipedia.org/wiki/Cypher_(query_language)) is a declarative graph query language that allows for expressive and efficient data querying in a property graph.
# >
# >[openCypher](https://opencypher.org/) is an open-source implementation of Cypher.# Neptune Open Cypher QA Chain
# This QA chain queries Amazon Neptune using openCypher and returns human readable response
# 
# LangChain supports both [Neptune Database](https://docs.aws.amazon.com/neptune/latest/userguide/intro.html) and [Neptune Analytics](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/what-is-neptune-analytics.html) with `create_neptune_opencypher_qa_chain`.
# 
# Neptune Database is a serverless graph database designed for optimal scalability and availability. It provides a solution for graph database workloads that need to scale to 100,000 queries per second, Multi-AZ high availability, and multi-Region deployments. You can use Neptune Database for social networking, fraud alerting, and Customer 360 applications.
# 
# Neptune Analytics is an analytics database engine that can quickly analyze large amounts of graph data in memory to get insights and find trends. Neptune Analytics is a solution for quickly analyzing existing graph databases or graph datasets stored in a data lake. It uses popular graph analytic algorithms and low-latency analytic queries.
# 
# 
# 
# ## Using Neptune Database

# In[ ]:


from langchain_aws.graphs import NeptuneGraph

host = "<neptune-host>"
port = 8182
use_https = True

graph = NeptuneGraph(host=host, port=port, use_https=use_https)


# ### Using Neptune Analytics

# In[ ]:


from langchain_aws.graphs import NeptuneAnalyticsGraph

graph = NeptuneAnalyticsGraph(graph_identifier="<neptune-analytics-graph-id>")


# ## Using the Neptune openCypher QA Chain
# 
# This QA chain queries the Neptune graph database using openCypher and returns a human-readable response.

# In[12]:


from langchain_aws import ChatBedrockConverse
from langchain_aws.chains import create_neptune_opencypher_qa_chain

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
llm = ChatBedrockConverse(
    model=MODEL_ID,
    temperature=0,
)

chain = create_neptune_opencypher_qa_chain(llm=llm, graph=graph)

result = chain.invoke("How many outgoing routes does the Austin airport have?")
print(result["result"].content)


# ### Adding Message History
# 
# The Neptune openCypher QA chain has the ability to be wrapped by [`RunnableWithMessageHistory`](https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html#langchain_core.runnables.history.RunnableWithMessageHistory). This adds message history to the chain, allowing us to create a chatbot that retains conversation state across multiple invocations.
# 
# To start, we need a way to store and load the message history. For this purpose, each thread will be created as an instance of [`InMemoryChatMessageHistory`](https://python.langchain.com/api_reference/core/chat_history/langchain_core.chat_history.InMemoryChatMessageHistory.html), and stored into a dictionary for repeated access.
# 
# (Also see: https://python.langchain.com/docs/versions/migrating_memory/chat_history/#chatmessagehistory)

# In[ ]:


from langchain_core.chat_history import InMemoryChatMessageHistory

chats_by_session_id = {}


def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history


# Now, the QA chain and message history storage can be used to create the new `RunnableWithMessageHistory`. Note that we must set `query` as the input key to match the format expected by the base chain.

# In[ ]:


from langchain_core.runnables.history import RunnableWithMessageHistory

runnable_with_history = RunnableWithMessageHistory(
    chain,
    get_chat_history,
    input_messages_key="query",
)


# Before invoking the chain, a unique `session_id` needs to be generated for the conversation that the new `InMemoryChatMessageHistory` will remember.

# In[ ]:


import uuid

session_id = uuid.uuid4()


# Finally, invoke the message history enabled chain with the `session_id`.

# In[8]:


result = runnable_with_history.invoke(
    {"query": "How many destinations can I fly to directly from Austin airport?"},
    config={"configurable": {"session_id": session_id}},
)
print(result["result"].content)


# As the chain continues to be invoked with the same `session_id`, responses will be returned in the context of previous queries in the conversation.
# 

# In[9]:


result = runnable_with_history.invoke(
    {"query": "Out of those destinations, how many are in Europe?"},
    config={"configurable": {"session_id": session_id}},
)
print(result["result"].content)


# In[10]:


result = runnable_with_history.invoke(
    {"query": "Give me the codes and names of those airports."},
    config={"configurable": {"session_id": session_id}},
)
print(result["result"].content)

