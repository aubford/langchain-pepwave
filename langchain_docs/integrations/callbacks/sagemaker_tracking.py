#!/usr/bin/env python
# coding: utf-8

# # SageMaker Tracking
# 
# >[Amazon SageMaker](https://aws.amazon.com/sagemaker/) is a fully managed service that is used to quickly and easily build, train and deploy machine learning (ML) models. 
# 
# >[Amazon SageMaker Experiments](https://docs.aws.amazon.com/sagemaker/latest/dg/experiments.html) is a capability of `Amazon SageMaker` that lets you organize, track, compare and evaluate ML experiments and model versions.
# 
# This notebook shows how LangChain Callback can be used to log and track prompts and other LLM hyperparameters into `SageMaker Experiments`. Here, we use different scenarios to showcase the capability:
# 
# * **Scenario 1**: *Single LLM* - A case where a single LLM model is used to generate output based on a given prompt.
# * **Scenario 2**: *Sequential Chain* - A case where a sequential chain of two LLM models is used.
# * **Scenario 3**: *Agent with Tools (Chain of Thought)* - A case where multiple tools (search and math) are used in addition to an LLM.
# 
# 
# In this notebook, we will create a single experiment to log the prompts from each scenario.

# ## Installation and Setup

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  sagemaker')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-openai')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  google-search-results')


# First, setup the required API keys
# 
# * OpenAI: https://platform.openai.com/account/api-keys (For OpenAI LLM model)
# * Google SERP API: https://serpapi.com/manage-api-key (For Google Search Tool)

# In[ ]:


import os

## Add your API keys below
os.environ["OPENAI_API_KEY"] = "<ADD-KEY-HERE>"
os.environ["SERPAPI_API_KEY"] = "<ADD-KEY-HERE>"


# In[ ]:


from langchain_community.callbacks.sagemaker_callback import SageMakerCallbackHandler


# In[ ]:


from langchain.agents import initialize_agent, load_tools
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from sagemaker.analytics import ExperimentAnalytics
from sagemaker.experiments.run import Run
from sagemaker.session import Session


# ## LLM Prompt Tracking

# In[ ]:


# LLM Hyperparameters
HPARAMS = {
    "temperature": 0.1,
    "model_name": "gpt-3.5-turbo-instruct",
}

# Bucket used to save prompt logs (Use `None` is used to save the default bucket or otherwise change it)
BUCKET_NAME = None

# Experiment name
EXPERIMENT_NAME = "langchain-sagemaker-tracker"

# Create SageMaker Session with the given bucket
session = Session(default_bucket=BUCKET_NAME)


# ### Scenario 1 - LLM

# In[ ]:


RUN_NAME = "run-scenario-1"
PROMPT_TEMPLATE = "tell me a joke about {topic}"
INPUT_VARIABLES = {"topic": "fish"}


# In[ ]:


with Run(
    experiment_name=EXPERIMENT_NAME, run_name=RUN_NAME, sagemaker_session=session
) as run:
    # Create SageMaker Callback
    sagemaker_callback = SageMakerCallbackHandler(run)

    # Define LLM model with callback
    llm = OpenAI(callbacks=[sagemaker_callback], **HPARAMS)

    # Create prompt template
    prompt = PromptTemplate.from_template(template=PROMPT_TEMPLATE)

    # Create LLM Chain
    chain = LLMChain(llm=llm, prompt=prompt, callbacks=[sagemaker_callback])

    # Run chain
    chain.run(**INPUT_VARIABLES)

    # Reset the callback
    sagemaker_callback.flush_tracker()


# ### Scenario 2 - Sequential Chain

# In[ ]:


RUN_NAME = "run-scenario-2"

PROMPT_TEMPLATE_1 = """You are a playwright. Given the title of play, it is your job to write a synopsis for that title.
Title: {title}
Playwright: This is a synopsis for the above play:"""
PROMPT_TEMPLATE_2 = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.
Play Synopsis: {synopsis}
Review from a New York Times play critic of the above play:"""

INPUT_VARIABLES = {
    "input": "documentary about good video games that push the boundary of game design"
}


# In[ ]:


with Run(
    experiment_name=EXPERIMENT_NAME, run_name=RUN_NAME, sagemaker_session=session
) as run:
    # Create SageMaker Callback
    sagemaker_callback = SageMakerCallbackHandler(run)

    # Create prompt templates for the chain
    prompt_template1 = PromptTemplate.from_template(template=PROMPT_TEMPLATE_1)
    prompt_template2 = PromptTemplate.from_template(template=PROMPT_TEMPLATE_2)

    # Define LLM model with callback
    llm = OpenAI(callbacks=[sagemaker_callback], **HPARAMS)

    # Create chain1
    chain1 = LLMChain(llm=llm, prompt=prompt_template1, callbacks=[sagemaker_callback])

    # Create chain2
    chain2 = LLMChain(llm=llm, prompt=prompt_template2, callbacks=[sagemaker_callback])

    # Create Sequential chain
    overall_chain = SimpleSequentialChain(
        chains=[chain1, chain2], callbacks=[sagemaker_callback]
    )

    # Run overall sequential chain
    overall_chain.run(**INPUT_VARIABLES)

    # Reset the callback
    sagemaker_callback.flush_tracker()


# ### Scenario 3 - Agent with Tools

# In[ ]:


RUN_NAME = "run-scenario-3"
PROMPT_TEMPLATE = "Who is the oldest person alive? And what is their current age raised to the power of 1.51?"


# In[ ]:


with Run(
    experiment_name=EXPERIMENT_NAME, run_name=RUN_NAME, sagemaker_session=session
) as run:
    # Create SageMaker Callback
    sagemaker_callback = SageMakerCallbackHandler(run)

    # Define LLM model with callback
    llm = OpenAI(callbacks=[sagemaker_callback], **HPARAMS)

    # Define tools
    tools = load_tools(["serpapi", "llm-math"], llm=llm, callbacks=[sagemaker_callback])

    # Initialize agent with all the tools
    agent = initialize_agent(
        tools, llm, agent="zero-shot-react-description", callbacks=[sagemaker_callback]
    )

    # Run agent
    agent.run(input=PROMPT_TEMPLATE)

    # Reset the callback
    sagemaker_callback.flush_tracker()


# ## Load Log Data
# 
# Once the prompts are logged, we can easily load and convert them to Pandas DataFrame as follows.

# In[ ]:


# Load
logs = ExperimentAnalytics(experiment_name=EXPERIMENT_NAME)

# Convert as pandas dataframe
df = logs.dataframe(force_refresh=True)

print(df.shape)
df.head()


# As can be seen above, there are three runs (rows) in the experiment corresponding to each scenario. Each run logs the prompts and related LLM settings/hyperparameters as json and are saved in s3 bucket. Feel free to load and explore the log data from each json path.

# In[ ]:




