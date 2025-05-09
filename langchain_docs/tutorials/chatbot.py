#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 1
keywords: [conversationchain]
---
# # Build a Chatbot

# :::note
# 
# This tutorial previously used the [RunnableWithMessageHistory](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html) abstraction. You can access that version of the documentation in the [v0.2 docs](https://python.langchain.com/v0.2/docs/tutorials/chatbot/).
# 
# As of the v0.3 release of LangChain, we recommend that LangChain users take advantage of [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/) to incorporate `memory` into new LangChain applications.
# 
# If your code is already relying on `RunnableWithMessageHistory` or `BaseChatMessageHistory`, you do **not** need to make any changes. We do not plan on deprecating this functionality in the near future as it works for simple chat applications and any code that uses `RunnableWithMessageHistory` will continue to work as expected.
# 
# Please see [How to migrate to LangGraph Memory](/docs/versions/migrating_memory/) for more details.
# :::
# 
# ## Overview
# 
# We'll go over an example of how to design and implement an LLM-powered chatbot. 
# This chatbot will be able to have a conversation and remember previous interactions with a [chat model](/docs/concepts/chat_models).
# 
# 
# Note that this chatbot that we build will only use the language model to have a conversation.
# There are several other related concepts that you may be looking for:
# 
# - [Conversational RAG](/docs/tutorials/qa_chat_history): Enable a chatbot experience over an external source of data
# - [Agents](/docs/tutorials/agents): Build a chatbot that can take actions
# 
# This tutorial will cover the basics which will be helpful for those two more advanced topics, but feel free to skip directly to there should you choose.
# 
# ## Setup
# 
# ### Jupyter Notebook
# 
# This guide (and most of the other guides in the documentation) uses [Jupyter notebooks](https://jupyter.org/) and assumes the reader is as well. Jupyter notebooks are perfect for learning how to work with LLM systems because oftentimes things can go wrong (unexpected output, API down, etc) and going through guides in an interactive environment is a great way to better understand them.
# 
# This and other tutorials are perhaps most conveniently run in a Jupyter notebook. See [here](https://jupyter.org/install) for instructions on how to install.
# 
# ### Installation
# 
# For this tutorial we will need `langchain-core` and `langgraph`. This guide requires `langgraph >= 0.2.28`.
# 
# import Tabs from '@theme/Tabs';
# import TabItem from '@theme/TabItem';
# import CodeBlock from "@theme/CodeBlock";
# 
# <Tabs>
#   <TabItem value="pip" label="Pip" default>
#     <CodeBlock language="bash">pip install langchain-core langgraph>0.2.27</CodeBlock>
#   </TabItem>
#   <TabItem value="conda" label="Conda">
#     <CodeBlock language="bash">conda install langchain-core langgraph>0.2.27 -c conda-forge</CodeBlock>
#   </TabItem>
# </Tabs>
# 
# 
# 
# For more details, see our [Installation guide](/docs/how_to/installation).
# 
# ### LangSmith
# 
# Many of the applications you build with LangChain will contain multiple steps with multiple invocations of LLM calls.
# As these applications get more and more complex, it becomes crucial to be able to inspect what exactly is going on inside your chain or agent.
# The best way to do this is with [LangSmith](https://smith.langchain.com).
# 
# After you sign up at the link above, make sure to set your environment variables to start logging traces:
# 
# ```shell
# export LANGSMITH_TRACING="true"
# export LANGSMITH_API_KEY="..."
# ```
# 
# Or, if in a notebook, you can set them with:
# 
# ```python
# import getpass
# import os
# 
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()
# ```
# 
# ## Quickstart
# 
# First up, let's learn how to use a language model by itself. LangChain supports many different language models that you can use interchangeably - select the one you want to use below!
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs overrideParams={{openai: {model: "gpt-4o-mini"}}} />
# 

# In[2]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")


# Let's first use the model directly. `ChatModel`s are instances of LangChain "Runnables", which means they expose a standard interface for interacting with them. To just simply call the model, we can pass in a list of messages to the `.invoke` method.

# In[3]:


from langchain_core.messages import HumanMessage

model.invoke([HumanMessage(content="Hi! I'm Bob")])


# The model on its own does not have any concept of state. For example, if you ask a followup question:

# In[4]:


model.invoke([HumanMessage(content="What's my name?")])


# Let's take a look at the example [LangSmith trace](https://smith.langchain.com/public/5c21cb92-2814-4119-bae9-d02b8db577ac/r)
# 
# We can see that it doesn't take the previous conversation turn into context, and cannot answer the question.
# This makes for a terrible chatbot experience!
# 
# To get around this, we need to pass the entire [conversation history](/docs/concepts/chat_history) into the model. Let's see what happens when we do that:

# In[5]:


