#!/usr/bin/env python
# coding: utf-8

# # Identity-enabled RAG using PebbloRetrievalQA
# 
# > PebbloRetrievalQA is a Retrieval chain with Identity & Semantic Enforcement for question-answering
# against a vector database.
# 
# This notebook covers how to retrieve documents using Identity & Semantic Enforcement (Deny Topics/Entities).
# For more details on Pebblo and its SafeRetriever feature visit [Pebblo documentation](https://daxa-ai.github.io/pebblo/retrieval_chain/)
# 
# ### Steps:
# 
# 1. **Loading Documents:**
# We will load documents with authorization and semantic metadata into an in-memory Qdrant vectorstore. This vectorstore will be used as a retriever in PebbloRetrievalQA. 
# 
# > **Note:** It is recommended to use [PebbloSafeLoader](https://daxa-ai.github.io/pebblo/rag) as the counterpart for loading documents with authentication and semantic metadata on the ingestion side. `PebbloSafeLoader` guarantees the secure and efficient loading of documents while maintaining the integrity of the metadata.
# 
# 
# 
# 2. **Testing Enforcement Mechanisms**:
#    We will test Identity and Semantic Enforcement separately. For each use case, we will define a specific "ask" function with the required contexts (*auth_context* and *semantic_context*) and then pose our questions.
# 

# ## Setup
# 
# ### Dependencies
# 
# We'll use an OpenAI LLM, OpenAI embeddings and a Qdrant vector store in this walkthrough.
# 

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain langchain_core langchain-community langchain-openai qdrant_client')


# ### Identity-aware Data Ingestion
# 
# Here we are using Qdrant as a vector database; however, you can use any of the supported vector databases.
# 
# **PebbloRetrievalQA chain supports the following vector databases:**
# - Qdrant
# - Pinecone
# - Postgres(utilizing the pgvector extension)
# 
# 
# **Load vector database with authorization and semantic information in metadata:**
# 
# In this step, we capture the authorization and semantic information of the source document into the `authorized_identities`, `pebblo_semantic_topics`, and `pebblo_semantic_entities` fields within the metadata of the VectorDB entry for each chunk. 
# 
# 
# *NOTE: To use the PebbloRetrievalQA chain, you must always place authorization and semantic metadata in the specified fields. These fields must contain a list of strings.*

# In[2]:


from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.llms import OpenAI

llm = OpenAI()
embeddings = OpenAIEmbeddings()
collection_name = "pebblo-identity-and-semantic-rag"

page_content = """
**ACME Corp Financial Report**

**Overview:**
ACME Corp, a leading player in the merger and acquisition industry, presents its financial report for the fiscal year ending December 31, 2020. 
Despite a challenging economic landscape, ACME Corp demonstrated robust performance and strategic growth.

**Financial Highlights:**
Revenue soared to $50 million, marking a 15% increase from the previous year, driven by successful deal closures and expansion into new markets. 
Net profit reached $12 million, showcasing a healthy margin of 24%.

**Key Metrics:**
Total assets surged to $80 million, reflecting a 20% growth, highlighting ACME Corp's strong financial position and asset base. 
Additionally, the company maintained a conservative debt-to-equity ratio of 0.5, ensuring sustainable financial stability.

**Future Outlook:**
ACME Corp remains optimistic about the future, with plans to capitalize on emerging opportunities in the global M&A landscape. 
The company is committed to delivering value to shareholders while maintaining ethical business practices.

**Bank Account Details:**
For inquiries or transactions, please refer to ACME Corp's US bank account:
Account Number: 123456789012
Bank Name: Fictitious Bank of America
"""

documents = [
    Document(
        **{
            "page_content": page_content,
            "metadata": {
                "pebblo_semantic_topics": ["financial-report"],
                "pebblo_semantic_entities": ["us-bank-account-number"],
                "authorized_identities": ["finance-team", "exec-leadership"],
                "page": 0,
                "source": "https://drive.google.com/file/d/xxxxxxxxxxxxx/view",
                "title": "ACME Corp Financial Report.pdf",
            },
        }
    )
]

vectordb = Qdrant.from_documents(
    documents,
    embeddings,
    location=":memory:",
    collection_name=collection_name,
)

print("Vectordb loaded.")


# ## Retrieval with Identity Enforcement
# 
# PebbloRetrievalQA chain uses a SafeRetrieval to enforce that the snippets used for in-context are retrieved only from the documents authorized for the user. 
# To achieve this, the Gen-AI application needs to provide an authorization context for this retrieval chain. 
# This *auth_context* should be filled with the identity and authorization groups of the user accessing the Gen-AI app.
# 
# 
# Here is the sample code for the `PebbloRetrievalQA` with `user_auth`(List of user authorizations, which may include their User ID and 
#     the groups they are part of) from the user accessing the RAG application, passed in `auth_context`.

# In[6]:


from langchain_community.chains import PebbloRetrievalQA
from langchain_community.chains.pebblo_retrieval.models import AuthContext, ChainInput

# Initialize PebbloRetrievalQA chain
qa_chain = PebbloRetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(),
    app_name="pebblo-identity-rag",
    description="Identity Enforcement app using PebbloRetrievalQA",
    owner="ACME Corp",
)


def ask(question: str, auth_context: dict):
    """
    Ask a question to the PebbloRetrievalQA chain
    """
    auth_context_obj = AuthContext(**auth_context) if auth_context else None
    chain_input_obj = ChainInput(query=question, auth_context=auth_context_obj)
    return qa_chain.invoke(chain_input_obj.dict())


