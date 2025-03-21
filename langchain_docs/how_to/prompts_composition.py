#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 5
---
# # How to compose prompts together
# 
# :::info Prerequisites
# 
# This guide assumes familiarity with the following concepts:
# - [Prompt templates](/docs/concepts/prompt_templates)
# 
# :::
# 
# LangChain provides a user friendly interface for composing different parts of [prompts](/docs/concepts/prompt_templates/) together. You can do this with either string prompts or chat prompts. Constructing prompts this way allows for easy reuse of components.

# ## String prompt composition
# 
# When working with string prompts, each template is joined together. You can work with either prompts directly or strings (the first element in the list needs to be a prompt).

# In[1]:


from langchain_core.prompts import PromptTemplate

prompt = (
    PromptTemplate.from_template("Tell me a joke about {topic}")
    + ", make it funny"
    + "\n\nand in {language}"
)

prompt


# In[2]:


prompt.format(topic="sports", language="spanish")


# ## Chat prompt composition

# A chat prompt is made up a of a list of messages. Similarly to the above example, we can concatenate chat prompt templates. Each new element is a new message in the final prompt.
# 
# First, let's initialize the a [`ChatPromptTemplate`](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.ChatPromptTemplate.html) with a [`SystemMessage`](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.system.SystemMessage.html).

# In[3]:


from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

prompt = SystemMessage(content="You are a nice pirate")


# You can then easily create a pipeline combining it with other messages *or* message templates.
# Use a `Message` when there is no variables to be formatted, use a `MessageTemplate` when there are variables to be formatted. You can also use just a string (note: this will automatically get inferred as a [`HumanMessagePromptTemplate`](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.HumanMessagePromptTemplate.html).)

# In[4]:


new_prompt = (
    prompt + HumanMessage(content="hi") + AIMessage(content="what?") + "{input}"
)


# Under the hood, this creates an instance of the ChatPromptTemplate class, so you can use it just as you did before!

# In[5]:


new_prompt.format_messages(input="i said hi")


# ## Using PipelinePrompt

# LangChain includes a class called [`PipelinePromptTemplate`](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.pipeline.PipelinePromptTemplate.html), which can be useful when you want to reuse parts of prompts. A PipelinePrompt consists of two main parts:
# 
# - Final prompt: The final prompt that is returned
# - Pipeline prompts: A list of tuples, consisting of a string name and a prompt template. Each prompt template will be formatted and then passed to future prompt templates as a variable with the same name.

# In[6]:


from langchain_core.prompts import PipelinePromptTemplate, PromptTemplate

full_template = """{introduction}

{example}

{start}"""
full_prompt = PromptTemplate.from_template(full_template)

introduction_template = """You are impersonating {person}."""
introduction_prompt = PromptTemplate.from_template(introduction_template)

example_template = """Here's an example of an interaction:

Q: {example_q}
A: {example_a}"""
example_prompt = PromptTemplate.from_template(example_template)

start_template = """Now, do this for real!

Q: {input}
A:"""
start_prompt = PromptTemplate.from_template(start_template)

input_prompts = [
    ("introduction", introduction_prompt),
    ("example", example_prompt),
    ("start", start_prompt),
]
pipeline_prompt = PipelinePromptTemplate(
    final_prompt=full_prompt, pipeline_prompts=input_prompts
)

pipeline_prompt.input_variables


# In[7]:


print(
    pipeline_prompt.format(
        person="Elon Musk",
        example_q="What's your favorite car?",
        example_a="Tesla",
        input="What's your favorite social media site?",
    )
)


# ## Next steps
# 
# You've now learned how to compose prompts together.
# 
# Next, check out the other how-to guides on prompt templates in this section, like [adding few-shot examples to your prompt templates](/docs/how_to/few_shot_examples_chat).
