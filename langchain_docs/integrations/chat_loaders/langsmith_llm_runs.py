#!/usr/bin/env python
# coding: utf-8

# # LangSmith LLM Runs
# 
# This notebook demonstrates how to directly load data from LangSmith's LLM runs and fine-tune a model on that data.
# The process is simple and comprises 3 steps.
# 
# 1. Select the LLM runs to train on.
# 2. Use the LangSmithRunChatLoader to load runs as chat sessions.
# 3. Fine-tune your model.
# 
# Then you can use the fine-tuned model in your LangChain app.
# 
# Before diving in, let's install our prerequisites.
# 
# ## Prerequisites
# 
# Ensure you've installed langchain >= 0.0.311 and have configured your environment with your LangSmith API key.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain langchain-openai')


# In[1]:


import os
import uuid

uid = uuid.uuid4().hex[:6]
project_name = f"Run Fine-tuning Walkthrough {uid}"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "YOUR API KEY"
os.environ["LANGSMITH_PROJECT"] = project_name


# ## 1. Select Runs
# The first step is selecting which runs to fine-tune on. A common case would be to select LLM runs within
# traces that have received positive user feedback. You can find examples of this in the[LangSmith Cookbook](https://github.com/langchain-ai/langsmith-cookbook/blob/main/exploratory-data-analysis/exporting-llm-runs-and-feedback/llm_run_etl.ipynb) and in the [docs](https://docs.smith.langchain.com/tracing/use-cases/export-runs/local).
# 
# For the sake of this tutorial, we will generate some runs for you to use here. Let's try fine-tuning a
# simple function-calling chain.

# In[2]:


from enum import Enum

from pydantic import BaseModel, Field


class Operation(Enum):
    add = "+"
    subtract = "-"
    multiply = "*"
    divide = "/"


class Calculator(BaseModel):
    """A calculator function"""

    num1: float
    num2: float
    operation: Operation = Field(..., description="+,-,*,/")

    def calculate(self):
        if self.operation == Operation.add:
            return self.num1 + self.num2
        elif self.operation == Operation.subtract:
            return self.num1 - self.num2
        elif self.operation == Operation.multiply:
            return self.num1 * self.num2
        elif self.operation == Operation.divide:
            if self.num2 != 0:
                return self.num1 / self.num2
            else:
                return "Cannot divide by zero"


# In[3]:


from pprint import pprint

from langchain_core.utils.function_calling import convert_pydantic_to_openai_function
from pydantic import BaseModel

openai_function_def = convert_pydantic_to_openai_function(Calculator)
pprint(openai_function_def)


# In[4]:


from langchain_core.output_parsers.openai_functions import PydanticOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an accounting assistant."),
        ("user", "{input}"),
    ]
)
chain = (
    prompt
    | ChatOpenAI().bind(functions=[openai_function_def])
    | PydanticOutputFunctionsParser(pydantic_schema=Calculator)
    | (lambda x: x.calculate())
)


# In[5]:


math_questions = [
    "What's 45/9?",
    "What's 81/9?",
    "What's 72/8?",
    "What's 56/7?",
    "What's 36/6?",
    "What's 64/8?",
    "What's 12*6?",
    "What's 8*8?",
    "What's 10*10?",
    "What's 11*11?",
    "What's 13*13?",
    "What's 45+30?",
    "What's 72+28?",
    "What's 56+44?",
    "What's 63+37?",
    "What's 70-35?",
    "What's 60-30?",
    "What's 50-25?",
    "What's 40-20?",
    "What's 30-15?",
]
results = chain.batch([{"input": q} for q in math_questions], return_exceptions=True)


# #### Load runs that did not error
# 
# Now we can select the successful runs to fine-tune on.

# In[6]:


from langsmith.client import Client

client = Client()


# In[7]:


successful_traces = {
    run.trace_id
    for run in client.list_runs(
        project_name=project_name,
        execution_order=1,
        error=False,
    )
}

llm_runs = [
    run
    for run in client.list_runs(
        project_name=project_name,
        run_type="llm",
    )
    if run.trace_id in successful_traces
]


# ## 2. Prepare data
# Now we can create an instance of LangSmithRunChatLoader and load the chat sessions using its lazy_load() method.

# In[8]:


from langchain_community.chat_loaders.langsmith import LangSmithRunChatLoader

loader = LangSmithRunChatLoader(runs=llm_runs)

chat_sessions = loader.lazy_load()


# #### With the chat sessions loaded, convert them into a format suitable for fine-tuning.

# In[9]:


from langchain_community.adapters.openai import convert_messages_for_finetuning

training_data = convert_messages_for_finetuning(chat_sessions)


# ## 3. Fine-tune the model
# Now, initiate the fine-tuning process using the OpenAI library.

# In[10]:


import json
import time
from io import BytesIO

import openai

my_file = BytesIO()
for dialog in training_data:
    my_file.write((json.dumps({"messages": dialog}) + "\n").encode("utf-8"))

my_file.seek(0)
training_file = openai.files.create(file=my_file, purpose="fine-tune")

job = openai.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-3.5-turbo",
)

# Wait for the fine-tuning to complete (this may take some time)
status = openai.fine_tuning.jobs.retrieve(job.id).status
start_time = time.time()
while status != "succeeded":
    print(f"Status=[{status}]... {time.time() - start_time:.2f}s", end="\r", flush=True)
    time.sleep(5)
    status = openai.fine_tuning.jobs.retrieve(job.id).status

# Now your model is fine-tuned!


# ## 4. Use in LangChain
# 
# After fine-tuning, use the resulting model ID with the ChatOpenAI model class in your LangChain app.

# In[11]:


# Get the fine-tuned model ID
job = openai.fine_tuning.jobs.retrieve(job.id)
model_id = job.fine_tuned_model

# Use the fine-tuned model in LangChain
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model=model_id,
    temperature=1,
)


# In[12]:


(prompt | model).invoke({"input": "What's 56/7?"})


# Now you have successfully fine-tuned a model using data from LangSmith LLM runs!
