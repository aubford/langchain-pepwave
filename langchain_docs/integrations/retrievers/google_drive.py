#!/usr/bin/env python
# coding: utf-8

# # Google Drive
# 
# This notebook covers how to retrieve documents from `Google Drive`.
# 
# ## Prerequisites
# 
# 1. Create a Google Cloud project or use an existing project
# 1. Enable the [Google Drive API](https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com)
# 1. [Authorize credentials for desktop app](https://developers.google.com/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
# 1. `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
# 
# ## Retrieve the Google Docs
# 
# By default, the `GoogleDriveRetriever` expects the `credentials.json` file to be `~/.credentials/credentials.json`, but this is configurable using the `GOOGLE_ACCOUNT_FILE` environment variable. 
# The location of `token.json` uses the same directory (or use the parameter `token_path`). Note that `token.json` will be created automatically the first time you use the retriever.
# 
# `GoogleDriveRetriever` can retrieve a selection of files with some requests. 
# 
# By default, If you use a `folder_id`, all the files inside this folder can be retrieved to `Document`.
# 

# You can obtain your folder and document id from the URL:
# 
# * Folder: https://drive.google.com/drive/u/0/folders/1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5 -> folder id is `"1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5"`
# * Document: https://docs.google.com/document/d/1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw/edit -> document id is `"1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw"`
# 
# The special value `root` is for your personal home.

# In[ ]:


from langchain_googledrive.retrievers import GoogleDriveRetriever

folder_id = "root"
# folder_id='1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5'

retriever = GoogleDriveRetriever(
    num_results=2,
)


# By default, all files with these MIME types can be converted to `Document`.
# 
# - `text/text`
# - `text/plain`
# - `text/html`
# - `text/csv`
# - `text/markdown`
# - `image/png`
# - `image/jpeg`
# - `application/epub+zip`
# - `application/pdf`
# - `application/rtf`
# - `application/vnd.google-apps.document` (GDoc)
# - `application/vnd.google-apps.presentation` (GSlide)
# - `application/vnd.google-apps.spreadsheet` (GSheet)
# - `application/vnd.google.colaboratory` (Notebook colab)
# - `application/vnd.openxmlformats-officedocument.presentationml.presentation` (PPTX)
# - `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (DOCX)
# 
# It's possible to update or customize this. See the documentation of `GoogleDriveRetriever`.
# 
# But, the corresponding packages must be installed.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  unstructured')


# In[ ]:


retriever.invoke("machine learning")


# You can customize the criteria to select the files. A set of predefined filter are proposed:
# 
# | Template                                 | Description                                                           |
# | --------------------------------------   | --------------------------------------------------------------------- |
# | `gdrive-all-in-folder`                   | Return all compatible files from a `folder_id`                        |
# | `gdrive-query`                           | Search `query` in all drives                                          |
# | `gdrive-by-name`                         | Search file with name `query`                                         |
# | `gdrive-query-in-folder`                 | Search `query` in `folder_id` (and sub-folders in `_recursive=true`)  |
# | `gdrive-mime-type`                       | Search a specific `mime_type`                                         |
# | `gdrive-mime-type-in-folder`             | Search a specific `mime_type` in `folder_id`                          |
# | `gdrive-query-with-mime-type`            | Search `query` with a specific `mime_type`                            |
# | `gdrive-query-with-mime-type-and-folder` | Search `query` with a specific `mime_type` and in `folder_id`         |

# In[ ]:


retriever = GoogleDriveRetriever(
    template="gdrive-query",  # Search everywhere
    num_results=2,  # But take only 2 documents
)
for doc in retriever.invoke("machine learning"):
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# Else, you can customize the prompt with a specialized `PromptTemplate`

# In[ ]:


from langchain_core.prompts import PromptTemplate

retriever = GoogleDriveRetriever(
    template=PromptTemplate(
        input_variables=["query"],
        # See https://developers.google.com/drive/api/guides/search-files
        template="(fullText contains '{query}') "
        "and mimeType='application/vnd.google-apps.document' "
        "and modifiedTime > '2000-01-01T00:00:00' "
        "and trashed=false",
    ),
    num_results=2,
    # See https://developers.google.com/drive/api/v3/reference/files/list
    includeItemsFromAllDrives=False,
    supportsAllDrives=False,
)
for doc in retriever.invoke("machine learning"):
    print(f"{doc.metadata['name']}:")
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# ## Use Google Drive 'description' metadata
# 
# Each Google Drive has a `description` field in metadata (see the *details of a file*).
# Use the `snippets` mode to return the description of selected files.
# 

# In[ ]:


retriever = GoogleDriveRetriever(
    template="gdrive-mime-type-in-folder",
    folder_id=folder_id,
    mime_type="application/vnd.google-apps.document",  # Only Google Docs
    num_results=2,
    mode="snippets",
    includeItemsFromAllDrives=False,
    supportsAllDrives=False,
)
retriever.invoke("machine learning")

