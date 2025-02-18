#!/usr/bin/env python
# coding: utf-8

# # Amazon Neptune with SPARQL
#
# >[Amazon Neptune](https://aws.amazon.com/neptune/) is a high-performance graph analytics and serverless database for superior scalability and availability.
# >
# >This example shows the QA chain that queries [Resource Description Framework (RDF)](https://en.wikipedia.org/wiki/Resource_Description_Framework) data
# in an `Amazon Neptune` graph database using the `SPARQL` query language and returns a human-readable response.
# >
# >[SPARQL](https://en.wikipedia.org/wiki/SPARQL) is a standard query language for `RDF` graphs.
#
#
# This example uses a `NeptuneRdfGraph` class that connects with the Neptune database and loads its schema.
# The `create_neptune_sparql_qa_chain` is used to connect the graph and LLM to ask natural language questions.
#
# This notebook demonstrates an example using organizational data.
#
# Requirements for running this notebook:
# - Neptune 1.2.x cluster accessible from this notebook
# - Kernel with Python 3.9 or higher
# - For Bedrock access, ensure IAM role has this policy
#
# ```json
# {
#         "Action": [
#             "bedrock:ListFoundationModels",
#             "bedrock:InvokeModel"
#         ],
#         "Resource": "*",
#         "Effect": "Allow"
# }
# ```
#
# - S3 bucket for staging sample data. The bucket should be in the same account/region as Neptune.

# ## Setting up
#
# ### Seed the W3C organizational data
#
# Seed the W3C organizational data, W3C org ontology plus some instances.
#
# You will need an S3 bucket in the same region and account as the Neptune cluster. Set `STAGE_BUCKET`as the name of that bucket.

# In[ ]:


STAGE_BUCKET = "<bucket-name>"


# In[ ]:


get_ipython().run_cell_magic(
    "bash",
    ' -s "$STAGE_BUCKET"',
    "\nrm -rf data\nmkdir -p data\ncd data\necho getting org ontology and sample org instances\nwget http://www.w3.org/ns/org.ttl \nwget https://raw.githubusercontent.com/aws-samples/amazon-neptune-ontology-example-blog/main/data/example_org.ttl \n\necho Copying org ttl to S3\naws s3 cp org.ttl s3://$1/org.ttl\naws s3 cp example_org.ttl s3://$1/example_org.ttl\n",
)


# We will use the `%load` magic command from the `graph-notebook` package to insert the W3C data into the Neptune graph. Before running `%load`, use `%%graph_notebook_config` to set the graph connection parameters.

# In[ ]:


get_ipython().system("pip install --upgrade --quiet graph-notebook")


# In[ ]:


get_ipython().run_line_magic("load_ext", "graph_notebook.magics")


# In[ ]:


get_ipython().run_cell_magic(
    "graph_notebook_config",
    "",
    '{\n    "host": "<neptune-endpoint>",\n    "neptune_service": "neptune-db",\n    "port": 8182,\n    "auth_mode": "<[DEFAULT|IAM]>",\n    "load_from_s3_arn": "<neptune-cluster-load-role-arn>",\n    "ssl": true,\n    "aws_region": "<region>"\n}\n',
)


# Bulk-load the org ttl - both ontology and instances.

# In[ ]:


get_ipython().run_line_magic(
    "load", "-s s3://{STAGE_BUCKET} -f turtle --store-to loadres --run"
)


# In[ ]:


get_ipython().run_line_magic(
    "load_status", "{loadres['payload']['loadId']} --errors --details"
)


# ### Setup Chain

# In[ ]:


get_ipython().system("pip install --upgrade --quiet langchain-aws")


# ** Restart kernel **

# ### Prepare an example

# In[ ]:


