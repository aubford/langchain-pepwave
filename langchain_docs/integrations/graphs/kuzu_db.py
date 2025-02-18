#!/usr/bin/env python
# coding: utf-8

# # Kuzu
#
# > [Kùzu](https://kuzudb.com/) is an embeddable, scalable, extremely fast graph database.
# > It is permissively licensed with an MIT license, and you can see its source code [here](https://github.com/kuzudb/kuzu).
#
# > Key characteristics of Kùzu:
# >- Performance and scalability: Implements modern, state-of-the-art join algorithms for graphs.
# >- Usability: Very easy to set up and get started with, as there are no servers (embedded architecture).
# >- Interoperability: Can conveniently scan and copy data from external columnar formats, CSV, JSON and relational databases.
# >- Structured property graph model: Implements the property graph model, with added structure.
# >- Cypher support: Allows convenient querying of the graph in Cypher, a declarative query language.
#
# > Get started with Kùzu by visiting their [documentation](https://docs.kuzudb.com/).

# ## Setting up
#
# Kùzu is an embedded database (it runs in-process), so there are no servers to manage. Install the
# following dependencies to get started:
#
# ```bash
# pip install -U langchain-kuzu langchain-openai langchain-experimental
# ```
#
# This installs Kùzu along with the LangChain integration for it, as well as the OpenAI Python package
# so that we can use OpenAI's LLMs. If you want to use other LLM providers, you can install their
# respective Python packages that come with LangChain.

# Here's how you would first create a Kùzu database on your local machine and connect to it:

# In[1]:


import kuzu

db = kuzu.Database("test_db")
conn = kuzu.Connection(db)


# ## Create `KuzuGraph`

# Kùzu's integration with LangChain makes it convenient to create and update graphs from unstructured text, and also to query graphs via a Text2Cypher pipeline that utilizes the
# power of LangChain's LLM chains. To begin, we create a `KuzuGraph` object that uses the database object we created above in combination with the `KuzuGraph` constructor.

# In[2]:


from langchain_kuzu.graphs.kuzu_graph import KuzuGraph

graph = KuzuGraph(db, allow_dangerous_requests=True)


# Say we want to transform the following text into a graph:

# In[3]:


text = "Tim Cook is the CEO of Apple. Apple has its headquarters in California."


# We will make use of `LLMGraphTransformer` to use an LLM to extract nodes and relationships from the text.
# To make the graph more useful, we will define the following schema, such that the LLM will only
# extract nodes and relationships that match the schema.

# In[4]:


# Define schema
allowed_nodes = ["Person", "Company", "Location"]
allowed_relationships = [
    ("Person", "IS_CEO_OF", "Company"),
    ("Company", "HAS_HEADQUARTERS_IN", "Location"),
]


# The `LLMGraphTransformer` class provides a convenient way to convert the text into a list of graph documents.

# In[6]:


from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI

# Define the LLMGraphTransformer
llm_transformer = LLMGraphTransformer(
    llm=ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY
    ),  # noqa: F821
    allowed_nodes=allowed_nodes,
    allowed_relationships=allowed_relationships,
)

documents = [Document(page_content=text)]
graph_documents = llm_transformer.convert_to_graph_documents(documents)


# In[7]:


graph_documents[:2]


# We can then call the above defined `KuzuGraph` object's `add_graph_documents` method to ingest the graph documents into the Kùzu database.
# The `include_source` argument is set to `True` so that we also create relationships between each entity node and the source document that it came from.

# In[8]:


# Add the graph document to the graph
graph.add_graph_documents(
    graph_documents,
    include_source=True,
)


# ## Creating `KuzuQAChain`
#
# To query the graph via a Text2Cypher pipeline, we can define a `KuzuQAChain` object. Then, we can invoke the chain with a query by connecting to the existing database that's stored in the `test_db` directory defined above.

# In[9]:


from langchain_kuzu.chains.graph_qa.kuzu import KuzuQAChain

# Create the KuzuQAChain with verbosity enabled to see the generated Cypher queries
chain = KuzuQAChain.from_llm(
    llm=ChatOpenAI(
        model="gpt-4o-mini", temperature=0.3, api_key=OPENAI_API_KEY
    ),  # noqa: F821
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
)


# Note that we set a temperature that's slightly higher than zero to avoid the LLM being overly concise in its response.

# Let's ask some questions using the QA chain.

# In[10]:


chain.invoke("Who is the CEO of Apple?")


# In[11]:


chain.invoke("Where is Apple headquartered?")


# ## Refresh graph schema
#
# If you mutate or update the graph, you can inspect the refreshed schema information that's used by the Text2Cypher chain to generate Cypher statements.
# You don't need to manually call `refresh_schema()` each time as it's called automatically when you invoke the chain.

# In[12]:


graph.refresh_schema()

print(graph.get_schema)


# ## Use separate LLMs for Cypher and answer generation
#
# You can specify `cypher_llm` and `qa_llm` separately to use different LLMs for Cypher generation and answer generation.

# In[13]:


chain = KuzuQAChain.from_llm(
    cypher_llm=ChatOpenAI(temperature=0, model="gpt-4o-mini"),
    qa_llm=ChatOpenAI(temperature=0, model="gpt-4"),
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
)


# In[14]:


chain.invoke("Who is the CEO of Apple?")