# ### 1. Questions by Authorized User
# 
# We ingested data for authorized identities `["finance-team", "exec-leadership"]`, so a user with the authorized identity/group `finance-team` should receive the correct answer.

# In[17]:


auth = {
    "user_id": "finance-user@acme.org",
    "user_auth": [
        "finance-team",
    ],
}

question = "Share the financial performance of ACME Corp for the year 2020"
resp = ask(question, auth)
print(f"Question: {question}\n\nAnswer: {resp['result']}")


# ### 2. Questions by Unauthorized User
# 
# Since the user's authorized identity/group `eng-support` is not included in the authorized identities `["finance-team", "exec-leadership"]`, we should not receive an answer.

# In[18]:


auth = {
    "user_id": "eng-user@acme.org",
    "user_auth": [
        "eng-support",
    ],
}

question = "Share the financial performance of ACME Corp for the year 2020"
resp = ask(question, auth)
print(f"Question: {question}\n\nAnswer: {resp['result']}")


# ### 3. Using PromptTemplate to provide additional instructions
# You can use PromptTemplate to provide additional instructions to the LLM for generating a custom response.

# In[19]:


from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    """
Answer the question using the provided context. 
If no context is provided, just say "I'm sorry, but that information is unavailable, or Access to it is restricted.".

Question: {question}
"""
)

question = "Share the financial performance of ACME Corp for the year 2020"
prompt = prompt_template.format(question=question)


# #### 3.1 Questions by Authorized User

# In[21]:


auth = {
    "user_id": "finance-user@acme.org",
    "user_auth": [
        "finance-team",
    ],
}
resp = ask(prompt, auth)
print(f"Question: {question}\n\nAnswer: {resp['result']}")


# #### 3.2 Questions by Unauthorized Users

# In[22]:


auth = {
    "user_id": "eng-user@acme.org",
    "user_auth": [
        "eng-support",
    ],
}
resp = ask(prompt, auth)
print(f"Question: {question}\n\nAnswer: {resp['result']}")


# ## Retrieval with Semantic Enforcement

# The PebbloRetrievalQA chain uses SafeRetrieval to ensure that the snippets used in context are retrieved only from documents that comply with the
# provided semantic context.
# To achieve this, the Gen-AI application must provide a semantic context for this retrieval chain.
# This `semantic_context` should include the topics and entities that should be denied for the user accessing the Gen-AI app.
# 
# Below is a sample code for PebbloRetrievalQA with `topics_to_deny` and `entities_to_deny`. These are passed in `semantic_context` to the chain input.

# In[28]:


from typing import List, Optional

from langchain_community.chains import PebbloRetrievalQA
from langchain_community.chains.pebblo_retrieval.models import (
    ChainInput,
    SemanticContext,
)

# Initialize PebbloRetrievalQA chain
qa_chain = PebbloRetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(),
    app_name="pebblo-semantic-rag",
    description="Semantic Enforcement app using PebbloRetrievalQA",
    owner="ACME Corp",
)


def ask(
    question: str,
    topics_to_deny: Optional[List[str]] = None,
    entities_to_deny: Optional[List[str]] = None,
):
    """
    Ask a question to the PebbloRetrievalQA chain
    """
    semantic_context = dict()
    if topics_to_deny:
        semantic_context["pebblo_semantic_topics"] = {"deny": topics_to_deny}
    if entities_to_deny:
        semantic_context["pebblo_semantic_entities"] = {"deny": entities_to_deny}

    semantic_context_obj = (
        SemanticContext(**semantic_context) if semantic_context else None
    )
    chain_input_obj = ChainInput(query=question, semantic_context=semantic_context_obj)
    return qa_chain.invoke(chain_input_obj.dict())


# ### 1. Without semantic enforcement
# 
# Since no semantic enforcement is applied, the system should return the answer without excluding any context due to the semantic labels associated with the context.
# 

# In[29]:


topic_to_deny = []
entities_to_deny = []
question = "Share the financial performance of ACME Corp for the year 2020"
resp = ask(question, topics_to_deny=topic_to_deny, entities_to_deny=entities_to_deny)
print(
    f"Topics to deny: {topic_to_deny}\nEntities to deny: {entities_to_deny}\n"
    f"Question: {question}\nAnswer: {resp['result']}"
)


# ### 2. Deny financial-report topic
# 
# Data has been ingested with the topics: `["financial-report"]`.
# Therefore, an app that denies the `financial-report` topic should not receive an answer.

# In[30]:


topic_to_deny = ["financial-report"]
entities_to_deny = []
question = "Share the financial performance of ACME Corp for the year 2020"
resp = ask(question, topics_to_deny=topic_to_deny, entities_to_deny=entities_to_deny)
print(
    f"Topics to deny: {topic_to_deny}\nEntities to deny: {entities_to_deny}\n"
    f"Question: {question}\nAnswer: {resp['result']}"
)


# ### 3. Deny us-bank-account-number entity
# Since the entity `us-bank-account-number` is denied, the system should not return the answer.

# In[31]:


topic_to_deny = []
entities_to_deny = ["us-bank-account-number"]
question = "Share the financial performance of ACME Corp for the year 2020"
resp = ask(question, topics_to_deny=topic_to_deny, entities_to_deny=entities_to_deny)
print(
    f"Topics to deny: {topic_to_deny}\nEntities to deny: {entities_to_deny}\n"
    f"Question: {question}\nAnswer: {resp['result']}"
)

