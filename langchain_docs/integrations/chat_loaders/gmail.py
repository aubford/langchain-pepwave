#!/usr/bin/env python
# coding: utf-8

# # GMail
# 
# This loader goes over how to load data from GMail. There are many ways you could want to load data from GMail. This loader is currently fairly opinionated in how to do so. The way it does it is it first looks for all messages that you have sent. It then looks for messages where you are responding to a previous email. It then fetches that previous email, and creates a training example of that email, followed by your email.
# 
# Note that there are clear limitations here. For example, all examples created are only looking at the previous email for context.
# 
# To use:
# 
# - Set up a Google Developer Account: Go to the Google Developer Console, create a project, and enable the Gmail API for that project. This will give you a credentials.json file that you'll need later.
# 
# - Install the Google Client Library: Run the following command to install the Google Client Library:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client')


# In[6]:


import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("email_token.json"):
    creds = Credentials.from_authorized_user_file("email_token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
            "creds.json",
            SCOPES,
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("email_token.json", "w") as token:
        token.write(creds.to_json())


# In[7]:


from langchain_community.chat_loaders.gmail import GMailLoader


# In[10]:


loader = GMailLoader(creds=creds, n=3)


# In[11]:


data = loader.load()


# In[13]:


# Sometimes there can be errors which we silently ignore
len(data)


# In[14]:


from langchain_community.chat_loaders.utils import (
    map_ai_messages,
)


# In[17]:


# This makes messages sent by hchase@langchain.com the AI Messages
# This means you will train an LLM to predict as if it's responding as hchase
training_data = list(
    map_ai_messages(data, sender="Harrison Chase <hchase@langchain.com>")
)


# In[ ]:




