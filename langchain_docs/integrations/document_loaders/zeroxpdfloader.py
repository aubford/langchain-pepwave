#!/usr/bin/env python
# coding: utf-8

# # ZeroxPDFLoader
# 
# ## Overview
# `ZeroxPDFLoader` is a document loader that leverages the [Zerox](https://github.com/getomni-ai/zerox) library. Zerox converts PDF documents into images, processes them using a vision-capable language model, and generates a structured Markdown representation. This loader allows for asynchronous operations and provides page-level document extraction.
# 
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support|
# | :--- | :--- | :---: | :---: |  :---: |
# | [ZeroxPDFLoader](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.pdf.ZeroxPDFLoader.html) | [langchain_community](https://python.langchain.com/api_reference/community/index.html) | ❌ | ❌ | ❌ | 
# 
# ### Loader features
# | Source | Document Lazy Loading | Native Async Support
# | :---: | :---: | :---: | 
# | ZeroxPDFLoader | ✅ | ❌ | 
# 
# ## Setup
# 
# ### Credentials
# Appropriate credentials need to be set up in environment variables. The loader supports number of different models and model providers. See _Usage_ header below to see few examples or [Zerox documentation](https://github.com/getomni-ai/zerox) for a full list of supported models.
# 
# ### Installation
# To use `ZeroxPDFLoader`, you need to install the `zerox` package. Also make sure to have `langchain-community` installed.
# 
# ```bash
# pip install zerox langchain-community
# ```
# 

# ## Initialization
# 
# `ZeroxPDFLoader` enables PDF text extraction using vision-capable language models by converting each page into an image and processing it asynchronously. To use this loader, you need to specify a model and configure any necessary environment variables for Zerox, such as API keys.
# 
# If you're working in an environment like Jupyter Notebook, you may need to handle asynchronous code by using `nest_asyncio`. You can set this up as follows:
# 
# ```python
# import nest_asyncio
# nest_asyncio.apply()
# ```
# 

# In[ ]:


import os

# use nest_asyncio (only necessary inside of jupyter notebook)
import nest_asyncio
from langchain_community.document_loaders.pdf import ZeroxPDFLoader

nest_asyncio.apply()

# Specify the url or file path for the PDF you want to process
# In this case let's use pdf from web
file_path = "https://assets.ctfassets.net/f1df9zr7wr1a/soP1fjvG1Wu66HJhu3FBS/034d6ca48edb119ae77dec5ce01a8612/OpenAI_Sacra_Teardown.pdf"

# Set up necessary env vars for a vision model
os.environ["OPENAI_API_KEY"] = (
    "zK3BAhQUmbwZNoHoOcscBwQdwi3oc3hzwJmbgdZ"  ## your-api-key
)

# Initialize ZeroxPDFLoader with the desired model
loader = ZeroxPDFLoader(file_path=file_path, model="azure/gpt-4o-mini")


# ## Load

# In[ ]:


# Load the document and look at the first page:
documents = loader.load()
documents[0]


# In[ ]:


# Let's look at parsed first page
print(documents[0].page_content)


# ## Lazy Load
# The loader always fetches results lazily. `.load()` method is equivalent to `.lazy_load()` 

# ## API reference
# 
# ### `ZeroxPDFLoader`
# 
# This loader class initializes with a file path and model type, and supports custom configurations via `zerox_kwargs` for handling Zerox-specific parameters.
# 
# **Arguments**:
# - `file_path` (Union[str, Path]): Path to the PDF file.
# - `model` (str): Vision-capable model to use for processing in format `<provider>/<model>`.
# Some examples of valid values are: 
#   - `model = "gpt-4o-mini" ## openai model`
#   - `model = "azure/gpt-4o-mini"`
#   - `model = "gemini/gpt-4o-mini"`
#   - `model="claude-3-opus-20240229"`
#   - `model = "vertex_ai/gemini-1.5-flash-001"`
#   - See more details in [Zerox documentation](https://github.com/getomni-ai/zerox)
#   - Defaults to `"gpt-4o-mini".`
# - `**zerox_kwargs` (dict): Additional Zerox-specific parameters such as API key, endpoint, etc.
#   - See [Zerox documentation](https://github.com/getomni-ai/zerox)
# 
# **Methods**:
# - `lazy_load`: Generates an iterator of `Document` instances, each representing a page of the PDF, along with metadata including page number and source.
# 
# See full API documentaton [here](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.pdf.ZeroxPDFLoader.html)

# ## Notes
# - **Model Compatibility**: Zerox supports a range of vision-capable models. Refer to [Zerox's GitHub documentation](https://github.com/getomni-ai/zerox) for a list of supported models and configuration details.
# - **Environment Variables**: Make sure to set required environment variables, such as `API_KEY` or endpoint details, as specified in the Zerox documentation.
# - **Asynchronous Processing**: If you encounter errors related to event loops in Jupyter Notebooks, you may need to apply `nest_asyncio` as shown in the setup section.
# 

# ## Troubleshooting
# - **RuntimeError: This event loop is already running**: Use `nest_asyncio.apply()` to prevent asynchronous loop conflicts in environments like Jupyter.
# - **Configuration Errors**: Verify that the `zerox_kwargs` match the expected arguments for your chosen model and that all necessary environment variables are set.
# 

# ## Additional Resources
# - **Zerox Documentation**: [Zerox GitHub Repository](https://github.com/getomni-ai/zerox)
# - **LangChain Document Loaders**: [LangChain Documentation](https://python.langchain.com/docs/integrations/document_loaders/)
