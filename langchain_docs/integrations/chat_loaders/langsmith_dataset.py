#!/usr/bin/env python
# coding: utf-8

# # LangSmith Chat Datasets
# 
# This notebook demonstrates an easy way to load a LangSmith chat dataset fine-tune a model on that data.
# The process is simple and comprises 3 steps.
# 
# 1. Create the chat dataset.
# 2. Use the LangSmithDatasetChatLoader to load examples.
# 3. Fine-tune your model.
# 
# Then you can use the fine-tuned model in your LangChain app.
# 
# Before diving in, let's install our prerequisites.
# 
# ## Prerequisites
# 
# Ensure you've installed langchain >= 0.0.311 and have configured your environment with your LangSmith API key.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain langchain-openai')


# In[1]:


import os
import uuid

uid = uuid.uuid4().hex[:6]
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "YOUR API KEY"


# ## 1. Select a dataset
# 
# This notebook fine-tunes a model directly on selecting which runs to fine-tune on. You will often curate these from traced runs. You can learn more about LangSmith datasets in the docs [docs](https://docs.smith.langchain.com/evaluation/concepts#datasets).
# 
# For the sake of this tutorial, we will upload an existing dataset here that you can use.

# In[2]:


from langsmith.client import Client

client = Client()


# In[3]:


import requests

url = "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/integrations/chat_loaders/example_data/langsmith_chat_dataset.json"
response = requests.get(url)
response.raise_for_status()
data = response.json()


# In[4]:


dataset_name = f"Extraction Fine-tuning Dataset {uid}"
ds = client.create_dataset(dataset_name=dataset_name, data_type="chat")


# In[5]:


_ = client.create_examples(
    inputs=[e["inputs"] for e in data],
    outputs=[e["outputs"] for e in data],
    dataset_id=ds.id,
)


# ## 2. Prepare Data
# Now we can create an instance of LangSmithRunChatLoader and load the chat sessions using its lazy_load() method.

# In[6]:


from langchain_community.chat_loaders.langsmith import LangSmithDatasetChatLoader

loader = LangSmithDatasetChatLoader(dataset_name=dataset_name)

chat_sessions = loader.lazy_load()


# #### With the chat sessions loaded, convert them into a format suitable for fine-tuning.

# In[7]:


from langchain_community.adapters.openai import convert_messages_for_finetuning

training_data = convert_messages_for_finetuning(chat_sessions)


# ## 3. Fine-tune the Model
# Now, initiate the fine-tuning process using the OpenAI library.

# In[8]:


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

# In[10]:


# Get the fine-tuned model ID
job = openai.fine_tuning.jobs.retrieve(job.id)
model_id = job.fine_tuned_model

# Use the fine-tuned model in LangChain
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model=model_id,
    temperature=1,
)


# In[11]:


model.invoke("There were three ravens sat on a tree.")


# Now you have successfully fine-tuned a model using data from LangSmith LLM runs!
