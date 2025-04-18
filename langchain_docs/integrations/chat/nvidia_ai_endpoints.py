#!/usr/bin/env python
# coding: utf-8

# ---
# sidebar_label: NVIDIA AI Endpoints
# ---

# # ChatNVIDIA
# 
# This will help you getting started with NVIDIA [chat models](/docs/concepts/chat_models). For detailed documentation of all `ChatNVIDIA` features and configurations head to the [API reference](https://python.langchain.com/api_reference/nvidia_ai_endpoints/chat_models/langchain_nvidia_ai_endpoints.chat_models.ChatNVIDIA.html).
# 
# ## Overview
# The `langchain-nvidia-ai-endpoints` package contains LangChain integrations building applications with models on
# NVIDIA NIM inference microservice. NIM supports models across domains like chat, embedding, and re-ranking models
# from the community as well as NVIDIA. These models are optimized by NVIDIA to deliver the best performance on NVIDIA
# accelerated infrastructure and deployed as a NIM, an easy-to-use, prebuilt containers that deploy anywhere using a single
# command on NVIDIA accelerated infrastructure.
# 
# NVIDIA hosted deployments of NIMs are available to test on the [NVIDIA API catalog](https://build.nvidia.com/). After testing,
# NIMs can be exported from NVIDIA’s API catalog using the NVIDIA AI Enterprise license and run on-premises or in the cloud,
# giving enterprises ownership and full control of their IP and AI application.
# 
# NIMs are packaged as container images on a per model basis and are distributed as NGC container images through the NVIDIA NGC Catalog.
# At their core, NIMs provide easy, consistent, and familiar APIs for running inference on an AI model.
# 
# This example goes over how to use LangChain to interact with NVIDIA supported via the `ChatNVIDIA` class.
# 
# For more information on accessing the chat models through this api, check out the [ChatNVIDIA](https://python.langchain.com/docs/integrations/chat/nvidia_ai_endpoints/) documentation.
# 
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatNVIDIA](https://python.langchain.com/api_reference/nvidia_ai_endpoints/chat_models/langchain_nvidia_ai_endpoints.chat_models.ChatNVIDIA.html) | [langchain_nvidia_ai_endpoints](https://python.langchain.com/api_reference/nvidia_ai_endpoints/index.html) | ✅ | beta | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain_nvidia_ai_endpoints?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain_nvidia_ai_endpoints?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
# 
# ## Setup
# 
# **To get started:**
# 
# 1. Create a free account with [NVIDIA](https://build.nvidia.com/), which hosts NVIDIA AI Foundation models.
# 
# 2. Click on your model of choice.
# 
# 3. Under `Input` select the `Python` tab, and click `Get API Key`. Then click `Generate Key`.
# 
# 4. Copy and save the generated key as `NVIDIA_API_KEY`. From there, you should have access to the endpoints.
# 
# ### Credentials
# 

# In[ ]:


import getpass
import os

if not os.getenv("NVIDIA_API_KEY"):
    # Note: the API key should start with "nvapi-"
    os.environ["NVIDIA_API_KEY"] = getpass.getpass("Enter your NVIDIA API key: ")


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain NVIDIA AI Endpoints integration lives in the `langchain_nvidia_ai_endpoints` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-nvidia-ai-endpoints')


# ## Instantiation
# 
# Now we can access models in the NVIDIA API Catalog:

# In[ ]:


## Core LC Chat Interface
from langchain_nvidia_ai_endpoints import ChatNVIDIA

llm = ChatNVIDIA(model="mistralai/mixtral-8x7b-instruct-v0.1")


# ## Invocation

# In[ ]:


result = llm.invoke("Write a ballad about LangChain.")
print(result.content)


# ## Working with NVIDIA NIMs
# When ready to deploy, you can self-host models with NVIDIA NIM—which is included with the NVIDIA AI Enterprise software license—and run them anywhere, giving you ownership of your customizations and full control of your intellectual property (IP) and AI applications.
# 
# [Learn more about NIMs](https://developer.nvidia.com/blog/nvidia-nim-offers-optimized-inference-microservices-for-deploying-ai-models-at-scale/)
# 

# In[ ]:


from langchain_nvidia_ai_endpoints import ChatNVIDIA

# connect to an embedding NIM running at localhost:8000, specifying a specific model
llm = ChatNVIDIA(base_url="http://localhost:8000/v1", model="meta/llama3-8b-instruct")


# ## Stream, Batch, and Async
# 
# These models natively support streaming, and as is the case with all LangChain LLMs they expose a batch method to handle concurrent requests, as well as async methods for invoke, stream, and batch. Below are a few examples.

# In[ ]:


print(llm.batch(["What's 2*3?", "What's 2*6?"]))
# Or via the async API
# await llm.abatch(["What's 2*3?", "What's 2*6?"])


# In[ ]:


for chunk in llm.stream("How far can a seagull fly in one day?"):
    # Show the token separations
    print(chunk.content, end="|")


# In[ ]:


async for chunk in llm.astream(
    "How long does it take for monarch butterflies to migrate?"
):
    print(chunk.content, end="|")


# ## Supported models
# 
# Querying `available_models` will still give you all of the other models offered by your API credentials.
# 
# The `playground_` prefix is optional.

# In[ ]:


ChatNVIDIA.get_available_models()
# llm.get_available_models()


# ## Model types

# All of these models above are supported and can be accessed via `ChatNVIDIA`.
# 
# Some model types support unique prompting techniques and chat messages. We will review a few important ones below.
# 
# **To find out more about a specific model, please navigate to the API section of an AI Foundation model [as linked here](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/ai-foundation/models/codellama-13b/api).**

# ### General Chat
# 
# Models such as `meta/llama3-8b-instruct` and `mistralai/mixtral-8x22b-instruct-v0.1` are good all-around models that you can use for with any LangChain chat messages. Example below.

# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a helpful AI assistant named Fred."), ("user", "{input}")]
)
chain = prompt | ChatNVIDIA(model="meta/llama3-8b-instruct") | StrOutputParser()

for txt in chain.stream({"input": "What's your name?"}):
    print(txt, end="")


# ### Code Generation
# 
# These models accept the same arguments and input structure as regular chat models, but they tend to perform better on code-genreation and structured code tasks. An example of this is `meta/codellama-70b`.

# In[ ]:


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert coding AI. Respond only in valid python; no narration whatsoever.",
        ),
        ("user", "{input}"),
    ]
)
chain = prompt | ChatNVIDIA(model="meta/codellama-70b") | StrOutputParser()

for txt in chain.stream({"input": "How do I solve this fizz buzz problem?"}):
    print(txt, end="")


# ## Multimodal
# 
# NVIDIA also supports multimodal inputs, meaning you can provide both images and text for the model to reason over. An example model supporting multimodal inputs is `nvidia/neva-22b`.
# 
# Below is an example use:

# In[ ]:


import IPython
import requests

image_url = "https://www.nvidia.com/content/dam/en-zz/Solutions/research/ai-playground/nvidia-picasso-3c33-p@2x.jpg"  ## Large Image
image_content = requests.get(image_url).content

IPython.display.Image(image_content)


# In[ ]:


from langchain_nvidia_ai_endpoints import ChatNVIDIA

llm = ChatNVIDIA(model="nvidia/neva-22b")


# #### Passing an image as a URL

# In[ ]:


from langchain_core.messages import HumanMessage

llm.invoke(
    [
        HumanMessage(
            content=[
                {"type": "text", "text": "Describe this image:"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
    ]
)


# #### Passing an image as a base64 encoded string

# At the moment, some extra processing happens client-side to support larger images like the one above. But for smaller images (and to better illustrate the process going on under the hood), we can directly pass in the image as shown below:

# In[ ]:


import IPython
import requests

image_url = "https://picsum.photos/seed/kitten/300/200"
image_content = requests.get(image_url).content

IPython.display.Image(image_content)


# In[ ]:


import base64

from langchain_core.messages import HumanMessage

## Works for simpler images. For larger images, see actual implementation
b64_string = base64.b64encode(image_content).decode("utf-8")

llm.invoke(
    [
        HumanMessage(
            content=[
                {"type": "text", "text": "Describe this image:"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_string}"},
                },
            ]
        )
    ]
)


# #### Directly within the string
# 
# The NVIDIA API uniquely accepts images as base64 images inlined within `<img/>` HTML tags. While this isn't interoperable with other LLMs, you can directly prompt the model accordingly.

# In[ ]:


base64_with_mime_type = f"data:image/png;base64,{b64_string}"
llm.invoke(f'What\'s in this image?\n<img src="{base64_with_mime_type}" />')


# ## Example usage within a RunnableWithMessageHistory

# Like any other integration, ChatNVIDIA is fine to support chat utilities like RunnableWithMessageHistory which is analogous to using `ConversationChain`. Below, we show the [LangChain RunnableWithMessageHistory](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html) example applied to the `mistralai/mixtral-8x22b-instruct-v0.1` model.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain')


# In[ ]:


from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# store is a dictionary that maps session IDs to their corresponding chat histories.
store = {}  # memory is maintained outside the chain


# A function that returns the chat history for a given session ID.
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


chat = ChatNVIDIA(
    model="mistralai/mixtral-8x22b-instruct-v0.1",
    temperature=0.1,
    max_tokens=100,
    top_p=1.0,
)

#  Define a RunnableConfig object, with a `configurable` key. session_id determines thread
config = {"configurable": {"session_id": "1"}}

conversation = RunnableWithMessageHistory(
    chat,
    get_session_history,
)

conversation.invoke(
    "Hi I'm Srijan Dubey.",  # input or query
    config=config,
)


# In[ ]:


conversation.invoke(
    "I'm doing well! Just having a conversation with an AI.",
    config=config,
)


# In[ ]:


conversation.invoke(
    "Tell me about yourself.",
    config=config,
)


# ## Tool calling
# 
# Starting in v0.2, `ChatNVIDIA` supports [bind_tools](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.chat_models.BaseChatModel.html#langchain_core.language_models.chat_models.BaseChatModel.bind_tools).
# 
# `ChatNVIDIA` provides integration with the variety of models on [build.nvidia.com](https://build.nvidia.com) as well as local NIMs. Not all these models are trained for tool calling. Be sure to select a model that does have tool calling for your experimention and applications.

# You can get a list of models that are known to support tool calling with,

# In[ ]:


tool_models = [
    model for model in ChatNVIDIA.get_available_models() if model.supports_tools
]
tool_models


# With a tool capable model,

# In[ ]:


from langchain_core.tools import tool
from pydantic import Field


@tool
def get_current_weather(
    location: str = Field(..., description="The location to get the weather for."),
):
    """Get the current weather for a location."""
    ...


llm = ChatNVIDIA(model=tool_models[0].id).bind_tools(tools=[get_current_weather])
response = llm.invoke("What is the weather in Boston?")
response.tool_calls


# See [How to use chat models to call tools](https://python.langchain.com/docs/how_to/tool_calling/) for additional examples.

# ## Chaining
# 
# We can [chain](/docs/how_to/sequence/) our model with a prompt template like so:

# In[ ]:


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
chain.invoke(
    {
        "input_language": "English",
        "output_language": "German",
        "input": "I love programming.",
    }
)


# ## API reference
# 
# For detailed documentation of all `ChatNVIDIA` features and configurations head to the API reference: https://python.langchain.com/api_reference/nvidia_ai_endpoints/chat_models/langchain_nvidia_ai_endpoints.chat_models.ChatNVIDIA.html
