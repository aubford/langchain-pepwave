#!/usr/bin/env python
# coding: utf-8

# # How to get a RAG application to add citations
# 
# This guide reviews methods to get a model to cite which parts of the source documents it referenced in generating its response.
# 
# We will cover five methods:
# 
# 1. Using tool-calling to cite document IDs;
# 2. Using tool-calling to cite documents IDs and provide text snippets;
# 3. Direct prompting;
# 4. Retrieval post-processing (i.e., compressing the retrieved context to make it more relevant);
# 5. Generation post-processing (i.e., issuing a second LLM call to annotate a generated answer with citations).
# 
# We generally suggest using the first item of the list that works for your use-case. That is, if your model supports tool-calling, try methods 1 or 2; otherwise, or if those fail, advance down the list.
# 
# Let's first create a simple [RAG](/docs/concepts/rag/) chain. To start we'll just retrieve from Wikipedia using the [WikipediaRetriever](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.wikipedia.WikipediaRetriever.html). We will use the same [LangGraph](/docs/concepts/architecture/#langgraph) implementation from the [RAG Tutorial](/docs/tutorials/rag).

# ## Setup
# 
# First we'll need to install some dependencies:

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community wikipedia')


# Let's first select a LLM:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm" />
# 

# In[2]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")


# We can now load a [retriever](/docs/concepts/retrievers/) and construct our [prompt](/docs/concepts/prompt_templates/):

# In[7]:


from langchain_community.retrievers import WikipediaRetriever
from langchain_core.prompts import ChatPromptTemplate

system_prompt = (
    "You're a helpful AI assistant. Given a user question "
    "and some Wikipedia article snippets, answer the user "
    "question. If none of the articles answer the question, "
    "just say you don't know."
    "\n\nHere are the Wikipedia articles: "
    "{context}"
)

retriever = WikipediaRetriever(top_k_results=6, doc_content_chars_max=2000)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{question}"),
    ]
)
prompt.pretty_print()


# Now that we've got a [model](/docs/concepts/chat_models/), [retriever](/docs/concepts/retrievers/) and [prompt](/docs/concepts/prompt_templates/), let's chain them all together. Following the how-to guide on [adding citations](/docs/how_to/qa_citations) to a RAG application, we'll make it so our chain returns both the answer and the retrieved Documents. This uses the same [LangGraph](/docs/concepts/architecture/#langgraph) implementation as in the [RAG Tutorial](/docs/tutorials/rag).

# In[4]:


from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = retriever.invoke(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# In[5]:


from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))


# In[10]:


result = graph.invoke({"question": "How fast are cheetahs?"})

sources = [doc.metadata["source"] for doc in result["context"]]
print(f"Sources: {sources}\n\n")
print(f'Answer: {result["answer"]}')


# Check out the [LangSmith trace](https://smith.langchain.com/public/ed043789-8599-44de-b88e-ba463ea454a3/r).

# ## Tool-calling
# 
# If your LLM of choice implements a [tool-calling](/docs/concepts/tool_calling) feature, you can use it to make the model specify which of the provided documents it's referencing when generating its answer. LangChain tool-calling models implement a `.with_structured_output` method which will force generation adhering to a desired schema (see details [here](/docs/how_to/structured_output/)).
# 
# ### Cite documents
# 
# To cite documents using an identifier, we format the identifiers into the prompt, then use `.with_structured_output` to coerce the LLM to reference these identifiers in its output.
# 
# First we define a schema for the output. The `.with_structured_output` supports multiple formats, including JSON schema and Pydantic. Here we will use Pydantic:

# In[11]:


from pydantic import BaseModel, Field


class CitedAnswer(BaseModel):
    """Answer the user question based only on the given sources, and cite the sources used."""

    answer: str = Field(
        ...,
        description="The answer to the user question, which is based only on the given sources.",
    )
    citations: List[int] = Field(
        ...,
        description="The integer IDs of the SPECIFIC sources which justify the answer.",
    )


# Let's see what the model output is like when we pass in our functions and a user input:

# In[12]:


structured_llm = llm.with_structured_output(CitedAnswer)

example_q = """What Brian's height?

Source: 1
Information: Suzy is 6'2"

Source: 2
Information: Jeremiah is blonde

Source: 3
Information: Brian is 3 inches shorter than Suzy"""
result = structured_llm.invoke(example_q)

result


# Or as a dict:

# In[13]:


result.dict()


# Now we structure the source identifiers into the prompt to replicate with our chain. We will make three changes:
# 
# 1. Update the prompt to include source identifiers;
# 2. Use the `structured_llm` (i.e., `llm.with_structured_output(CitedAnswer)`);
# 3. Return the Pydantic object in the output.

# In[26]:


def format_docs_with_id(docs: List[Document]) -> str:
    formatted = [
        f"Source ID: {i}\nArticle Title: {doc.metadata['title']}\nArticle Snippet: {doc.page_content}"
        for i, doc in enumerate(docs)
    ]
    return "\n\n" + "\n\n".join(formatted)


