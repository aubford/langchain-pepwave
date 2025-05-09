#!/usr/bin/env python
# coding: utf-8

# # Docling

# [Docling](https://github.com/DS4SD/docling) parses PDF, DOCX, PPTX, HTML, and other formats into a rich unified representation including document layout, tables etc., making them ready for generative AI workflows like RAG.
# 
# This integration provides Docling's capabilities via the `DoclingLoader` document loader.

# ## Overview
# 
# <!-- 
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support|
# | :--- | :--- | :---: | :---: |  :---: |
# | langchain_docling.DoclingLoader | langchain-docling | ✅ | ❌ | ❌ | 
# 
# ### Loader features
# | Source | Document Lazy Loading | Native Async Support
# | :---: | :---: | :---: | 
# | DoclingLoader | ✅ | ❌ | 
#  -->
# 
# The presented `DoclingLoader` component enables you to:
# - use various document types in your LLM applications with ease and speed, and
# - leverage Docling's rich format for advanced, document-native grounding.
# 
# `DoclingLoader` supports two different export modes:
# - `ExportType.DOC_CHUNKS` (default): if you want to have each input document chunked and
#   to then capture each individual chunk as a separate LangChain Document downstream, or
# - `ExportType.MARKDOWN`: if you want to capture each input document as a separate
#   LangChain Document
# 
# The example allows exploring both modes via parameter `EXPORT_TYPE`; depending on the
# value set, the example pipeline is then set up accordingly.

# ## Setup

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain-docling')


# > For best conversion speed, use GPU acceleration whenever available; e.g. if running on Colab, use a GPU-enabled runtime.

# ## Initialization

# Basic initialization looks as follows:

# In[2]:


from langchain_docling import DoclingLoader

FILE_PATH = "https://arxiv.org/pdf/2408.09869"

loader = DoclingLoader(file_path=FILE_PATH)


# For advanced usage, `DoclingLoader` has the following parameters:
# - `file_path`: source as single str (URL or local file) or iterable thereof
# - `converter` (optional): any specific Docling converter instance to use
# - `convert_kwargs` (optional): any specific kwargs for conversion execution
# - `export_type` (optional): export mode to use: `ExportType.DOC_CHUNKS` (default) or
#     `ExportType.MARKDOWN`
# - `md_export_kwargs` (optional): any specific Markdown export kwargs (for Markdown mode)
# - `chunker` (optional): any specific Docling chunker instance to use (for doc-chunk
#     mode)
# - `meta_extractor` (optional): any specific metadata extractor to use
# 

# ## Load

# In[3]:


docs = loader.load()


# > Note: a message saying `"Token indices sequence length is longer than the specified
# maximum sequence length..."` can be ignored in this case — more details
# [here](https://github.com/DS4SD/docling-core/issues/119#issuecomment-2577418826).

# Inspecting some sample docs:

# In[4]:


for d in docs[:3]:
    print(f"- {d.page_content=}")


# ## Lazy Load
# 
# Documents can also be loaded in a lazy fashion:

# In[5]:


doc_iter = loader.lazy_load()
for doc in doc_iter:
    pass  # you can operate on `doc` here


# ## End-to-end Example
# 

# In[6]:


import os

# https://github.com/huggingface/transformers/issues/5486:
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# 
# > - The following example pipeline uses HuggingFace's Inference API; for increased LLM quota, token can be provided via env var `HF_TOKEN`.
# > - Dependencies for this pipeline can be installed as shown below (`--no-warn-conflicts` meant for Colab's pre-populated Python env; feel free to remove for stricter usage):

# In[7]:


get_ipython().run_line_magic('pip', 'install -q --progress-bar off --no-warn-conflicts langchain-core langchain-huggingface langchain_milvus langchain python-dotenv')


# Defining the pipeline parameters:

# In[8]:


from pathlib import Path
from tempfile import mkdtemp

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_docling.loader import ExportType


def _get_env_from_colab_or_os(key):
    try:
        from google.colab import userdata

        try:
            return userdata.get(key)
        except userdata.SecretNotFoundError:
            pass
    except ImportError:
        pass
    return os.getenv(key)


load_dotenv()

HF_TOKEN = _get_env_from_colab_or_os("HF_TOKEN")
FILE_PATH = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EXPORT_TYPE = ExportType.DOC_CHUNKS
QUESTION = "Which are the main AI models in Docling?"
PROMPT = PromptTemplate.from_template(
    "Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {input}\nAnswer:\n",
)
TOP_K = 3
MILVUS_URI = str(Path(mkdtemp()) / "docling.db")


# Now we can instantiate our loader and load documents:

# In[9]:


from docling.chunking import HybridChunker
from langchain_docling import DoclingLoader

loader = DoclingLoader(
    file_path=FILE_PATH,
    export_type=EXPORT_TYPE,
    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
)

docs = loader.load()


# Determining the splits:

# In[10]:


if EXPORT_TYPE == ExportType.DOC_CHUNKS:
    splits = docs
elif EXPORT_TYPE == ExportType.MARKDOWN:
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ],
    )
    splits = [split for doc in docs for split in splitter.split_text(doc.page_content)]
else:
    raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")


# Inspecting some sample splits:

# In[11]:


for d in splits[:3]:
    print(f"- {d.page_content=}")
print("...")


# ### Ingestion

# In[12]:


import json
from pathlib import Path
from tempfile import mkdtemp

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)

milvus_uri = str(Path(mkdtemp()) / "docling.db")  # or set as needed
vectorstore = Milvus.from_documents(
    documents=splits,
    embedding=embedding,
    collection_name="docling_demo",
    connection_args={"uri": milvus_uri},
    index_params={"index_type": "FLAT"},
    drop_old=True,
)


# ### RAG

# In[13]:


from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEndpoint

retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
llm = HuggingFaceEndpoint(
    repo_id=GEN_MODEL_ID,
    huggingfacehub_api_token=HF_TOKEN,
    task="text-generation",
)


# In[14]:


def clip_text(text, threshold=100):
    return f"{text[:threshold]}..." if len(text) > threshold else text


# In[15]:


question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
resp_dict = rag_chain.invoke({"input": QUESTION})

clipped_answer = clip_text(resp_dict["answer"], threshold=350)
print(f"Question:\n{resp_dict['input']}\n\nAnswer:\n{clipped_answer}")
for i, doc in enumerate(resp_dict["context"]):
    print()
    print(f"Source {i+1}:")
    print(f"  text: {json.dumps(clip_text(doc.page_content, threshold=350))}")
    for key in doc.metadata:
        if key != "pk":
            val = doc.metadata.get(key)
            clipped_val = clip_text(val) if isinstance(val, str) else val
            print(f"  {key}: {clipped_val}")


# Notice that the sources contain rich grounding information, including the passage
# headings (i.e. section), page, and precise bounding box.

# ## API reference
# 
# - [LangChain Docling integration GitHub](https://github.com/docling-project/docling-langchain)
# - [Docling GitHub](https://github.com/docling-project/docling)
# - [Docling docs](https://docling-project.github.io/docling//)

# 
