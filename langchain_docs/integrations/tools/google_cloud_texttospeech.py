#!/usr/bin/env python
# coding: utf-8

# # Google Cloud Text-to-Speech
# 
# >[Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) enables developers to synthesize natural-sounding speech with 100+ voices, available in multiple languages and variants. It applies DeepMind’s groundbreaking research in WaveNet and Google’s powerful neural networks to deliver the highest fidelity possible.
# >
# >It supports multiple languages, including English, German, Polish, Spanish, Italian, French, Portuguese, and Hindi.
# 
# This notebook shows how to interact with the `Google Cloud Text-to-Speech API` to achieve speech synthesis capabilities.

# First, you need to set up an Google Cloud project. You can follow the instructions [here](https://cloud.google.com/text-to-speech/docs/before-you-begin).

# In[ ]:


get_ipython().system('pip install --upgrade langchain-google-community[texttospeech]')


# ## Instantiation

# In[8]:


from langchain_google_community import TextToSpeechTool


# ## Deprecated GoogleCloudTextToSpeechTool

# In[10]:


from langchain_community.tools import GoogleCloudTextToSpeechTool


# In[ ]:


text_to_speak = "Hello world!"

tts = GoogleCloudTextToSpeechTool()
tts.name


# We can generate audio, save it to the temporary file and then play it.

# In[7]:


speech_file = tts.run(text_to_speak)

