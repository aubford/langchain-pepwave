#!/usr/bin/env python
# coding: utf-8

# # RunPod LLM

# Get started with RunPod LLMs.
# 
# ## Overview
# 
# This guide covers how to use the LangChain `RunPod` LLM class to interact with text generation models hosted on [RunPod Serverless](https://www.runpod.io/serverless-gpu).

# ## Setup
# 
# 1. **Install the package:**
#    ```bash
#    pip install -qU langchain-runpod
#    ```
# 2. **Deploy an LLM Endpoint:** Follow the setup steps in the [RunPod Provider Guide](/docs/integrations/providers/runpod#setup) to deploy a compatible text generation endpoint on RunPod Serverless and get its Endpoint ID.
# 3. **Set Environment Variables:** Make sure `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID` are set.

# In[ ]:


import getpass
import os

# Make sure environment variables are set (or pass them directly to RunPod)
if "RUNPOD_API_KEY" not in os.environ:
    os.environ["RUNPOD_API_KEY"] = getpass.getpass("Enter your RunPod API Key: ")
if "RUNPOD_ENDPOINT_ID" not in os.environ:
    os.environ["RUNPOD_ENDPOINT_ID"] = input("Enter your RunPod Endpoint ID: ")


# ## Instantiation
# 
# Initialize the `RunPod` class. You can pass model-specific parameters via `model_kwargs` and configure polling behavior.

# In[ ]:


from langchain_runpod import RunPod

llm = RunPod(
    # runpod_endpoint_id can be passed here if not set in env
    model_kwargs={
        "max_new_tokens": 256,
        "temperature": 0.6,
        "top_k": 50,
        # Add other parameters supported by your endpoint handler
    },
    # Optional: Adjust polling
    # poll_interval=0.3,
    # max_polling_attempts=100
)


# ## Invocation
# 
# Use the standard LangChain `.invoke()` and `.ainvoke()` methods to call the model. Streaming is also supported via `.stream()` and `.astream()` (simulated by polling the RunPod `/stream` endpoint).

# In[ ]:


prompt = "Write a tagline for an ice cream shop on the moon."

# Invoke (Sync)
try:
    response = llm.invoke(prompt)
    print("--- Sync Invoke Response ---")
    print(response)
except Exception as e:
    print(
        f"Error invoking LLM: {e}. Ensure endpoint ID/API key are correct and endpoint is active/compatible."
    )


# In[ ]:


# Stream (Sync, simulated via polling /stream)
print("\n--- Sync Stream Response ---")
try:
    for chunk in llm.stream(prompt):
        print(chunk, end="", flush=True)
    print()  # Newline
except Exception as e:
    print(
        f"\nError streaming LLM: {e}. Ensure endpoint handler supports streaming output format."
    )


# ### Async Usage

# In[ ]:


# AInvoke (Async)
try:
    async_response = await llm.ainvoke(prompt)
    print("--- Async Invoke Response ---")
    print(async_response)
except Exception as e:
    print(f"Error invoking LLM asynchronously: {e}.")


# In[ ]:


# AStream (Async)
print("\n--- Async Stream Response ---")
try:
    async for chunk in llm.astream(prompt):
        print(chunk, end="", flush=True)
    print()  # Newline
except Exception as e:
    print(
        f"\nError streaming LLM asynchronously: {e}. Ensure endpoint handler supports streaming output format."
    )


# ## Chaining
# 
# The LLM integrates seamlessly with LangChain Expression Language (LCEL) chains.

# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# Assumes 'llm' variable is instantiated from the 'Instantiation' cell
prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")
parser = StrOutputParser()

chain = prompt_template | llm | parser

try:
    chain_response = chain.invoke({"topic": "bears"})
    print("--- Chain Response ---")
    print(chain_response)
except Exception as e:
    print(f"Error running chain: {e}")

# Async chain
try:
    async_chain_response = await chain.ainvoke({"topic": "robots"})
    print("--- Async Chain Response ---")
    print(async_chain_response)
except Exception as e:
    print(f"Error running async chain: {e}")


# ## Endpoint Considerations
# 
# - **Input:** The endpoint handler should expect the prompt string within `{"input": {"prompt": "...", ...}}`.
# - **Output:** The handler should return the generated text within the `"output"` key of the final status response (e.g., `{"output": "Generated text..."}` or `{"output": {"text": "..."}}`).
# - **Streaming:** For simulated streaming via the `/stream` endpoint, the handler must populate the `"stream"` key in the status response with a list of chunk dictionaries, like `[{"output": "token1"}, {"output": "token2"}]`.

# ## API reference
# 
# For detailed documentation of the `RunPod` LLM class, parameters, and methods, refer to the source code or the generated API reference (if available).
# 
# Link to source code: [https://github.com/runpod/langchain-runpod/blob/main/langchain_runpod/llms.py](https://github.com/runpod/langchain-runpod/blob/main/langchain_runpod/llms.py)
