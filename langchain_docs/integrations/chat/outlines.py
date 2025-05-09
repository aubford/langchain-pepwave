#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Outlines
---
# # ChatOutlines
# 
# This will help you getting started with Outlines [chat models](/docs/concepts/chat_models/). For detailed documentation of all ChatOutlines features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.outlines.ChatOutlines.html).
# 
# [Outlines](https://github.com/outlines-dev/outlines) is a library for constrained language generation. It allows you to use large language models (LLMs) with various backends while applying constraints to the generated output.
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatOutlines](https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.outlines.ChatOutlines.html) | [langchain-community](https://python.langchain.com/api_reference/community/index.html) | ✅ | ❌ | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-community?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-community?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | 
# 
# ## Setup
# 
# To access Outlines models you'll need to have an internet connection to download the model weights from huggingface. Depending on the backend you need to install the required dependencies (see [Outlines docs](https://dottxt-ai.github.io/outlines/latest/installation/))
# 
# ### Credentials
# 
# There is no built-in auth mechanism for Outlines.
# 
# ### Installation
# 
# The LangChain Outlines integration lives in the `langchain-community` package and requires the `outlines` library:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community outlines')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[ ]:


from langchain_community.chat_models.outlines import ChatOutlines

# For llamacpp backend
model = ChatOutlines(model="TheBloke/phi-2-GGUF/phi-2.Q4_K_M.gguf", backend="llamacpp")

# For vllm backend (not available on Mac)
model = ChatOutlines(model="meta-llama/Llama-3.2-1B", backend="vllm")

# For mlxlm backend (only available on Mac)
model = ChatOutlines(model="mistralai/Ministral-8B-Instruct-2410", backend="mlxlm")

# For huggingface transformers backend
model = ChatOutlines(model="microsoft/phi-2")  # defaults to transformers backend


# ## Invocation

# In[ ]:


from langchain_core.messages import HumanMessage

messages = [HumanMessage(content="What will the capital of mars be called?")]
response = model.invoke(messages)

response.content


# ## Streaming
# 
# ChatOutlines supports streaming of tokens:

# In[ ]:


messages = [HumanMessage(content="Count to 10 in French:")]

for chunk in model.stream(messages):
    print(chunk.content, end="", flush=True)


# ## Chaining

# In[ ]:


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | model
chain.invoke(
    {
        "input_language": "English",
        "output_language": "German",
        "input": "I love programming.",
    }
)


# ## Constrained Generation
# 
# ChatOutlines allows you to apply various constraints to the generated output:
# 
# ### Regex Constraint

# In[ ]:


model.regex = r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)"

response = model.invoke("What is the IP address of Google's DNS server?")

response.content


# ### Type Constraints

# In[ ]:


model.type_constraints = int
response = model.invoke("What is the answer to life, the universe, and everything?")

response.content


# ### Pydantic and JSON Schemas

# In[ ]:


from pydantic import BaseModel


class Person(BaseModel):
    name: str


model.json_schema = Person
response = model.invoke("Who are the main contributors to LangChain?")
person = Person.model_validate_json(response.content)

person


# ### Context Free Grammars

# In[ ]:


model.grammar = """
?start: expression
?expression: term (("+" | "-") term)*
?term: factor (("*" | "/") factor)*
?factor: NUMBER | "-" factor | "(" expression ")"
%import common.NUMBER
%import common.WS
%ignore WS
"""
response = model.invoke("Give me a complex arithmetic expression:")

response.content


# ## LangChain's Structured Output
# 
# You can also use LangChain's Structured Output with ChatOutlines:

# In[ ]:


from pydantic import BaseModel


class AnswerWithJustification(BaseModel):
    answer: str
    justification: str


_model = model.with_structured_output(AnswerWithJustification)
result = _model.invoke("What weighs more, a pound of bricks or a pound of feathers?")

result


# ## API reference
# 
# For detailed documentation of all ChatOutlines features and configurations head to the API reference: https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.outlines.ChatOutlines.html
# 
# ## Full Outlines Documentation: 
# 
# https://dottxt-ai.github.io/outlines/latest/
