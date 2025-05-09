#!/usr/bin/env python
# coding: utf-8

# # Amazon Textract 
# 
# >[Amazon Textract](https://docs.aws.amazon.com/managedservices/latest/userguide/textract.html) is a machine learning (ML) service that automatically extracts text, handwriting, and data from scanned documents.
# >
# >It goes beyond simple optical character recognition (OCR) to identify, understand, and extract data from forms and tables. Today, many companies manually extract data from scanned documents such as PDFs, images, tables, and forms, or through simple OCR software that requires manual configuration (which often must be updated when the form changes). To overcome these manual and expensive processes, `Textract` uses ML to read and process any type of document, accurately extracting text, handwriting, tables, and other data with no manual effort. 
# 
# This sample demonstrates the use of `Amazon Textract` in combination with LangChain as a DocumentLoader.
# 
# `Textract` supports`PDF`, `TIFF`, `PNG` and `JPEG` format.
# 
# `Textract` supports these [document sizes, languages and characters](https://docs.aws.amazon.com/textract/latest/dg/limits-document.html).

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  boto3 langchain-openai tiktoken python-dotenv')


# In[2]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  "amazon-textract-caller>=0.2.0"')


# ## Sample 1
# 
# The first example uses a local file, which internally will be send to Amazon Textract sync API [DetectDocumentText](https://docs.aws.amazon.com/textract/latest/dg/API_DetectDocumentText.html). 
# 
# Local files or URL endpoints like HTTP:// are limited to one page documents for Textract.
# Multi-page documents have to reside on S3. This sample file is a jpeg.

# In[ ]:


from langchain_community.document_loaders import AmazonTextractPDFLoader

loader = AmazonTextractPDFLoader("example_data/alejandro_rosalez_sample-small.jpeg")
documents = loader.load()


# Output from the file

# In[10]:


documents


# ## Sample 2
# The next sample loads a file from an HTTPS endpoint. 
# It has to be single page, as Amazon Textract requires all multi-page documents to be stored on S3.

# In[7]:


from langchain_community.document_loaders import AmazonTextractPDFLoader

loader = AmazonTextractPDFLoader(
    "https://amazon-textract-public-content.s3.us-east-2.amazonaws.com/langchain/alejandro_rosalez_sample_1.jpg"
)
documents = loader.load()


# In[11]:


documents


# ## Sample 3
# 
# Processing a multi-page document requires the document to be on S3. The sample document resides in a bucket in us-east-2 and Textract needs to be called in that same region to be successful, so we set the region_name on the client and pass that in to the loader to ensure Textract is called from us-east-2. You could also to have your notebook running in us-east-2, setting the AWS_DEFAULT_REGION set to us-east-2 or when running in a different environment, pass in a boto3 Textract client with that region name like in the cell below.

# In[12]:


import boto3

textract_client = boto3.client("textract", region_name="us-east-2")

file_path = "s3://amazon-textract-public-content/langchain/layout-parser-paper.pdf"
loader = AmazonTextractPDFLoader(file_path, client=textract_client)
documents = loader.load()


# Now getting the number of pages to validate the response (printing out the full response would be quite long...). We expect 16 pages.

# In[13]:


len(documents)


# ## Sample 4
# 
# You have the option to pass an additional parameter called `linearization_config` to the AmazonTextractPDFLoader which will determine how the the text output will be linearized by the parser after Textract runs.

# In[ ]:


from langchain_community.document_loaders import AmazonTextractPDFLoader
from textractor.data.text_linearization_config import TextLinearizationConfig

loader = AmazonTextractPDFLoader(
    "s3://amazon-textract-public-content/langchain/layout-parser-paper.pdf",
    linearization_config=TextLinearizationConfig(
        hide_header_layout=True,
        hide_footer_layout=True,
        hide_figure_layout=True,
    ),
)
documents = loader.load()


# ## Using the AmazonTextractPDFLoader in an LangChain chain (e. g. OpenAI)
# 
# The AmazonTextractPDFLoader can be used in a chain the same way the other loaders are used.
# Textract itself does have a [Query feature](https://docs.aws.amazon.com/textract/latest/dg/API_Query.html), which offers similar functionality to the QA chain in this sample, which is worth checking out as well.

# In[14]:


# You can store your OPENAI_API_KEY in a .env file as well
# import os
# from dotenv import load_dotenv

# load_dotenv()


# In[15]:


# Or set the OpenAI key in the environment directly
import os

os.environ["OPENAI_API_KEY"] = "your-OpenAI-API-key"


# In[16]:


from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI

chain = load_qa_chain(llm=OpenAI(), chain_type="map_reduce")
query = ["Who are the autors?"]

chain.run(input_documents=documents, question=query)


# 