class State(TypedDict):
    question: str
    context: List[Document]
    # highlight-next-line
    answer: CitedAnswer


def generate(state: State):
    # highlight-next-line
    formatted_docs = format_docs_with_id(state["context"])
    messages = prompt.invoke({"question": state["question"], "context": formatted_docs})
    # highlight-start
    structured_llm = llm.with_structured_output(CitedAnswer)
    response = structured_llm.invoke(messages)
    # highlight-end
    return {"answer": response}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# In[27]:


result = graph.invoke({"question": "How fast are cheetahs?"})

result["answer"]


# We can inspect the document at index 0, which the model cited:

# In[21]:


print(result["context"][0])


# LangSmith trace: https://smith.langchain.com/public/6f34d136-451d-4625-90c8-2d8decebc21a/r

# ### Cite snippets
# 
# To return text spans (perhaps in addition to source identifiers), we can use the same approach. The only change will be to build a more complex output schema, here using Pydantic, that includes a "quote" alongside a source identifier.
# 
# *Aside: Note that if we break up our documents so that we have many documents with only a sentence or two instead of a few long documents, citing documents becomes roughly equivalent to citing snippets, and may be easier for the model because the model just needs to return an identifier for each snippet instead of the actual text. Probably worth trying both approaches and evaluating.*

# In[28]:


class Citation(BaseModel):
    source_id: int = Field(
        ...,
        description="The integer ID of a SPECIFIC source which justifies the answer.",
    )
    quote: str = Field(
        ...,
        description="The VERBATIM quote from the specified source that justifies the answer.",
    )


class QuotedAnswer(BaseModel):
    """Answer the user question based only on the given sources, and cite the sources used."""

    answer: str = Field(
        ...,
        description="The answer to the user question, which is based only on the given sources.",
    )
    citations: List[Citation] = Field(
        ..., description="Citations from the given sources that justify the answer."
    )


# In[32]:


class State(TypedDict):
    question: str
    context: List[Document]
    # highlight-next-line
    answer: QuotedAnswer


def generate(state: State):
    formatted_docs = format_docs_with_id(state["context"])
    messages = prompt.invoke({"question": state["question"], "context": formatted_docs})
    # highlight-next-line
    structured_llm = llm.with_structured_output(QuotedAnswer)
    response = structured_llm.invoke(messages)
    return {"answer": response}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# Here we see that the model has extracted a relevant snippet of text from source 0:

# In[33]:


result = graph.invoke({"question": "How fast are cheetahs?"})

result["answer"]


# LangSmith trace: https://smith.langchain.com/public/e16dc72f-4261-4f25-a9a7-906238737283/r

# ## Direct prompting
# 
# Some models don't support function-calling. We can achieve similar results with direct prompting. Let's try instructing a model to generate structured XML for its output:

# In[38]:


xml_system = """You're a helpful AI assistant. Given a user question and some Wikipedia article snippets, \
answer the user question and provide citations. If none of the articles answer the question, just say you don't know.

Remember, you must return both an answer and citations. A citation consists of a VERBATIM quote that \
justifies the answer and the ID of the quote article. Return a citation for every quote across all articles \
that justify the answer. Use the following format for your final output:

<cited_answer>
    <answer></answer>
    <citations>
        <citation><source_id></source_id><quote></quote></citation>
        <citation><source_id></source_id><quote></quote></citation>
        ...
    </citations>
</cited_answer>

Here are the Wikipedia articles:{context}"""
xml_prompt = ChatPromptTemplate.from_messages(
    [("system", xml_system), ("human", "{question}")]
)


# We now make similar small updates to our chain:
# 
# 1. We update the formatting function to wrap the retrieved context in XML tags;
# 2. We do not use `.with_structured_output` (e.g., because it does not exist for a model);
# 3. We use [XMLOutputParser](https://python.langchain.com/api_reference/core/output_parsers/langchain_core.output_parsers.xml.XMLOutputParser.html) to parse the answer into a dict.

# In[41]:


from langchain_core.output_parsers import XMLOutputParser


def format_docs_xml(docs: List[Document]) -> str:
    formatted = []
    for i, doc in enumerate(docs):
        doc_str = f"""\
    <source id=\"{i}\">
        <title>{doc.metadata['title']}</title>
        <article_snippet>{doc.page_content}</article_snippet>
    </source>"""
        formatted.append(doc_str)
    return "\n\n<sources>" + "\n".join(formatted) + "</sources>"


class State(TypedDict):
    question: str
    context: List[Document]
    # highlight-next-line
    answer: dict


def generate(state: State):
    # highlight-start
    formatted_docs = format_docs_xml(state["context"])
    messages = xml_prompt.invoke(
        {"question": state["question"], "context": formatted_docs}
    )
    response = llm.invoke(messages)
    parsed_response = XMLOutputParser().invoke(response)
    # highlight-end
    return {"answer": parsed_response}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# Note that citations are again structured into the answer:

