#!/usr/bin/env python
# coding: utf-8

# <a target="_blank" href="https://colab.research.google.com/github/langchain-ai/langchain/blob/master/docs/docs/integrations/callbacks/uptrain.ipynb">
#   <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
# </a>

# # UpTrain
# 
# > UpTrain [[github](https://github.com/uptrain-ai/uptrain) || [website](https://uptrain.ai/) || [docs](https://docs.uptrain.ai/getting-started/introduction)] is an open-source platform to evaluate and improve LLM applications. It provides grades for 20+ preconfigured checks (covering language, code, embedding use cases), performs root cause analyses on instances of failure cases and provides guidance for resolving them.

# ## UpTrain Callback Handler
# 
# This notebook showcases the UpTrain callback handler seamlessly integrating into your pipeline, facilitating diverse evaluations. We have chosen a few evaluations that we deemed apt for evaluating the chains. These evaluations run automatically, with results displayed in the output. More details on UpTrain's evaluations can be found [here](https://github.com/uptrain-ai/uptrain?tab=readme-ov-file#pre-built-evaluations-we-offer-). 
# 
# Selected retievers from Langchain are highlighted for demonstration:
# 
# ### 1. **Vanilla RAG**:
# RAG plays a crucial role in retrieving context and generating responses. To ensure its performance and response quality, we conduct the following evaluations:
# 
# - **[Context Relevance](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-relevance)**: Determines if the context extracted from the query is relevant to the response.
# - **[Factual Accuracy](https://docs.uptrain.ai/predefined-evaluations/context-awareness/factual-accuracy)**: Assesses if the LLM is hallcuinating or providing incorrect information.
# - **[Response Completeness](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-completeness)**: Checks if the response contains all the information requested by the query.
# 
# ### 2. **Multi Query Generation**:
# MultiQueryRetriever creates multiple variants of a question having a similar meaning to the original question. Given the complexity, we include the previous evaluations and add:
# 
# - **[Multi Query Accuracy](https://docs.uptrain.ai/predefined-evaluations/query-quality/multi-query-accuracy)**: Assures that the multi-queries generated mean the same as the original query.
# 
# ### 3. **Context Compression and Reranking**:
# Re-ranking involves reordering nodes based on relevance to the query and choosing top n nodes. Since the number of nodes can reduce once the re-ranking is complete, we perform the following evaluations:
# 
# - **[Context Reranking](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-reranking)**: Checks if the order of re-ranked nodes is more relevant to the query than the original order.
# - **[Context Conciseness](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-conciseness)**: Examines whether the reduced number of nodes still provides all the required information.
# 
# These evaluations collectively ensure the robustness and effectiveness of the RAG, MultiQueryRetriever, and the Reranking process in the chain.

# ## Install Dependencies

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain_openai langchain-community uptrain faiss-cpu flashrank')


# NOTE: that you can also install `faiss-gpu` instead of `faiss-cpu` if you want to use the GPU enabled version of the library.

# ## Import Libraries

# In[2]:


from getpass import getpass

from langchain.chains import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.callbacks.uptrain_callback import UpTrainCallbackHandler
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


# ## Load the documents

# In[3]:


loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()


# ## Split the document into chunks

# In[4]:


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
chunks = text_splitter.split_documents(documents)


# ## Create the retriever

# In[5]:


embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(chunks, embeddings)
retriever = db.as_retriever()


# ## Define the LLM

# In[6]:


llm = ChatOpenAI(temperature=0, model="gpt-4")


# ## Setup
# 
# UpTrain provides you with:
# 1. Dashboards with advanced drill-down and filtering options
# 1. Insights and common topics among failing cases
# 1. Observability and real-time monitoring of production data
# 1. Regression testing via seamless integration with your CI/CD pipelines
# 
# You can choose between the following options for evaluating using UpTrain:
# ### 1. **UpTrain's Open-Source Software (OSS)**: 
# You can use the open-source evaluation service to evaluate your model. In this case, you will need to provie an OpenAI API key. UpTrain uses the GPT models to evaluate the responses generated by the LLM. You can get yours [here](https://platform.openai.com/account/api-keys).
# 
# In order to view your evaluations in the UpTrain dashboard, you will need to set it up by running the following commands in your terminal:
# 
# ```bash
# git clone https://github.com/uptrain-ai/uptrain
# cd uptrain
# bash run_uptrain.sh
# ```
# 
# This will start the UpTrain dashboard on your local machine. You can access it at `http://localhost:3000/dashboard`.
# 
# Parameters:
# - key_type="openai"
# - api_key="OPENAI_API_KEY"
# - project_name="PROJECT_NAME"
# 
# 
# ### 2. **UpTrain Managed Service and Dashboards**:
# Alternatively, you can use UpTrain's managed service to evaluate your model. You can create a free UpTrain account [here](https://uptrain.ai/) and get free trial credits. If you want more trial credits, [book a call with the maintainers of UpTrain here](https://calendly.com/uptrain-sourabh/30min).
# 
# The benefits of using the managed service are:
# 1. No need to set up the UpTrain dashboard on your local machine.
# 1. Access to many LLMs without needing their API keys.
# 
# Once you perform the evaluations, you can view them in the UpTrain dashboard at `https://dashboard.uptrain.ai/dashboard`
# 
# Parameters:
# - key_type="uptrain"
# - api_key="UPTRAIN_API_KEY"
# - project_name="PROJECT_NAME"
# 
# 
# **Note:** The `project_name` will be the project name under which the evaluations performed will be shown in the UpTrain dashboard.

