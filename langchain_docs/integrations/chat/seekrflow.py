#!/usr/bin/env python
# coding: utf-8

# # ChatSeekrFlow
# 
# > [Seekr](https://www.seekr.com/) provides AI-powered solutions for structured, explainable, and transparent AI interactions.
# 
# This notebook provides a quick overview for getting started with Seekr [chat models](/docs/concepts/chat_models). For detailed documentation of all `ChatSeekrFlow` features and configurations, head to the [API reference](https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.seekrflow.ChatSeekrFlow.html).
# 
# ## Overview
# 
# `ChatSeekrFlow` class wraps a chat model endpoint hosted on SeekrFlow, enabling seamless integration with LangChain applications.
# 
# ### Integration Details
# 
# | Class | Package | Local | Serializable | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: |
# | [ChatSeekrFlow](https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.seekrflow.ChatSeekrFlow.html) | [seekrai](https://python.langchain.com/docs/integrations/providers/seekr/) | ❌ | beta | ![PyPI - Downloads](https://img.shields.io/pypi/dm/seekrai?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/seekrai?style=flat-square&label=%20) |
# 
# ### Model Features
# 
# | [Tool calling](/docs/how_to/tool_calling/) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
# 
# ### Supported Methods
# `ChatSeekrFlow` supports all methods of `ChatModel`, **except async APIs**.
# 
# ### Endpoint Requirements
# 
# The serving endpoint `ChatSeekrFlow` wraps **must** have OpenAI-compatible chat input/output format. It can be used for:
# 1. **Fine-tuned Seekr models**
# 2. **Custom SeekrFlow models**
# 3. **RAG-enabled models using Seekr's retrieval system**
# 
# For async usage, please refer to `AsyncChatSeekrFlow` (coming soon).
# 

# # Getting Started with ChatSeekrFlow in LangChain
# 
# This notebook covers how to use SeekrFlow as a chat model in LangChain.

# ## Setup
# 
# Ensure you have the necessary dependencies installed:
# 
# ```bash
# pip install seekrai langchain langchain-community
# ```
# 
# You must also have an API key from Seekr to authenticate requests.
# 

# In[1]:


# Standard library
import getpass
import os

# Third-party
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain_core.runnables import RunnableSequence

# OSS SeekrFlow integration
from langchain_seekrflow import ChatSeekrFlow
from seekrai import SeekrFlow


# ## API Key Setup
# 
# You'll need to set your API key as an environment variable to authenticate requests.
# 
# Run the below cell.
# 
# Or manually assign it before running queries:
# 
# ```python
# SEEKR_API_KEY = "your-api-key-here"
# ```
# 

# In[ ]:


os.environ["SEEKR_API_KEY"] = getpass.getpass("Enter your Seekr API key:")


# ## Instantiation

# In[ ]:


os.environ["SEEKR_API_KEY"]
seekr_client = SeekrFlow(api_key=SEEKR_API_KEY)

llm = ChatSeekrFlow(
    client=seekr_client, model_name="meta-llama/Meta-Llama-3-8B-Instruct"
)


# ## Invocation

# In[4]:


response = llm.invoke([HumanMessage(content="Hello, Seekr!")])
print(response.content)


# ## Chaining

# In[5]:


prompt = ChatPromptTemplate.from_template("Translate to French: {text}")

chain: RunnableSequence = prompt | llm
result = chain.invoke({"text": "Good morning"})
print(result)


# In[6]:


def test_stream():
    """Test synchronous invocation in streaming mode."""
    print("\n🔹 Testing Sync `stream()` (Streaming)...")

    for chunk in llm.stream([HumanMessage(content="Write me a haiku.")]):
        print(chunk.content, end="", flush=True)


# ✅ Ensure streaming is enabled
llm = ChatSeekrFlow(
    client=seekr_client,
    model_name="meta-llama/Meta-Llama-3-8B-Instruct",
    streaming=True,  # ✅ Enable streaming
)

# ✅ Run sync streaming test
test_stream()


# ## Error Handling & Debugging

# In[8]:


# Define a minimal mock SeekrFlow client
class MockSeekrClient:
    """Mock SeekrFlow API client that mimics the real API structure."""

    class MockChat:
        """Mock Chat object with a completions method."""

        class MockCompletions:
            """Mock Completions object with a create method."""

            def create(self, *args, **kwargs):
                return {
                    "choices": [{"message": {"content": "Mock response"}}]
                }  # Mimic API response

        completions = MockCompletions()

    chat = MockChat()


def test_initialization_errors():
    """Test that invalid ChatSeekrFlow initializations raise expected errors."""

    test_cases = [
        {
            "name": "Missing Client",
            "args": {"client": None, "model_name": "seekrflow-model"},
            "expected_error": "SeekrFlow client cannot be None.",
        },
        {
            "name": "Missing Model Name",
            "args": {"client": MockSeekrClient(), "model_name": ""},
            "expected_error": "A valid model name must be provided.",
        },
    ]

    for test in test_cases:
        try:
            print(f"Running test: {test['name']}")
            faulty_llm = ChatSeekrFlow(**test["args"])

            # If no error is raised, fail the test
            print(f"❌ Test '{test['name']}' failed: No error was raised!")
        except Exception as e:
            error_msg = str(e)
            assert test["expected_error"] in error_msg, f"Unexpected error: {error_msg}"
            print(f"✅ Expected Error: {error_msg}")


# Run test
test_initialization_errors()


# ## API reference

# - `ChatSeekrFlow` class: [`langchain_seekrflow.ChatSeekrFlow`](https://github.com/benfaircloth/langchain-seekrflow/blob/main/langchain_seekrflow/seekrflow.py)
# - PyPI package: [`langchain-seekrflow`](https://pypi.org/project/langchain-seekrflow/)
# 

# 
