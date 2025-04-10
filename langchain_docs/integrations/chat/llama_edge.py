#!/usr/bin/env python
# coding: utf-8

# # LlamaEdge
# 
# [LlamaEdge](https://github.com/second-state/LlamaEdge) allows you to chat with LLMs of [GGUF](https://github.com/ggerganov/llama.cpp/blob/master/gguf-py/README.md) format both locally and via chat service.
# 
# - `LlamaEdgeChatService` provides developers an OpenAI API compatible service to chat with LLMs via HTTP requests.
# 
# - `LlamaEdgeChatLocal` enables developers to chat with LLMs locally (coming soon).
# 
# Both `LlamaEdgeChatService` and `LlamaEdgeChatLocal` run on the infrastructure driven by [WasmEdge Runtime](https://wasmedge.org/), which provides a lightweight and portable WebAssembly container environment for LLM inference tasks.
# 
# ## Chat via API Service
# 
# `LlamaEdgeChatService` works on the `llama-api-server`. Following the steps in [llama-api-server quick-start](https://github.com/second-state/llama-utils/tree/main/api-server#readme), you can host your own API service so that you can chat with any models you like on any device you have anywhere as long as the internet is available.

# In[2]:


from langchain_community.chat_models.llama_edge import LlamaEdgeChatService
from langchain_core.messages import HumanMessage, SystemMessage


# ### Chat with LLMs in the non-streaming mode

# In[5]:


# service url
service_url = "https://b008-54-186-154-209.ngrok-free.app"

# create wasm-chat service instance
chat = LlamaEdgeChatService(service_url=service_url)

# create message sequence
system_message = SystemMessage(content="You are an AI assistant")
user_message = HumanMessage(content="What is the capital of France?")
messages = [system_message, user_message]

# chat with wasm-chat service
response = chat.invoke(messages)

print(f"[Bot] {response.content}")


# ### Chat with LLMs in the streaming mode

# In[4]:


# service url
service_url = "https://b008-54-186-154-209.ngrok-free.app"

# create wasm-chat service instance
chat = LlamaEdgeChatService(service_url=service_url, streaming=True)

# create message sequence
system_message = SystemMessage(content="You are an AI assistant")
user_message = HumanMessage(content="What is the capital of Norway?")
messages = [
    system_message,
    user_message,
]

output = ""
for chunk in chat.stream(messages):
    # print(chunk.content, end="", flush=True)
    output += chunk.content

print(f"[Bot] {output}")

