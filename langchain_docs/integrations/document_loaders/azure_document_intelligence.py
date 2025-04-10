#!/usr/bin/env python
# coding: utf-8

# # Azure AI Document Intelligence

# >[Azure AI Document Intelligence](https://aka.ms/doc-intelligence) (formerly known as `Azure Form Recognizer`) is machine-learning 
# >based service that extracts texts (including handwriting), tables, document structures (e.g., titles, section headings, etc.) and key-value-pairs from
# >digital or scanned PDFs, images, Office and HTML files.
# >
# >Document Intelligence supports `PDF`, `JPEG/JPG`, `PNG`, `BMP`, `TIFF`, `HEIF`, `DOCX`, `XLSX`, `PPTX` and `HTML`.
# 
# This current implementation of a loader using `Document Intelligence` can incorporate content page-wise and turn it into LangChain documents. The default output format is markdown, which can be easily chained with `MarkdownHeaderTextSplitter` for semantic document chunking. You can also use `mode="single"` or `mode="page"` to return pure texts in a single page or document split by page.
# 

# ## Prerequisite
# 
# An Azure AI Document Intelligence resource in one of the 3 preview regions: **East US**, **West US2**, **West Europe** - follow [this document](https://learn.microsoft.com/azure/ai-services/document-intelligence/create-document-intelligence-resource?view=doc-intel-4.0.0) to create one if you don't have. You will be passing `<endpoint>` and `<key>` as parameters to the loader.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain langchain-community azure-ai-documentintelligence')


# ## Example 1

# The first example uses a local file which will be sent to Azure AI Document Intelligence.

# With the initialized document analysis client, we can proceed to create an instance of the DocumentIntelligenceLoader:

# In[ ]:


from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

file_path = "<filepath>"
endpoint = "<endpoint>"
key = "<key>"
loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=endpoint, api_key=key, file_path=file_path, api_model="prebuilt-layout"
)

documents = loader.load()


# The default output contains one LangChain document with markdown format content: 

# In[ ]:


documents


# ## Example 2
# The input file can also be a public URL path. E.g., https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/rest-api/layout.png.

# In[ ]:


url_path = "<url>"
loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=endpoint, api_key=key, url_path=url_path, api_model="prebuilt-layout"
)

documents = loader.load()


# In[ ]:


documents


# ## Example 3
# You can also specify `mode="page"` to load document by pages.

# In[ ]:


from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

file_path = "<filepath>"
endpoint = "<endpoint>"
key = "<key>"
loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=endpoint,
    api_key=key,
    file_path=file_path,
    api_model="prebuilt-layout",
    mode="page",
)

documents = loader.load()


# The output will be each page stored as a separate document in the list:

# In[ ]:


for document in documents:
    print(f"Page Content: {document.page_content}")
    print(f"Metadata: {document.metadata}")


# ## Example 4
# You can also specify `analysis_feature=["ocrHighResolution"]` to enable add-on capabilities. For more information, see: https://aka.ms/azsdk/python/documentintelligence/analysisfeature.

# In[ ]:


from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

file_path = "<filepath>"
endpoint = "<endpoint>"
key = "<key>"
analysis_features = ["ocrHighResolution"]
loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=endpoint,
    api_key=key,
    file_path=file_path,
    api_model="prebuilt-layout",
    analysis_features=analysis_features,
)

documents = loader.load()


# The output contains the LangChain document recognized with high resolution add-on capability:

# In[ ]:


documents