EXAMPLES = """

<question>
Find organizations.
</question>

<sparql>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX org: <http://www.w3.org/ns/org#> 

select ?org ?orgName where {{
    ?org rdfs:label ?orgName .
}} 
</sparql>

<question>
Find sites of an organization
</question>

<sparql>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX org: <http://www.w3.org/ns/org#> 

select ?org ?orgName ?siteName where {{
    ?org rdfs:label ?orgName .
    ?org org:hasSite/rdfs:label ?siteName . 
}} 
</sparql>

<question>
Find suborganizations of an organization
</question>

<sparql>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX org: <http://www.w3.org/ns/org#> 

select ?org ?orgName ?subName where {{
    ?org rdfs:label ?orgName .
    ?org org:hasSubOrganization/rdfs:label ?subName  .
}} 
</sparql>

<question>
Find organizational units of an organization
</question>

<sparql>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX org: <http://www.w3.org/ns/org#> 

select ?org ?orgName ?unitName where {{
    ?org rdfs:label ?orgName .
    ?org org:hasUnit/rdfs:label ?unitName . 
}} 
</sparql>

<question>
Find members of an organization. Also find their manager, or the member they report to.
</question>

<sparql>
PREFIX org: <http://www.w3.org/ns/org#> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 

select * where {{
    ?person rdf:type foaf:Person .
    ?person  org:memberOf ?org .
    OPTIONAL {{ ?person foaf:firstName ?firstName . }}
    OPTIONAL {{ ?person foaf:family_name ?lastName . }}
    OPTIONAL {{ ?person  org:reportsTo ??manager }} .
}}
</sparql>


<question>
Find change events, such as mergers and acquisitions, of an organization
</question>

<sparql>
PREFIX org: <http://www.w3.org/ns/org#> 

select ?event ?prop ?obj where {{
    ?org rdfs:label ?orgName .
    ?event rdf:type org:ChangeEvent .
    ?event org:originalOrganization ?origOrg .
    ?event org:resultingOrganization ?resultingOrg .
}}
</sparql>

"""


# ### Create the Neptune Database RDF Graph

# In[ ]:


from langchain_aws.graphs import NeptuneRdfGraph

host = "<your host>"
port = 8182  # change if different
region = "us-east-1"  # change if different
graph = NeptuneRdfGraph(host=host, port=port, use_iam_auth=True, region_name=region)

# Optionally, change the schema
# elems = graph.get_schema_elements
# change elems ...
# graph.load_schema(elems)


# ## Using the Neptune SPARQL QA Chain
#
# This QA chain queries the Neptune graph database using SPARQL and returns a human-readable response.

# In[ ]:


from langchain_aws import ChatBedrockConverse
from langchain_aws.chains import create_neptune_sparql_qa_chain

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
llm = ChatBedrockConverse(
    model_id=MODEL_ID,
    temperature=0,
)

chain = create_neptune_sparql_qa_chain(
    llm=llm,
    graph=graph,
    examples=EXAMPLES,
)

result = chain.invoke("How many organizations are in the graph?")
print(result["result"].content)


# Here are a few more prompts to try on the graph data that was ingested.
#

# In[ ]:


result = chain.invoke("Are there any mergers or acquisitions?")
print(result["result"].content)


# In[ ]:


result = chain.invoke("Find organizations.")
print(result["result"].content)


# In[ ]:


result = chain.invoke("Find sites of MegaSystems or MegaFinancial.")
print(result["result"].content)


# In[ ]:


result = chain.invoke("Find a member who is a manager of one or more members.")
print(result["result"].content)


# In[ ]:


result = chain.invoke("Find five members and their managers.")
print(result["result"].content)


# In[ ]:


result = chain.invoke(
    "Find org units or suborganizations of The Mega Group. What are the sites of those units?"
)
print(result["result"].content)


# ### Adding Message History
#
# The Neptune SPARQL QA chain has the ability to be wrapped by [`RunnableWithMessageHistory`](https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html#langchain_core.runnables.history.RunnableWithMessageHistory). This adds message history to the chain, allowing us to create a chatbot that retains conversation state across multiple invocations.
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
#

# In[ ]:


import uuid

session_id = uuid.uuid4()


# Finally, invoke the message history enabled chain with the `session_id`.
#

# In[ ]:


result = runnable_with_history.invoke(
    {"query": "How many org units or suborganizations does the The Mega Group have?"},
    config={"configurable": {"session_id": session_id}},
)
print(result["result"].content)


# As the chain continues to be invoked with the same `session_id`, responses will be returned in the context of previous queries in the conversation.
#

# In[ ]:


result = runnable_with_history.invoke(
    {"query": "List the sites for each of the units."},
    config={"configurable": {"session_id": session_id}},
)
print(result["result"].content)
