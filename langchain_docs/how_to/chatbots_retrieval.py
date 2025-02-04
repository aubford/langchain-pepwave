#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 2
---
# # How to add retrieval to chatbots
# 
# [Retrieval](/docs/concepts/retrieval/) is a common technique chatbots use to augment their responses with data outside a chat model's training data. This section will cover how to implement retrieval in the context of chatbots, but it's worth noting that retrieval is a very subtle and deep topic - we encourage you to explore [other parts of the documentation](/docs/how_to#qa-with-rag) that go into greater depth!
# 
# ## Setup
# 
# You'll need to install a few packages, and have your OpenAI API key set as an environment variable named `OPENAI_API_KEY`:

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain-openai langchain-chroma beautifulsoup4')

# Set env var OPENAI_API_KEY or load from a .env file:
import dotenv

dotenv.load_dotenv()


# Let's also set up a chat model that we'll use for the below examples.

# In[2]:


from langchain_openai import ChatOpenAI

chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


# ## Creating a retriever
# 
# We'll use [the LangSmith documentation](https://docs.smith.langchain.com/overview) as source material and store the content in a [vector store](/docs/concepts/vectorstores/) for later retrieval. Note that this example will gloss over some of the specifics around parsing and storing a data source - you can see more [in-depth documentation on creating retrieval systems here](/docs/how_to#qa-with-rag).
# 
# Let's use a document loader to pull text from the docs:

# In[3]:


from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.smith.langchain.com/overview")
data = loader.load()


# Next, we split it into smaller chunks that the LLM's context window can handle and store it in a vector database:

# In[4]:


from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)


# Then we embed and store those chunks in a vector database:

# In[5]:


from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())


# And finally, let's create a retriever from our initialized vectorstore:

# In[6]:


# k is the number of chunks to retrieve
retriever = vectorstore.as_retriever(k=4)

docs = retriever.invoke("Can LangSmith help test my LLM applications?")

docs


# We can see that invoking the retriever above results in some parts of the LangSmith docs that contain information about testing that our chatbot can use as context when answering questions. And now we've got a retriever that can return related data from the LangSmith docs!
# 
# ## Document chains
# 
# Now that we have a retriever that can return LangChain docs, let's create a chain that can use them as context to answer questions. We'll use a `create_stuff_documents_chain` helper function to "stuff" all of the input documents into the prompt. It will also handle formatting the docs as strings.
# 
# In addition to a chat model, the function also expects a prompt that has a `context` variables, as well as a placeholder for chat history messages named `messages`. We'll create an appropriate prompt and pass it as shown below:

# In[7]:


from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_TEMPLATE = """
Answer the user's questions based on the below context. 
If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

<context>
{context}
</context>
"""

question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_TEMPLATE,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

document_chain = create_stuff_documents_chain(chat, question_answering_prompt)


# We can invoke this `document_chain` by itself to answer questions. Let's use the docs we retrieved above and the same question, `how can langsmith help with testing?`:

# In[8]:


from langchain_core.messages import HumanMessage

document_chain.invoke(
    {
        "context": docs,
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?")
        ],
    }
)


# Looks good! For comparison, we can try it with no context docs and compare the result:

# In[9]:


document_chain.invoke(
    {
        "context": [],
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?")
        ],
    }
)


# We can see that the LLM does not return any results.
# 
# ## Retrieval chains
# 
# Let's combine this document chain with the retriever. Here's one way this can look:

# In[10]:


from typing import Dict

from langchain_core.runnables import RunnablePassthrough


def parse_retriever_input(params: Dict):
    return params["messages"][-1].content


retrieval_chain = RunnablePassthrough.assign(
    context=parse_retriever_input | retriever,
).assign(
    answer=document_chain,
)


# Given a list of input messages, we extract the content of the last message in the list and pass that to the retriever to fetch some documents. Then, we pass those documents as context to our document chain to generate a final response.
# 
# Invoking this chain combines both steps outlined above:

# In[11]:


retrieval_chain.invoke(
    {
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?")
        ],
    }
)


