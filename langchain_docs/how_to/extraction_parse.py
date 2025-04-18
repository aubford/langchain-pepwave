#!/usr/bin/env python
# coding: utf-8

# # How to use prompting alone (no tool calling) to do extraction
# 
# [Tool calling](/docs/concepts/tool_calling/) features are not required for generating structured output from LLMs. LLMs that are able to follow prompt instructions well can be tasked with outputting information in a given format.
# 
# This approach relies on designing good prompts and then parsing the output of the LLMs to make them extract information well.
# 
# To extract data without tool-calling features: 
# 
# 1. Instruct the LLM to generate text following an expected format (e.g., JSON with a certain schema);
# 2. Use [output parsers](/docs/concepts/output_parsers) to structure the model response into a desired Python object.
# 
# First we select a LLM:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="model" />
# 

# In[1]:


# | output: false
# | echo: false

from langchain_anthropic.chat_models import ChatAnthropic

model = ChatAnthropic(model_name="claude-3-sonnet-20240229", temperature=0)


# :::tip
# This tutorial is meant to be simple, but generally should really include reference examples to squeeze out performance!
# :::

# ## Using PydanticOutputParser
# 
# The following example uses the built-in `PydanticOutputParser` to parse the output of a chat model.

# In[2]:


from typing import List, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, validator


class Person(BaseModel):
    """Information about a person."""

    name: str = Field(..., description="The name of the person")
    height_in_meters: float = Field(
        ..., description="The height of the person expressed in meters."
    )


class People(BaseModel):
    """Identifying information about all people in a text."""

    people: List[Person]


# Set up a parser
parser = PydanticOutputParser(pydantic_object=People)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Wrap the output in `json` tags\n{format_instructions}",
        ),
        ("human", "{query}"),
    ]
).partial(format_instructions=parser.get_format_instructions())


# Let's take a look at what information is sent to the model

# In[3]:


query = "Anna is 23 years old and she is 6 feet tall"


# In[4]:


print(prompt.format_prompt(query=query).to_string())


# Having defined our prompt, we simply chain together the prompt, model and output parser:

# In[5]:


chain = prompt | model | parser
chain.invoke({"query": query})


# Check out the associated [Langsmith trace](https://smith.langchain.com/public/92ed52a3-92b9-45af-a663-0a9c00e5e396/r).
# 
# Note that the schema shows up in two places: 
# 
# 1. In the prompt, via `parser.get_format_instructions()`;
# 2. In the chain, to receive the formatted output and structure it into a Python object (in this case, the Pydantic object `People`).

# ## Custom Parsing
# 
# If desired, it's easy to create a custom prompt and parser with `LangChain` and `LCEL`.
# 
# To create a custom parser, define a function to parse the output from the model (typically an [AIMessage](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.AIMessage.html)) into an object of your choice.
# 
# See below for a simple implementation of a JSON parser.

# In[6]:


import json
import re
from typing import List, Optional

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, validator


class Person(BaseModel):
    """Information about a person."""

    name: str = Field(..., description="The name of the person")
    height_in_meters: float = Field(
        ..., description="The height of the person expressed in meters."
    )


class People(BaseModel):
    """Identifying information about all people in a text."""

    people: List[Person]


# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user query. Output your answer as JSON that  "
            "matches the given schema: ```json\n{schema}\n```. "
            "Make sure to wrap the answer in ```json and ``` tags",
        ),
        ("human", "{query}"),
    ]
).partial(schema=People.schema())


# Custom parser
def extract_json(message: AIMessage) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json and ``` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON strings.
    """
    text = message.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        return [json.loads(match.strip()) for match in matches]
    except Exception:
        raise ValueError(f"Failed to parse: {message}")


# In[7]:


query = "Anna is 23 years old and she is 6 feet tall"
print(prompt.format_prompt(query=query).to_string())


# In[8]:


chain = prompt | model | extract_json
chain.invoke({"query": query})


# ## Other Libraries
# 
# If you're looking at extracting using a parsing approach, check out the [Kor](https://eyurtsev.github.io/kor/) library. It's written by one of the `LangChain` maintainers and it
# helps to craft a prompt that takes examples into account, allows controlling formats (e.g., JSON or CSV) and expresses the schema in TypeScript. It seems to work pretty!