# In[42]:


result = graph.invoke({"question": "How fast are cheetahs?"})

result["answer"]


# LangSmith trace: https://smith.langchain.com/public/0c45f847-c640-4b9a-a5fa-63559e413527/r

# ## Retrieval post-processing
# 
# Another approach is to post-process our retrieved documents to compress the content, so that the source content is already minimal enough that we don't need the model to cite specific sources or spans. For example, we could break up each document into a sentence or two, embed those and keep only the most relevant ones. LangChain has some built-in components for this. Here we'll use a [RecursiveCharacterTextSplitter](https://python.langchain.com/api_reference/text_splitters/text_splitter/langchain_text_splitters.RecursiveCharacterTextSplitter.html#langchain_text_splitters.RecursiveCharacterTextSplitter), which creates chunks of a specified size by splitting on separator substrings, and an [EmbeddingsFilter](https://python.langchain.com/api_reference/langchain/retrievers/langchain.retrievers.document_compressors.embeddings_filter.EmbeddingsFilter.html#langchain.retrievers.document_compressors.embeddings_filter.EmbeddingsFilter), which keeps only the texts with the most relevant embeddings.
# 
# This approach effectively updates our `retrieve` step to compress the documents. Let's first select an [embedding model](/docs/integrations/text_embedding/):
# 
# import EmbeddingTabs from "@theme/EmbeddingTabs";
# 
# <EmbeddingTabs/>

# In[43]:


# | output: false
# | echo: false

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()


# We can now rewrite the `retrieve` step:

# In[44]:


from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain_core.runnables import RunnableParallel
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=0,
    separators=["\n\n", "\n", ".", " "],
    keep_separator=False,
)
compressor = EmbeddingsFilter(embeddings=embeddings, k=10)


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def retrieve(state: State):
    retrieved_docs = retriever.invoke(state["question"])
    # highlight-start
    split_docs = splitter.split_documents(retrieved_docs)
    stateful_docs = compressor.compress_documents(split_docs, state["question"])
    # highlight-end
    return {"context": stateful_docs}


# Let's test this out:

# In[60]:


retrieval_result = retrieve({"question": "How fast are cheetahs?"})

for doc in retrieval_result["context"]:
    print(f"{doc.page_content}\n\n")


# Next, we assemble it into our chain as before:

# In[63]:


# This step is unchanged from our original RAG implementation
def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# In[64]:


result = graph.invoke({"question": "How fast are cheetahs?"})

print(result["answer"])


# Note that the document content is now compressed, although the document objects retain the original content in a "summary" key in their metadata. These summaries are not passed to the model; only the condensed content is.

# In[65]:


result["context"][0].page_content  # passed to model


# In[66]:


result["context"][0].metadata["summary"]  # original document  # original document


# LangSmith trace: https://smith.langchain.com/public/21b0dc15-d70a-4293-9402-9c70f9178e66/r

# ## Generation post-processing
# 
# Another approach is to post-process our model generation. In this example we'll first generate just an answer, and then we'll ask the model to annotate it's own answer with citations. The downside of this approach is of course that it is slower and more expensive, because two model calls need to be made.
# 
# Let's apply this to our initial chain. If desired, we can implement this via a third step in our application.

# In[67]:


class Citation(BaseModel):
    source_id: int = Field(
        ...,
        description="The integer ID of a SPECIFIC source which justifies the answer.",
    )
    quote: str = Field(
        ...,
        description="The VERBATIM quote from the specified source that justifies the answer.",
    )


class AnnotatedAnswer(BaseModel):
    """Annotate the answer to the user question with quote citations that justify the answer."""

    citations: List[Citation] = Field(
        ..., description="Citations from the given sources that justify the answer."
    )


structured_llm = llm.with_structured_output(AnnotatedAnswer)


# In[80]:


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    # highlight-next-line
    annotations: AnnotatedAnswer


def retrieve(state: State):
    retrieved_docs = retriever.invoke(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# highlight-start
def annotate(state: State):
    formatted_docs = format_docs_with_id(state["context"])
    messages = [
        ("system", system_prompt.format(context=formatted_docs)),
        ("human", state["question"]),
        ("ai", state["answer"]),
        ("human", "Annotate your answer with citations."),
    ]
    response = structured_llm.invoke(messages)
    # highlight-end
    # highlight-next-line
    return {"annotations": response}


# highlight-next-line
graph_builder = StateGraph(State).add_sequence([retrieve, generate, annotate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# In[81]:


display(Image(graph.get_graph().draw_mermaid_png()))


# In[82]:


result = graph.invoke({"question": "How fast are cheetahs?"})

print(result["answer"])


# In[83]:


result["annotations"]


# LangSmith trace: https://smith.langchain.com/public/b8257417-573b-47c4-a750-74e542035f19/r

# In[ ]:




