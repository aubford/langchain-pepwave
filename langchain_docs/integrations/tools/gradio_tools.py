#!/usr/bin/env python
# coding: utf-8

# # Gradio
# 
# There are many 1000s of `Gradio` apps on `Hugging Face Spaces`. This library puts them at the tips of your LLM's fingers 🦾
# 
# Specifically, `gradio-tools` is a Python library for converting `Gradio` apps into tools that can be leveraged by a large language model (LLM)-based agent to complete its task. For example, an LLM could use a `Gradio` tool to transcribe a voice recording it finds online and then summarize it for you. Or it could use a different `Gradio` tool to apply OCR to a document on your Google Drive and then answer questions about it.
# 
# It's very easy to create you own tool if you want to use a space that's not one of the pre-built tools. Please see this section of the gradio-tools documentation for information on how to do that. All contributions are welcome!

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  gradio_tools langchain-community')


# ## Using a tool

# In[3]:


from gradio_tools.tools import StableDiffusionTool


# In[4]:


local_file_path = StableDiffusionTool().langchain.run(
    "Please create a photo of a dog riding a skateboard"
)
local_file_path


# In[6]:


from PIL import Image


# In[9]:


im = Image.open(local_file_path)


# In[ ]:


from IPython.display import display

display(im)


# ## Using within an agent

# In[14]:


from gradio_tools.tools import (
    ImageCaptioningTool,
    StableDiffusionPromptGeneratorTool,
    StableDiffusionTool,
    TextToVideoTool,
)
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI

llm = OpenAI(temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history")
tools = [
    StableDiffusionTool().langchain,
    ImageCaptioningTool().langchain,
    StableDiffusionPromptGeneratorTool().langchain,
    TextToVideoTool().langchain,
]


agent = initialize_agent(
    tools, llm, memory=memory, agent="conversational-react-description", verbose=True
)
output = agent.run(
    input=(
        "Please create a photo of a dog riding a skateboard "
        "but improve my prompt prior to using an image generator."
        "Please caption the generated image and create a video for it using the improved prompt."
    )
)


# In[ ]:




