#!/usr/bin/env python
# coding: utf-8

# # MLflow
# 
# >[MLflow](https://mlflow.org/) is a versatile, open-source platform for managing workflows and artifacts across the machine learning and generative AI lifecycle. It has built-in integrations with many popular AI and ML libraries, but can be used with any library, algorithm, or deployment tool.
# 
# MLflow's [LangChain integration](https://mlflow.org/docs/latest/llms/langchain/autologging.html) provides the following capabilities:
# 
# - **[Tracing](https://mlflow.org/docs/latest/llms/langchain/autologging.html)**: Visualize data flows through your LangChain components with one line of code (`mlflow.langchain.autolog()`)
# - **[Experiment Tracking](https://mlflow.org/docs/latest/llms/langchain/index.html#experiment-tracking)**: Log artifacts, code, and metrics from your LangChain runs
# - **[Model Management](https://mlflow.org/docs/latest/model-registry.html)**: Version and deploy LangChain applications with dependency tracking
# - **[Evaluation](https://mlflow.org/docs/latest/llms/langchain/index.html#mlflow-evaluate)**: Measure the performance of your LangChain applications
# 
# **Note**: MLflow tracing is available in MLflow versions 2.14.0 and later.
# 
# This short guide focuses on MLflow's tracing capability for LangChain and LangGraph applications. You'll see how to enable tracing with one line of code and view the execution flow of your applications. For information about MLflow's other capabilities and to explore additional tutorials, please refer to the [MLflow documentation for LangChain](https://mlflow.org/docs/latest/llms/langchain/index.html). If you're new to MLflow, check out the [Getting Started with MLflow](https://mlflow.org/docs/latest/getting-started/index.html) guide.

# ## Setup
# 
# To get started with MLflow tracing for LangChain, install the MLflow Python package. We will also use the `langchain-openai` package.
# 

# In[ ]:


get_ipython().run_line_magic('pip', 'install mlflow langchain-openai langgraph -qU')


# Next, set the MLflow tracking URI and OpenAI API key.

# In[4]:


import os

# Set MLflow tracking URI if you have MLflow Tracking Server running
os.environ["MLFLOW_TRACKING_URI"] = ""
os.environ["OPENAI_API_KEY"] = ""


# ## MLflow Tracing
# 
# MLflow's tracing capability helps you visualize the execution flow of your LangChain applications. Here's how to enable it.

# In[ ]:


import mlflow

# Optional: Set an experiment to organize your traces
mlflow.set_experiment("LangChain MLflow Integration")

# Enable tracing
mlflow.langchain.autolog()


# ## Example: Tracing a LangChain Application
# 
# Here's a complete example showing MLflow tracing with LangChain:

# In[4]:


import mlflow
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Enable MLflow tracing
mlflow.langchain.autolog()

# Create a simple chain
llm = ChatOpenAI(model_name="gpt-4o")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm | StrOutputParser()

# Run the chain
result = chain.invoke(
    {
        "input_language": "English",
        "output_language": "German",
        "input": "I love programming.",
    }
)


# To view the trace, run `mlflow ui` in your terminal and navigate to the Traces tab in the MLflow UI.
# 
# ## Example: Tracing a LangGraph Application
# 
# MLflow also supports tracing LangGraph applications:

# In[5]:


import mlflow
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Enable MLflow tracing
mlflow.langchain.autolog()


# Define a tool
@tool
def count_words(text: str) -> str:
    """Counts the number of words in a text."""
    word_count = len(text.split())
    return f"This text contains {word_count} words."


# Create a LangGraph agent
llm = ChatOpenAI(model="gpt-4o")
tools = [count_words]
graph = create_react_agent(llm, tools)

# Run the agent
result = graph.invoke(
    {"messages": [{"role": "user", "content": "Write me a 71-word story about a cat."}]}
)


# To view the trace, run `mlflow ui` in your terminal and navigate to the Traces tab in the MLflow UI.

# ## Resources
# 
# For more information on using MLflow with LangChain, please visit:
# 
# - [MLflow LangChain Integration Documentation](https://mlflow.org/docs/latest/llms/langchain/index.html)
# - [MLflow Tracing Documentation](https://mlflow.org/docs/latest/llms/tracing/index.html)
# - [Logging LangChain and LangGraph Models](https://mlflow.org/docs/latest/llms/langchain/index.html#logging-models-from-code)
# - [Evaluating LangChain and LangGraph Models](https://mlflow.org/docs/latest/llms/langchain/index.html#how-can-i-evaluate-a-langgraph-agent)
