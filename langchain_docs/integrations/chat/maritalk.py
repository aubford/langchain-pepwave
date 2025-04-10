#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/langchain-ai/langchain/blob/master/docs/docs/integrations/chat/maritalk.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
# 
# # Maritalk
# 
# ## Introduction
# 
# MariTalk is an assistant developed by the Brazilian company [Maritaca AI](https://www.maritaca.ai).
# MariTalk is based on language models that have been specially trained to understand Portuguese well.
# 
# This notebook demonstrates how to use MariTalk with LangChain through two examples:
# 
# 1. A simple example of how to use MariTalk to perform a task.
# 2. LLM + RAG: The second example shows how to answer a question whose answer is found in a long document that does not fit within the token limit of MariTalk. For this, we will use a simple searcher (BM25) to first search the document for the most relevant sections and then feed them to MariTalk for answering.

# ## Installation
# First, install the LangChain library (and all its dependencies) using the following command:

# In[ ]:


get_ipython().system('pip install langchain langchain-core langchain-community httpx')


# ## API Key
# You will need an API key that can be obtained from chat.maritaca.ai ("Chaves da API" section).

# 
# ### Example 1 - Pet Name Suggestions
# 
# Let's define our language model, ChatMaritalk, and configure it with your API key.

# In[ ]:


from langchain_community.chat_models import ChatMaritalk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate

llm = ChatMaritalk(
    model="sabia-2-medium",  # Available models: sabia-2-small and sabia-2-medium
    api_key="",  # Insert your API key here
    temperature=0.7,
    max_tokens=100,
)

output_parser = StrOutputParser()

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an assistant specialized in suggesting pet names. Given the animal, you must suggest 4 names.",
        ),
        ("human", "I have a {animal}"),
    ]
)

chain = chat_prompt | llm | output_parser

response = chain.invoke({"animal": "dog"})
print(response)  # should answer something like "1. Max\n2. Bella\n3. Charlie\n4. Rocky"


# ### Stream Generation
# 
# For tasks involving the generation of long text, such as creating an extensive article or translating a large document, it can be advantageous to receive the response in parts, as the text is generated, instead of waiting for the complete text. This makes the application more responsive and efficient, especially when the generated text is extensive. We offer two approaches to meet this need: one synchronous and another asynchronous.
# 
# #### Synchronous:

# In[ ]:


from langchain_core.messages import HumanMessage

messages = [HumanMessage(content="Suggest 3 names for my dog")]

for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)


# #### Asynchronous:

# In[ ]:


from langchain_core.messages import HumanMessage


async def async_invoke_chain(animal: str):
    messages = [HumanMessage(content=f"Suggest 3 names for my {animal}")]
    async for chunk in llm._astream(messages):
        print(chunk.message.content, end="", flush=True)


await async_invoke_chain("dog")


# ### Example 2 - RAG + LLM: UNICAMP 2024 Entrance Exam Question Answering System
# For this example, we need to install some extra libraries:

# In[ ]:


get_ipython().system('pip install unstructured rank_bm25 pdf2image pdfminer-six pikepdf pypdf unstructured_inference fastapi kaleido uvicorn "pillow<10.1.0" pillow_heif -q')


# #### Loading the database
# 
# The first step is to create a database with the information from the notice. For this, we will download the notice from the COMVEST website and segment the extracted text into 500-character windows.

# In[ ]:


from langchain_community.document_loaders import OnlinePDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Loading the COMVEST 2024 notice
loader = OnlinePDFLoader(
    "https://www.comvest.unicamp.br/wp-content/uploads/2023/10/31-2023-Dispoe-sobre-o-Vestibular-Unicamp-2024_com-retificacao.pdf"
)
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=100, separators=["\n", " ", ""]
)
texts = text_splitter.split_documents(data)


# #### Creating a Searcher
# Now that we have our database, we need a searcher. For this example, we will use a simple BM25 as a search system, but this could be replaced by any other searcher (such as search via embeddings).

# In[ ]:


from langchain_community.retrievers import BM25Retriever

retriever = BM25Retriever.from_documents(texts)


# #### Combining Search System + LLM
# Now that we have our searcher, we just need to implement a prompt specifying the task and invoke the chain.

# In[ ]:


from langchain.chains.question_answering import load_qa_chain

prompt = """Baseado nos seguintes documentos, responda a pergunta abaixo.

{context}

Pergunta: {query}
"""

qa_prompt = ChatPromptTemplate.from_messages([("human", prompt)])

chain = load_qa_chain(llm, chain_type="stuff", verbose=True, prompt=qa_prompt)

query = "Qual o tempo máximo para realização da prova?"

docs = retriever.invoke(query)

chain.invoke(
    {"input_documents": docs, "query": query}
)  # Should output something like: "O tempo máximo para realização da prova é de 5 horas."

