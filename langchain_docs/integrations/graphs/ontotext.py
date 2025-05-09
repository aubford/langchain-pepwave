#!/usr/bin/env python
# coding: utf-8

# # Ontotext GraphDB
# 
# >[Ontotext GraphDB](https://graphdb.ontotext.com/) is a graph database and knowledge discovery tool compliant with [RDF](https://www.w3.org/RDF/) and [SPARQL](https://www.w3.org/TR/sparql11-query/).
# 
# >This notebook shows how to use LLMs to provide natural language querying (NLQ to SPARQL, also called `text2sparql`) for `Ontotext GraphDB`. 

# ## GraphDB LLM Functionalities
# 
# `GraphDB` supports some LLM integration functionalities as described [here](https://github.com/w3c/sparql-dev/issues/193):
# 
# [gpt-queries](https://graphdb.ontotext.com/documentation/10.5/gpt-queries.html)
# 
# * magic predicates to ask an LLM for text, list or table using data from your knowledge graph (KG)
# * query explanation
# * result explanation, summarization, rephrasing, translation
# 
# [retrieval-graphdb-connector](https://graphdb.ontotext.com/documentation/10.5/retrieval-graphdb-connector.html)
# 
# * Indexing of KG entities in a vector database
# * Supports any text embedding algorithm and vector database
# * Uses the same powerful connector (indexing) language that GraphDB uses for Elastic, Solr, Lucene
# * Automatic synchronization of changes in RDF data to the KG entity index
# * Supports nested objects (no UI support in GraphDB version 10.5)
# * Serializes KG entities to text like this (e.g. for a Wines dataset):
# 
# ```
# Franvino:
# - is a RedWine.
# - made from grape Merlo.
# - made from grape Cabernet Franc.
# - has sugar dry.
# - has year 2012.
# ```
# 
# [talk-to-graph](https://graphdb.ontotext.com/documentation/10.5/talk-to-graph.html)
# 
# * A simple chatbot using a defined KG entity index
# 
# 
# For this tutorial, we won't use the GraphDB LLM integration, but `SPARQL` generation from NLQ. We'll use the `Star Wars API` (`SWAPI`) ontology and dataset that you can examine [here](https://github.com/Ontotext-AD/langchain-graphdb-qa-chain-demo/blob/main/starwars-data.trig).
# 

# ## Setting up
# 
# You need a running GraphDB instance. This tutorial shows how to run the database locally using the [GraphDB Docker image](https://hub.docker.com/r/ontotext/graphdb). It provides a docker compose set-up, which populates GraphDB with the Star Wars dataset. All necessary files including this notebook can be downloaded from [the GitHub repository langchain-graphdb-qa-chain-demo](https://github.com/Ontotext-AD/langchain-graphdb-qa-chain-demo).
# 
# * Install [Docker](https://docs.docker.com/get-docker/). This tutorial is created using Docker version `24.0.7` which bundles [Docker Compose](https://docs.docker.com/compose/). For earlier Docker versions you may need to install Docker Compose separately.
# * Clone [the GitHub repository langchain-graphdb-qa-chain-demo](https://github.com/Ontotext-AD/langchain-graphdb-qa-chain-demo) in a local folder on your machine.
# * Start GraphDB with the following script executed from the same folder
#   
# ```
# docker build --tag graphdb .
# docker compose up -d graphdb
# ```
# 
#   You need to wait a couple of seconds for the database to start on `http://localhost:7200/`. The Star Wars dataset `starwars-data.trig` is automatically loaded into the `langchain` repository. The local SPARQL endpoint `http://localhost:7200/repositories/langchain` can be used to run queries against. You can also open the GraphDB Workbench from your favourite web browser `http://localhost:7200/sparql` where you can make queries interactively.
# * Set up working environment
# 
# If you use `conda`, create and activate a new conda environment, e.g.:
# 
# ```
# conda create -n graph_ontotext_graphdb_qa python=3.12
# conda activate graph_ontotext_graphdb_qa
# ```
# 
# Install the following libraries:
# 
# ```
# pip install jupyter==1.1.1
# pip install rdflib==7.1.1
# pip install langchain-community==0.3.4
# pip install langchain-openai==0.2.4
# ```
# 
# Run Jupyter with
# ```
# jupyter notebook
# ```