from langchain_core.messages import AIMessage

model.invoke(
    [
        HumanMessage(content="Hi! I'm Bob"),
        AIMessage(content="Hello Bob! How can I assist you today?"),
        HumanMessage(content="What's my name?"),
    ]
)


# And now we can see that we get a good response!
# 
# This is the basic idea underpinning a chatbot's ability to interact conversationally.
# So how do we best implement this?

# ## Message persistence
# 
# [LangGraph](https://langchain-ai.github.io/langgraph/) implements a built-in persistence layer, making it ideal for chat applications that support multiple conversational turns.
# 
# Wrapping our chat model in a minimal LangGraph application allows us to automatically persist the message history, simplifying the development of multi-turn applications.
# 
# LangGraph comes with a simple in-memory checkpointer, which we use below. See its [documentation](https://langchain-ai.github.io/langgraph/concepts/persistence/) for more detail, including how to use different persistence backends (e.g., SQLite or Postgres).

# In[6]:


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)


# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# We now need to create a `config` that we pass into the runnable every time. This config contains information that is not part of the input directly, but is still useful. In this case, we want to include a `thread_id`. This should look like:

# In[7]:


config = {"configurable": {"thread_id": "abc123"}}


# This enables us to support multiple conversation threads with a single application, a common requirement when your application has multiple users.
# 
# We can then invoke the application:

# In[8]:


query = "Hi! I'm Bob."

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
output["messages"][-1].pretty_print()  # output contains all messages in state


# In[9]:


query = "What's my name?"

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
output["messages"][-1].pretty_print()


# Great! Our chatbot now remembers things about us. If we change the config to reference a different `thread_id`, we can see that it starts the conversation fresh.

# In[10]:


config = {"configurable": {"thread_id": "abc234"}}

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
output["messages"][-1].pretty_print()


# However, we can always go back to the original conversation (since we are persisting it in a database)

# In[11]:


config = {"configurable": {"thread_id": "abc123"}}

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
output["messages"][-1].pretty_print()


# This is how we can support a chatbot having conversations with many users!
# 
# :::tip
# 
# For async support, update the `call_model` node to be an async function and use `.ainvoke` when invoking the application:
# 
# ```python
# # Async function for node:
# async def call_model(state: MessagesState):
#     response = await model.ainvoke(state["messages"])
#     return {"messages": response}
# 
# 
# # Define graph as before:
# workflow = StateGraph(state_schema=MessagesState)
# workflow.add_edge(START, "model")
# workflow.add_node("model", call_model)
# app = workflow.compile(checkpointer=MemorySaver())
# 
# # Async invocation:
# output = await app.ainvoke({"messages": input_messages}, config)
# output["messages"][-1].pretty_print()
# ```
# 
# :::

# Right now, all we've done is add a simple persistence layer around the model. We can start to make the chatbot more complicated and personalized by adding in a prompt template.
# 
# ## Prompt templates
# 
# [Prompt Templates](/docs/concepts/prompt_templates) help to turn raw user information into a format that the LLM can work with. In this case, the raw user input is just a message, which we are passing to the LLM. Let's now make that a bit more complicated. First, let's add in a system message with some custom instructions (but still taking messages as input). Next, we'll add in more input besides just the messages.
# 
# To add in a system message, we will create a `ChatPromptTemplate`. We will utilize `MessagesPlaceholder` to pass all the messages in.

# In[12]:


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You talk like a pirate. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


# We can now update our application to incorporate this template:

# In[13]:


workflow = StateGraph(state_schema=MessagesState)


def call_model(state: MessagesState):
    # highlight-start
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    # highlight-end
    return {"messages": response}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# We invoke the application in the same way:

# In[14]:


config = {"configurable": {"thread_id": "abc345"}}
query = "Hi! I'm Jim."

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
output["messages"][-1].pretty_print()


# In[15]:


query = "What is my name?"

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
output["messages"][-1].pretty_print()


# Awesome! Let's now make our prompt a little bit more complicated. Let's assume that the prompt template now looks something like this:

# In[19]:


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


# Note that we have added a new `language` input to the prompt. Our application now has two parameters-- the input `messages` and `language`. We should update our application's state to reflect this:

# In[20]:


from typing import Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict


# highlight-next-line
class State(TypedDict):
    # highlight-next-line
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # highlight-next-line
    language: str


workflow = StateGraph(state_schema=State)


def call_model(state: State):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response]}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# In[21]:


config = {"configurable": {"thread_id": "abc456"}}
query = "Hi! I'm Bob."
language = "Spanish"

input_messages = [HumanMessage(query)]
output = app.invoke(
    # highlight-next-line
    {"messages": input_messages, "language": language},
    config,
)
output["messages"][-1].pretty_print()