# ## Set the API key
# 
# The notebook will prompt you to enter the API key. You can choose between the OpenAI API key or the UpTrain API key by changing the `key_type` parameter in the cell below.

# In[7]:


KEY_TYPE = "openai"  # or "uptrain"
API_KEY = getpass()


# # 1. Vanilla RAG

# UpTrain callback handler will automatically capture the query, context and response once generated and will run the following three evaluations *(Graded from 0 to 1)* on the response:
# - **[Context Relevance](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-relevance)**: Check if the context extractedfrom the query is relevant to the response.
# - **[Factual Accuracy](https://docs.uptrain.ai/predefined-evaluations/context-awareness/factual-accuracy)**: Check how factually accurate the response is.
# - **[Response Completeness](https://docs.uptrain.ai/predefined-evaluations/response-quality/response-completeness)**: Check if the response contains all the information that the query is asking for.

# In[8]:


# Create the RAG prompt
template = """Answer the question based only on the following context, which can include text and tables:
{context}
Question: {question}
"""
rag_prompt_text = ChatPromptTemplate.from_template(template)

# Create the chain
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | rag_prompt_text
    | llm
    | StrOutputParser()
)

# Create the uptrain callback handler
uptrain_callback = UpTrainCallbackHandler(key_type=KEY_TYPE, api_key=API_KEY)
config = {"callbacks": [uptrain_callback]}

# Invoke the chain with a query
query = "What did the president say about Ketanji Brown Jackson"
docs = chain.invoke(query, config=config)


# # 2. Multi Query Generation
# 
# The **MultiQueryRetriever** is used to tackle the problem that the RAG pipeline might not return the best set of documents based on the query. It generates multiple queries that mean the same as the original query and then fetches documents for each.
# 
# To evaluate this retriever, UpTrain will run the following evaluation:
# - **[Multi Query Accuracy](https://docs.uptrain.ai/predefined-evaluations/query-quality/multi-query-accuracy)**: Checks if the multi-queries generated mean the same as the original query.

# In[9]:


# Create the retriever
multi_query_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)

# Create the uptrain callback
uptrain_callback = UpTrainCallbackHandler(key_type=KEY_TYPE, api_key=API_KEY)
config = {"callbacks": [uptrain_callback]}

# Create the RAG prompt
template = """Answer the question based only on the following context, which can include text and tables:
{context}
Question: {question}
"""
rag_prompt_text = ChatPromptTemplate.from_template(template)

chain = (
    {"context": multi_query_retriever, "question": RunnablePassthrough()}
    | rag_prompt_text
    | llm
    | StrOutputParser()
)

# Invoke the chain with a query
question = "What did the president say about Ketanji Brown Jackson"
docs = chain.invoke(question, config=config)


# # 3. Context Compression and Reranking
# 
# The reranking process involves reordering nodes based on relevance to the query and choosing the top n nodes. Since the number of nodes can reduce once the reranking is complete, we perform the following evaluations:
# - **[Context Reranking](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-reranking)**: Check if the order of re-ranked nodes is more relevant to the query than the original order.
# - **[Context Conciseness](https://docs.uptrain.ai/predefined-evaluations/context-awareness/context-conciseness)**: Check if the reduced number of nodes still provides all the required information.

# In[10]:


# Create the retriever
compressor = FlashrankRerank()
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

# Create the chain
chain = RetrievalQA.from_chain_type(llm=llm, retriever=compression_retriever)

# Create the uptrain callback
uptrain_callback = UpTrainCallbackHandler(key_type=KEY_TYPE, api_key=API_KEY)
config = {"callbacks": [uptrain_callback]}

# Invoke the chain with a query
query = "What did the president say about Ketanji Brown Jackson"
result = chain.invoke(query, config=config)


# # UpTrain's Dashboard and Insights
# 
# Here's a short video showcasing the dashboard and the insights:
# 
# ![langchain_uptrain.gif](https://uptrain-assets.s3.ap-south-1.amazonaws.com/images/langchain/langchain_uptrain.gif)