# ## Specifying the ontology
# 
# In order for the LLM to be able to generate SPARQL, it needs to know the knowledge graph schema (the ontology). It can be provided using one of two parameters on the `OntotextGraphDBGraph` class:
# 
# * `query_ontology`: a `CONSTRUCT` query that is executed on the SPARQL endpoint and returns the KG schema statements. We recommend that you store the ontology in its own named graph, which will make it easier to get only the relevant statements (as the example below). `DESCRIBE` queries are not supported, because `DESCRIBE` returns the Symmetric Concise Bounded Description (SCBD), i.e. also the incoming class links. In case of large graphs with a million of instances, this is not efficient. Check https://github.com/eclipse-rdf4j/rdf4j/issues/4857
# * `local_file`: a local RDF ontology file. Supported RDF formats are `Turtle`, `RDF/XML`, `JSON-LD`, `N-Triples`, `Notation-3`, `Trig`, `Trix`, `N-Quads`.
# 
# In either case, the ontology dump should:
# 
# * Include enough information about classes, properties, property attachment to classes (using rdfs:domain, schema:domainIncludes or OWL restrictions), and taxonomies (important individuals).
# * Not include overly verbose and irrelevant definitions and examples that do not help SPARQL construction.

# In[1]:


from langchain_community.graphs import OntotextGraphDBGraph

# feeding the schema using a user construct query

graph = OntotextGraphDBGraph(
    query_endpoint="http://localhost:7200/repositories/langchain",
    query_ontology="CONSTRUCT {?s ?p ?o} FROM <https://swapi.co/ontology/> WHERE {?s ?p ?o}",
)


# In[ ]:


# feeding the schema using a local RDF file

graph = OntotextGraphDBGraph(
    query_endpoint="http://localhost:7200/repositories/langchain",
    local_file="/path/to/langchain_graphdb_tutorial/starwars-ontology.nt",  # change the path here
)


# Either way, the ontology (schema) is fed to the LLM as `Turtle` since `Turtle` with appropriate prefixes is most compact and easiest for the LLM to remember.
# 
# The Star Wars ontology is a bit unusual in that it includes a lot of specific triples about classes, e.g. that the species `:Aleena` live on `<planet/38>`, they are a subclass of `:Reptile`, have certain typical characteristics (average height, average lifespan, skinColor), and specific individuals (characters) are representatives of that class:
# 
# 
# ```
# @prefix : <https://swapi.co/vocabulary/> .
# @prefix owl: <http://www.w3.org/2002/07/owl#> .
# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# 
# :Aleena a owl:Class, :Species ;
#     rdfs:label "Aleena" ;
#     rdfs:isDefinedBy <https://swapi.co/ontology/> ;
#     rdfs:subClassOf :Reptile, :Sentient ;
#     :averageHeight 80.0 ;
#     :averageLifespan "79" ;
#     :character <https://swapi.co/resource/aleena/47> ;
#     :film <https://swapi.co/resource/film/4> ;
#     :language "Aleena" ;
#     :planet <https://swapi.co/resource/planet/38> ;
#     :skinColor "blue", "gray" .
# 
#     ...
# 
#  ```
# 

# In order to keep this tutorial simple, we use un-secured GraphDB. If GraphDB is secured, you should set the environment variables 'GRAPHDB_USERNAME' and 'GRAPHDB_PASSWORD' before the initialization of `OntotextGraphDBGraph`.
# 
# ```python
# os.environ["GRAPHDB_USERNAME"] = "graphdb-user"
# os.environ["GRAPHDB_PASSWORD"] = "graphdb-password"
# 
# graph = OntotextGraphDBGraph(
#     query_endpoint=...,
#     query_ontology=...
# )
# ```
# 

# ## Question Answering against the StarWars dataset
# 
# We can now use the `OntotextGraphDBQAChain` to ask some questions.

# In[2]:


import os

from langchain.chains import OntotextGraphDBQAChain
from langchain_openai import ChatOpenAI

# We'll be using an OpenAI model which requires an OpenAI API Key.
# However, other models are available as well:
# https://python.langchain.com/docs/integrations/chat/

# Set the environment variable `OPENAI_API_KEY` to your OpenAI API key
os.environ["OPENAI_API_KEY"] = "sk-***"

# Any available OpenAI model can be used here.
# We use 'gpt-4-1106-preview' because of the bigger context window.
# The 'gpt-4-1106-preview' model_name will deprecate in the future and will change to 'gpt-4-turbo' or similar,
# so be sure to consult with the OpenAI API https://platform.openai.com/docs/models for the correct naming.

