#!/usr/bin/env python
# coding: utf-8

# # Outlines
# 
# This will help you getting started with Outlines LLM. For detailed documentation of all Outlines features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/llms/langchain_community.llms.outlines.Outlines.html).
# 
# [Outlines](https://github.com/outlines-dev/outlines) is a library for constrained language generation. It allows you to use large language models (LLMs) with various backends while applying constraints to the generated output.
# 
# ## Overview
# 
# ### Integration details
# | Class | Package | Local | Serializable | JS support | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [Outlines](https://python.langchain.com/api_reference/community/llms/langchain_community.llms.outlines.Outlines.html) | [langchain-community](https://python.langchain.com/api_reference/community/index.html) | ✅ | beta | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-community?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-community?style=flat-square&label=%20) |
# 
# ## Setup
# 
# To access Outlines models you'll need to have an internet connection to download the model weights from huggingface. Depending on the backend you need to install the required dependencies (see [Outlines docs](https://dottxt-ai.github.io/outlines/latest/installation/))
# 
# ### Credentials
# 
# There is no built-in auth mechanism for Outlines.
# 
# ## Installation
# 
# The LangChain Outlines integration lives in the `langchain-community` package and requires the `outlines` library:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community outlines')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[ ]:


from langchain_community.llms import Outlines

# For use with llamacpp backend
model = Outlines(model="microsoft/Phi-3-mini-4k-instruct", backend="llamacpp")

# For use with vllm backend (not available on Mac)
model = Outlines(model="microsoft/Phi-3-mini-4k-instruct", backend="vllm")

# For use with mlxlm backend (only available on Mac)
model = Outlines(model="microsoft/Phi-3-mini-4k-instruct", backend="mlxlm")

# For use with huggingface transformers backend
model = Outlines(
    model="microsoft/Phi-3-mini-4k-instruct"
)  # defaults to backend="transformers"


# ## Invocation

# In[ ]:


model.invoke("Hello how are you?")


# ## Chaining

# In[ ]:


from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("How to say {input} in {output_language}:\n")

chain = prompt | model
chain.invoke(
    {
        "output_language": "German",
        "input": "I love programming.",
    }
)


# ### Streaming
# 
# Outlines supports streaming of tokens:

# In[ ]:


for chunk in model.stream("Count to 10 in French:"):
    print(chunk, end="", flush=True)


# ### Constrained Generation
# 
# Outlines allows you to apply various constraints to the generated output:
# 
# #### Regex Constraint

# In[ ]:


model.regex = r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)"
response = model.invoke("What is the IP address of Google's DNS server?")

response


# ### Type Constraints

# In[ ]:


model.type_constraints = int
response = model.invoke("What is the answer to life, the universe, and everything?")


# #### JSON Schema

# In[ ]:


from pydantic import BaseModel


class Person(BaseModel):
    name: str


model.json_schema = Person
response = model.invoke("Who is the author of LangChain?")
person = Person.model_validate_json(response)

person


# #### Grammar Constraint

# In[ ]:


model.grammar = """
?start: expression
?expression: term (("+" | "-") term)
?term: factor (("" | "/") factor)
?factor: NUMBER | "-" factor | "(" expression ")"
%import common.NUMBER
%import common.WS
%ignore WS
"""
response = model.invoke("Give me a complex arithmetic expression:")

response


# ## API reference
# 
# For detailed documentation of all ChatOutlines features and configurations head to the API reference: https://python.langchain.com/api_reference/community/chat_models/langchain_community.chat_models.outlines.ChatOutlines.html
# 
# ## Outlines Documentation: 
# 
# https://dottxt-ai.github.io/outlines/latest/
