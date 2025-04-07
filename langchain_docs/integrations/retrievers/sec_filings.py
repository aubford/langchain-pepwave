#!/usr/bin/env python
# coding: utf-8

# # SEC filing
# 
# 
# >[SEC filing](https://www.sec.gov/edgar) is a financial statement or other formal document submitted to the U.S. Securities and Exchange Commission (SEC). Public companies, certain insiders, and broker-dealers are required to make regular `SEC filings`. Investors and financial professionals rely on these filings for information about companies they are evaluating for investment purposes.
# >
# >`SEC filings` data powered by [Kay.ai](https://kay.ai) and [Cybersyn](https://www.cybersyn.com/) via [Snowflake Marketplace](https://app.snowflake.com/marketplace/providers/GZTSZAS2KCS/Cybersyn%2C%20Inc).
# 

# ## Setup
# 
# 
# First, you will need to install the `kay` package. You will also need an API key: you can get one for free at [https://kay.ai](https://kay.ai/). Once you have an API key, you must set it as an environment variable `KAY_API_KEY`.
# 
# In this example, we're going to use the `KayAiRetriever`. Take a look at the [kay notebook](/docs/integrations/retrievers/kay) for more detailed information for the parameters that it accepts.`

# In[2]:


# Setup API keys for Kay and OpenAI
from getpass import getpass

KAY_API_KEY = getpass()
OPENAI_API_KEY = getpass()


# In[3]:


import os

os.environ["KAY_API_KEY"] = KAY_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# ## Example

# In[7]:


from langchain.chains import ConversationalRetrievalChain
from langchain_community.retrievers import KayAiRetriever
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-3.5-turbo")
retriever = KayAiRetriever.create(
    dataset_id="company", data_types=["10-K", "10-Q"], num_contexts=6
)
qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)


# In[11]:


questions = [
    "What are patterns in Nvidia's spend over the past three quarters?",
    # "What are some recent challenges faced by the renewable energy sector?",
]
chat_history = []

for question in questions:
    result = qa({"question": question, "chat_history": chat_history})
    chat_history.append((question, result["answer"]))
    print(f"-> **Question**: {question} \n")
    print(f"**Answer**: {result['answer']} \n")

