#!/usr/bin/env python
# coding: utf-8

# # Contextual AI
# 
# Contextual AI provides state-of-the-art RAG components designed specifically for accurate and reliable enterprise AI applications. Our LangChain integration exposes standalone API endpoints for our specialized models:
# 
# - Grounded Language Model (GLM): The world's most grounded language model, engineered to minimize hallucinations by prioritizing faithfulness to retrieved knowledge. GLM delivers exceptional factual accuracy with inline attributions, making it ideal for enterprise RAG and agentic applications where reliability is critical.
# 
# - Instruction-Following Reranker: The first reranker that follows custom instructions to intelligently prioritize documents based on specific criteria like recency, source, or document type. Outperforming competitors on industry benchmarks, our reranker resolves conflicting information challenges in enterprise knowledge bases.
# 
# Founded by the inventors of RAG technology, Contextual AI's specialized components help innovative teams accelerate the development of production-ready RAG agents that deliver responses with exceptional accuracy.
# 
# ## Grounded Language Model (GLM)
# 
# The Grounded Language Model (GLM) is engineered specifically to minimize hallucinations in enterprise RAG and agentic applications. The GLM delivers:
# 
# - Strong performance with 88% factual accuracy on the FACTS benchmark ([See benchmark results](https://venturebeat.com/ai/contextual-ais-new-ai-model-crushes-gpt-4o-in-accuracy-heres-why-it-matters/))
# - Responses strictly grounded in provided knowledge sources with inline attributions ([Read product details](https://contextual.ai/blog/introducing-grounded-language-model/))
# - Precise source citations integrated directly within generated responses
# - Prioritization of retrieved context over parametric knowledge ([View technical overview](https://contextual.ai/blog/platform-benchmarks-2025/))
# - Clear acknowledgment of uncertainty when information is unavailable
# 
# GLM serves as a drop-in replacement for general-purpose LLMs in RAG pipelines, dramatically improving reliability for mission-critical enterprise applications.
# 
# ## Instruction-Following Reranker
# 
# The world's first Instruction-Following Reranker revolutionizes document ranking with unprecedented control and accuracy. Key capabilities include:
# 
# - Natural language instructions to prioritize documents based on recency, source, metadata, and more ([See how it works](https://contextual.ai/blog/introducing-instruction-following-reranker/))
# - Superior performance on the BEIR benchmark with a score of 61.2, outperforming competitors by significant margins ([View benchmark data](https://contextual.ai/blog/platform-benchmarks-2025/))
# - Intelligent resolution of conflicting information from multiple knowledge sources
# - Seamless integration as a drop-in replacement for existing rerankers
# - Dynamic control over document ranking through natural language commands
# 
# The reranker excels at handling enterprise knowledge bases with potentially contradictory information, allowing you to specify exactly which sources should take precedence in various scenarios.
# 
# ## Using Contextual AI with LangChain
# 
# See details [here](/docs/integrations/chat/contextual).
# 
# This integration allows you to easily incorporate Contextual AI's GLM and Instruction-Following Reranker into your LangChain workflows. The GLM ensures your applications deliver strictly grounded responses, while the reranker significantly improves retrieval quality by intelligently prioritizing the most relevant documents.
# 
# Whether you're building applications for regulated industries or security-conscious environments, Contextual AI provides the accuracy, control, and reliability your enterprise use cases demand.
# 
# Get started with a free trial today and experience the most grounded language model and instruction-following reranker for enterprise AI applications.

# ### Grounded Language Model

# In[ ]:


# Integrating the Grounded Language Model
import getpass
import os

from langchain_contextual import ChatContextual

# Set credentials
if not os.getenv("CONTEXTUAL_AI_API_KEY"):
    os.environ["CONTEXTUAL_AI_API_KEY"] = getpass.getpass(
        "Enter your Contextual API key: "
    )

# initialize Contextual llm
llm = ChatContextual(
    model="v1",
    api_key="",
)
# include a system prompt (optional)
system_prompt = "You are a helpful assistant that uses all of the provided knowledge to answer the user's query to the best of your ability."

# provide your own knowledge from your knowledge-base here in an array of string
knowledge = [
    "There are 2 types of dogs in the world: good dogs and best dogs.",
    "There are 2 types of cats in the world: good cats and best cats.",
]

# create your message
messages = [
    ("human", "What type of cats are there in the world and what are the types?"),
]

# invoke the GLM by providing the knowledge strings, optional system prompt
# if you want to turn off the GLM's commentary, pass True to the `avoid_commentary` argument
ai_msg = llm.invoke(
    messages, knowledge=knowledge, system_prompt=system_prompt, avoid_commentary=True
)

print(ai_msg.content)


# ### Instruction-Following Reranker

# In[ ]:


import getpass
import os

from langchain_contextual import ContextualRerank

if not os.getenv("CONTEXTUAL_AI_API_KEY"):
    os.environ["CONTEXTUAL_AI_API_KEY"] = getpass.getpass(
        "Enter your Contextual API key: "
    )


api_key = ""
model = "ctxl-rerank-en-v1-instruct"

compressor = ContextualRerank(
    model=model,
    api_key=api_key,
)

from langchain_core.documents import Document

query = "What is the current enterprise pricing for the RTX 5090 GPU for bulk orders?"
instruction = "Prioritize internal sales documents over market analysis reports. More recent documents should be weighted higher. Enterprise portal content supersedes distributor communications."

document_contents = [
    "Following detailed cost analysis and market research, we have implemented the following changes: AI training clusters will see a 15% uplift in raw compute performance, enterprise support packages are being restructured, and bulk procurement programs (100+ units) for the RTX 5090 Enterprise series will operate on a $2,899 baseline.",
    "Enterprise pricing for the RTX 5090 GPU bulk orders (100+ units) is currently set at $3,100-$3,300 per unit. This pricing for RTX 5090 enterprise bulk orders has been confirmed across all major distribution channels.",
    "RTX 5090 Enterprise GPU requires 450W TDP and 20% cooling overhead.",
]

metadata = [
    {
        "Date": "January 15, 2025",
        "Source": "NVIDIA Enterprise Sales Portal",
        "Classification": "Internal Use Only",
    },
    {"Date": "11/30/2023", "Source": "TechAnalytics Research Group"},
    {
        "Date": "January 25, 2025",
        "Source": "NVIDIA Enterprise Sales Portal",
        "Classification": "Internal Use Only",
    },
]

documents = [
    Document(page_content=content, metadata=metadata[i])
    for i, content in enumerate(document_contents)
]
reranked_documents = compressor.compress_documents(
    query=query,
    instruction=instruction,
    documents=documents,
)

