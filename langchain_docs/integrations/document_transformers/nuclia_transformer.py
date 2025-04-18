#!/usr/bin/env python
# coding: utf-8

# # Nuclia
# 
# >[Nuclia](https://nuclia.com) automatically indexes your unstructured data from any internal and external source, providing optimized search results and generative answers. It can handle video and audio transcription, image content extraction, and document parsing.
# 
# `Nuclia Understanding API` document transformer splits text into paragraphs and sentences, identifies entities, provides a summary of the text and generates embeddings for all the sentences.
# 
# To use the Nuclia Understanding API, you need to have a Nuclia account. You can create one for free at [https://nuclia.cloud](https://nuclia.cloud), and then [create a NUA key](https://docs.nuclia.dev/docs/docs/using/understanding/intro).
# 
# from langchain_community.document_transformers.nuclia_text_transform import NucliaTextTransformer

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  protobuf')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  nucliadb-protos')


# In[ ]:


import os

os.environ["NUCLIA_ZONE"] = "<YOUR_ZONE>"  # e.g. europe-1
os.environ["NUCLIA_NUA_KEY"] = "<YOUR_API_KEY>"


# To use the Nuclia document transformer, you need to instantiate a `NucliaUnderstandingAPI` tool with `enable_ml` set to `True`:

# In[ ]:


from langchain_community.tools.nuclia import NucliaUnderstandingAPI

nua = NucliaUnderstandingAPI(enable_ml=True)


# The Nuclia document transformer must be called in async mode, so you need to use the `atransform_documents` method:

# In[ ]:


import asyncio

from langchain_community.document_transformers.nuclia_text_transform import (
    NucliaTextTransformer,
)
from langchain_core.documents import Document


async def process():
    documents = [
        Document(page_content="<TEXT 1>", metadata={}),
        Document(page_content="<TEXT 2>", metadata={}),
        Document(page_content="<TEXT 3>", metadata={}),
    ]
    nuclia_transformer = NucliaTextTransformer(nua)
    transformed_documents = await nuclia_transformer.atransform_documents(documents)
    print(transformed_documents)


asyncio.run(process())