# Looks good!
# 
# ## Query transformation
# 
# Our retrieval chain is capable of answering questions about LangSmith, but there's a problem - chatbots interact with users conversationally, and therefore have to deal with followup questions.
# 
# The chain in its current form will struggle with this. Consider a followup question to our original question like `Tell me more!`. If we invoke our retriever with that query directly, we get documents irrelevant to LLM application testing:

# In[12]:


retriever.invoke("Tell me more!")


# This is because the retriever has no innate concept of state, and will only pull documents most similar to the query given. To solve this, we can transform the query into a standalone query without any external references an LLM.
# 
# Here's an example:

# In[13]:


from langchain_core.messages import AIMessage, HumanMessage

query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
        ),
    ]
)

query_transformation_chain = query_transform_prompt | chat

query_transformation_chain.invoke(
    {
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?"),
            AIMessage(
                content="Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examples and add them to datasets to expand the surface area of your evaluation sets or to fine-tune a model for improved quality or reduced costs. Additionally, LangSmith can be used to monitor your application, log all traces, visualize latency and token usage statistics, and troubleshoot specific issues as they arise."
            ),
            HumanMessage(content="Tell me more!"),
        ],
    }
)


# Awesome! That transformed query would pull up context documents related to LLM application testing.
# 
# Let's add this to our retrieval chain. We can wrap our retriever as follows:

# In[14]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

query_transforming_retriever_chain = RunnableBranch(
    (
        lambda x: len(x.get("messages", [])) == 1,
        # If only one message, then we just pass that message's content to retriever
        (lambda x: x["messages"][-1].content) | retriever,
    ),
    # If messages, then we pass inputs to LLM chain to transform the query, then pass to retriever
    query_transform_prompt | chat | StrOutputParser() | retriever,
).with_config(run_name="chat_retriever_chain")


# Then, we can use this query transformation chain to make our retrieval chain better able to handle such followup questions:

# In[15]:


SYSTEM_TEMPLATE = """
Answer the user's questions based on the below context. 
If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

<context>
{context}
</context>
"""

question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_TEMPLATE,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

document_chain = create_stuff_documents_chain(chat, question_answering_prompt)

conversational_retrieval_chain = RunnablePassthrough.assign(
    context=query_transforming_retriever_chain,
).assign(
    answer=document_chain,
)


# Awesome! Let's invoke this new chain with the same inputs as earlier:

# In[16]:


conversational_retrieval_chain.invoke(
    {
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?"),
        ]
    }
)


# In[17]:


conversational_retrieval_chain.invoke(
    {
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?"),
            AIMessage(
                content="Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examples and add them to datasets to expand the surface area of your evaluation sets or to fine-tune a model for improved quality or reduced costs. Additionally, LangSmith can be used to monitor your application, log all traces, visualize latency and token usage statistics, and troubleshoot specific issues as they arise."
            ),
            HumanMessage(content="Tell me more!"),
        ],
    }
)


# You can check out [this LangSmith trace](https://smith.langchain.com/public/bb329a3b-e92a-4063-ad78-43f720fbb5a2/r) to see the internal query transformation step for yourself.
# 
# ## Streaming
# 
# Because this chain is constructed with LCEL, you can use familiar methods like `.stream()` with it:

# In[18]:


stream = conversational_retrieval_chain.stream(
    {
        "messages": [
            HumanMessage(content="Can LangSmith help test my LLM applications?"),
            AIMessage(
                content="Yes, LangSmith can help test and evaluate your LLM applications. It allows you to quickly edit examples and add them to datasets to expand the surface area of your evaluation sets or to fine-tune a model for improved quality or reduced costs. Additionally, LangSmith can be used to monitor your application, log all traces, visualize latency and token usage statistics, and troubleshoot specific issues as they arise."
            ),
            HumanMessage(content="Tell me more!"),
        ],
    }
)

for chunk in stream:
    print(chunk)


# ## Further reading
# 
# This guide only scratches the surface of retrieval techniques. For more on different ways of ingesting, preparing, and retrieving the most relevant data, check out the relevant how-to guides [here](/docs/how_to#document-loaders).