# Note that the entire state is persisted, so we can omit parameters like `language` if no changes are desired:

# In[22]:


query = "What is my name?"

input_messages = [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages},
    config,
)
output["messages"][-1].pretty_print()


# To help you understand what's happening internally, check out [this LangSmith trace](https://smith.langchain.com/public/15bd8589-005c-4812-b9b9-23e74ba4c3c6/r).

# ## Managing Conversation History
# 
# One important concept to understand when building chatbots is how to manage conversation history. If left unmanaged, the list of messages will grow unbounded and potentially overflow the context window of the LLM. Therefore, it is important to add a step that limits the size of the messages you are passing in.
# 
# **Importantly, you will want to do this BEFORE the prompt template but AFTER you load previous messages from Message History.**
# 
# We can do this by adding a simple step in front of the prompt that modifies the `messages` key appropriately, and then wrap that new chain in the Message History class. 
# 
# LangChain comes with a few built-in helpers for [managing a list of messages](/docs/how_to/#messages). In this case we'll use the [trim_messages](/docs/how_to/trim_messages/) helper to reduce how many messages we're sending to the model. The trimmer allows us to specify how many tokens we want to keep, along with other parameters like if we want to always keep the system message and whether to allow partial messages:

# In[23]:


from langchain_core.messages import SystemMessage, trim_messages

trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

messages = [
    SystemMessage(content="you're a good assistant"),
    HumanMessage(content="hi! I'm bob"),
    AIMessage(content="hi!"),
    HumanMessage(content="I like vanilla ice cream"),
    AIMessage(content="nice"),
    HumanMessage(content="whats 2 + 2"),
    AIMessage(content="4"),
    HumanMessage(content="thanks"),
    AIMessage(content="no problem!"),
    HumanMessage(content="having fun?"),
    AIMessage(content="yes!"),
]

trimmer.invoke(messages)


# To  use it in our chain, we just need to run the trimmer before we pass the `messages` input to our prompt. 

# In[24]:


workflow = StateGraph(state_schema=State)


def call_model(state: State):
    # highlight-start
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke(
        {"messages": trimmed_messages, "language": state["language"]}
    )
    response = model.invoke(prompt)
    # highlight-end
    return {"messages": [response]}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# Now if we try asking the model our name, it won't know it since we trimmed that part of the chat history:

# In[25]:


config = {"configurable": {"thread_id": "abc567"}}
query = "What is my name?"
language = "English"

# highlight-next-line
input_messages = messages + [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages, "language": language},
    config,
)
output["messages"][-1].pretty_print()


# But if we ask about information that is within the last few messages, it remembers:

# In[26]:


config = {"configurable": {"thread_id": "abc678"}}
query = "What math problem did I ask?"
language = "English"

input_messages = messages + [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages, "language": language},
    config,
)
output["messages"][-1].pretty_print()


# If you take a look at LangSmith, you can see exactly what is happening under the hood in the [LangSmith trace](https://smith.langchain.com/public/04402eaa-29e6-4bb1-aa91-885b730b6c21/r).

# ## Streaming
# 
# Now we've got a functioning chatbot. However, one *really* important UX consideration for chatbot applications is streaming. LLMs can sometimes take a while to respond, and so in order to improve the user experience one thing that most applications do is stream back each token as it is generated. This allows the user to see progress.
# 
# It's actually super easy to do this!
# 
# By default, `.stream` in our LangGraph application streams application steps-- in this case, the single step of the model response. Setting `stream_mode="messages"` allows us to stream output tokens instead:

# In[27]:


config = {"configurable": {"thread_id": "abc789"}}
query = "Hi I'm Todd, please tell me a joke."
language = "English"

input_messages = [HumanMessage(query)]
# highlight-next-line
for chunk, metadata in app.stream(
    {"messages": input_messages, "language": language},
    config,
    # highlight-next-line
    stream_mode="messages",
):
    if isinstance(chunk, AIMessage):  # Filter to just model responses
        print(chunk.content, end="|")


# ## Next Steps
# 
# Now that you understand the basics of how to create a chatbot in LangChain, some more advanced tutorials you may be interested in are:
# 
# - [Conversational RAG](/docs/tutorials/qa_chat_history): Enable a chatbot experience over an external source of data
# - [Agents](/docs/tutorials/agents): Build a chatbot that can take actions
# 
# If you want to dive deeper on specifics, some things worth checking out are:
# 
# - [Streaming](/docs/how_to/streaming): streaming is *crucial* for chat applications
# - [How to add message history](/docs/how_to/message_history): for a deeper dive into all things related to message history
# - [How to manage large message history](/docs/how_to/trim_messages/): more techniques for managing a large chat history
# - [LangGraph main docs](https://langchain-ai.github.io/langgraph/): for more detail on building with LangGraph