chain = OntotextGraphDBQAChain.from_llm(
    ChatOpenAI(temperature=0, model_name="gpt-4-1106-preview"),
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
)


# Let's ask a simple one.

# In[3]:


chain.invoke({chain.input_key: "What is the climate on Tatooine?"})[chain.output_key]


# And a bit more complicated one.

# In[4]:


chain.invoke({chain.input_key: "What is the climate on Luke Skywalker's home planet?"})[
    chain.output_key
]


# We can also ask more complicated questions like

# In[5]:


chain.invoke(
    {
        chain.input_key: "What is the average box office revenue for all the Star Wars movies?"
    }
)[chain.output_key]


# ## Chain modifiers
# 
# The Ontotext GraphDB QA chain allows prompt refinement for further improvement of your QA chain and enhancing the overall user experience of your app.
# 
# 
# ### "SPARQL Generation" prompt
# 
# The prompt is used for the SPARQL query generation based on the user question and the KG schema.
# 
# - `sparql_generation_prompt`
# 
#     Default value:
#   ````python
#     GRAPHDB_SPARQL_GENERATION_TEMPLATE = """
#     Write a SPARQL SELECT query for querying a graph database.
#     The ontology schema delimited by triple backticks in Turtle format is:
#     ```
#     {schema}
#     ```
#     Use only the classes and properties provided in the schema to construct the SPARQL query.
#     Do not use any classes or properties that are not explicitly provided in the SPARQL query.
#     Include all necessary prefixes.
#     Do not include any explanations or apologies in your responses.
#     Do not wrap the query in backticks.
#     Do not include any text except the SPARQL query generated.
#     The question delimited by triple backticks is:
#     ```
#     {prompt}
#     ```
#     """
#     GRAPHDB_SPARQL_GENERATION_PROMPT = PromptTemplate(
#         input_variables=["schema", "prompt"],
#         template=GRAPHDB_SPARQL_GENERATION_TEMPLATE,
#     )
#   ````
# 
# ### "SPARQL Fix" prompt
# 
# Sometimes, the LLM may generate a SPARQL query with syntactic errors or missing prefixes, etc. The chain will try to amend this by prompting the LLM to correct it a certain number of times.
# 
# - `sparql_fix_prompt`
# 
#     Default value:
#   ````python
#     GRAPHDB_SPARQL_FIX_TEMPLATE = """
#     This following SPARQL query delimited by triple backticks
#     ```
#     {generated_sparql}
#     ```
#     is not valid.
#     The error delimited by triple backticks is
#     ```
#     {error_message}
#     ```
#     Give me a correct version of the SPARQL query.
#     Do not change the logic of the query.
#     Do not include any explanations or apologies in your responses.
#     Do not wrap the query in backticks.
#     Do not include any text except the SPARQL query generated.
#     The ontology schema delimited by triple backticks in Turtle format is:
#     ```
#     {schema}
#     ```
#     """
#     
#     GRAPHDB_SPARQL_FIX_PROMPT = PromptTemplate(
#         input_variables=["error_message", "generated_sparql", "schema"],
#         template=GRAPHDB_SPARQL_FIX_TEMPLATE,
#     )
#   ````
# 
# - `max_fix_retries`
#   
#     Default value: `5`
# 
# ### "Answering" prompt
# 
# The prompt is used for answering the question based on the results returned from the database and the initial user question. By default, the LLM is instructed to only use the information from the returned result(s). If the result set is empty, the LLM should inform that it can't answer the question.
# 
# - `qa_prompt`
#   
#   Default value:
#   ````python
#     GRAPHDB_QA_TEMPLATE = """Task: Generate a natural language response from the results of a SPARQL query.
#     You are an assistant that creates well-written and human understandable answers.
#     The information part contains the information provided, which you can use to construct an answer.
#     The information provided is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
#     Make your response sound like the information is coming from an AI assistant, but don't add any information.
#     Don't use internal knowledge to answer the question, just say you don't know if no information is available.
#     Information:
#     {context}
#     
#     Question: {prompt}
#     Helpful Answer:"""
#     GRAPHDB_QA_PROMPT = PromptTemplate(
#         input_variables=["context", "prompt"], template=GRAPHDB_QA_TEMPLATE
#     )
#   ````

# Once you're finished playing with QA with GraphDB, you can shut down the Docker environment by running
# ``
# docker compose down -v --remove-orphans
# ``
# from the directory with the Docker compose file.
