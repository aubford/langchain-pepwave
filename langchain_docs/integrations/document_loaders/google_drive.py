#!/usr/bin/env python
# coding: utf-8

# # Google Drive
# 
# >[Google Drive](https://en.wikipedia.org/wiki/Google_Drive) is a file storage and synchronization service developed by Google.
# 
# This notebook covers how to load documents from `Google Drive`. Currently, only `Google Docs` are supported.
# 
# ## Prerequisites
# 
# 1. Create a Google Cloud project or use an existing project
# 1. Enable the [Google Drive API](https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com)
# 1. [Authorize credentials for desktop app](https://developers.google.com/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
# 1. `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
# 
# ## 🧑 Instructions for ingesting your Google Docs data
# Set the environmental variable `GOOGLE_APPLICATION_CREDENTIALS` to an empty string (`""`).
# 
# By default, the `GoogleDriveLoader` expects the `credentials.json` file to be located at `~/.credentials/credentials.json`, but this is configurable using the `credentials_path` keyword argument. Same thing with `token.json` - default path: `~/.credentials/token.json`, constructor param: `token_path`.
# 
# The first time you use GoogleDriveLoader, you will be displayed with the consent screen in your browser for user authentication. After authentication, `token.json` will be created automatically at the provided or the default path. Also, if there is already a `token.json` at that path, then you will not be prompted for authentication.
# 
# `GoogleDriveLoader` can load from a list of Google Docs document ids or a folder id. You can obtain your folder and document id from the URL:
# 
# * Folder: https://drive.google.com/drive/u/0/folders/1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5 -> folder id is `"1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5"`
# * Document: https://docs.google.com/document/d/1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw/edit -> document id is `"1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw"`

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-google-community[drive]')


# In[ ]:


from langchain_google_community import GoogleDriveLoader


# In[ ]:


loader = GoogleDriveLoader(
    folder_id="1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5",
    token_path="/path/where/you/want/token/to/be/created/google_token.json",
    # Optional: configure whether to recursively fetch files from subfolders. Defaults to False.
    recursive=False,
)


# In[ ]:


docs = loader.load()


# When you pass a `folder_id` by default all files of type document, sheet and pdf are loaded. You can modify this behaviour by passing a `file_types` argument 

# In[ ]:


loader = GoogleDriveLoader(
    folder_id="1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5",
    file_types=["document", "sheet"],
    recursive=False,
)


# ## Passing in Optional File Loaders
# 
# When processing files other than Google Docs and Google Sheets, it can be helpful to pass an optional file loader to `GoogleDriveLoader`. If you pass in a file loader, that file loader will be used on documents that do not have a Google Docs or Google Sheets MIME type. Here is an example of how to load an Excel document from Google Drive using a file loader. 

# In[ ]:


from langchain_community.document_loaders import UnstructuredFileIOLoader
from langchain_google_community import GoogleDriveLoader


# In[ ]:


file_id = "1x9WBtFPWMEAdjcJzPScRsjpjQvpSo_kz"
loader = GoogleDriveLoader(
    file_ids=[file_id],
    file_loader_cls=UnstructuredFileIOLoader,
    file_loader_kwargs={"mode": "elements"},
)


# In[ ]:


docs = loader.load()


# In[ ]:


docs[0]


# You can also process a folder with a mix of files and Google Docs/Sheets using the following pattern:

# In[ ]:


folder_id = "1asMOHY1BqBS84JcRbOag5LOJac74gpmD"
loader = GoogleDriveLoader(
    folder_id=folder_id,
    file_loader_cls=UnstructuredFileIOLoader,
    file_loader_kwargs={"mode": "elements"},
)


# In[ ]:


docs = loader.load()


# In[ ]:


docs[0]


# In[ ]:





# ## Extended usage
# An external (unofficial) component can manage the complexity of Google Drive : `langchain-googledrive`
# It's compatible with the ̀`langchain_community.document_loaders.GoogleDriveLoader` and can be used
# in its place.
# 
# To be compatible with containers, the authentication uses an environment variable `̀GOOGLE_ACCOUNT_FILE` to credential file (for user or service).

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-googledrive')


# In[ ]:


folder_id = "root"
# folder_id='1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5'


# In[ ]:


# Use the advanced version.
from langchain_googledrive.document_loaders import GoogleDriveLoader


# In[ ]:


loader = GoogleDriveLoader(
    folder_id=folder_id,
    recursive=False,
    num_results=2,  # Maximum number of file to load
)


# By default, all files with these mime-type can be converted to `Document`.
# - text/text
# - text/plain
# - text/html
# - text/csv
# - text/markdown
# - image/png
# - image/jpeg
# - application/epub+zip
# - application/pdf
# - application/rtf
# - application/vnd.google-apps.document (GDoc)
# - application/vnd.google-apps.presentation (GSlide)
# - application/vnd.google-apps.spreadsheet (GSheet)
# - application/vnd.google.colaboratory (Notebook colab)
# - application/vnd.openxmlformats-officedocument.presentationml.presentation (PPTX)
# - application/vnd.openxmlformats-officedocument.wordprocessingml.document (DOCX)
# 
# It's possible to update or customize this. See the documentation of `GDriveLoader`.
# 
# But, the corresponding packages must be installed.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  unstructured')


# In[ ]:


for doc in loader.load():
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# ### Loading auth Identities
# 
# Authorized identities for each file ingested by Google Drive Loader can be loaded along with metadata per Document.

# In[ ]:


from langchain_google_community import GoogleDriveLoader

loader = GoogleDriveLoader(
    folder_id=folder_id,
    load_auth=True,
    # Optional: configure whether to load authorized identities for each Document.
)

doc = loader.load()


# You can pass load_auth=True, to add Google Drive document access identities to metadata.

# In[ ]:


doc[0].metadata


# ### Loading extended metadata
# Following extra fields can also be fetched within metadata of each Document:
#  - full_path - Full path of the file/s in google drive.
#  - owner - owner of the file/s.
#  - size - size of the file/s.

# In[ ]:


from langchain_google_community import GoogleDriveLoader

loader = GoogleDriveLoader(
    folder_id=folder_id,
    load_extended_matadata=True,
    # Optional: configure whether to load extended metadata for each Document.
)

doc = loader.load()


# You can pass load_extended_matadata=True, to add Google Drive document extended details to metadata.

# In[ ]:


doc[0].metadata


# ### Customize the search pattern
# 
# All parameter compatible with Google [`list()`](https://developers.google.com/drive/api/v3/reference/files/list)
# API can be set.
# 
# To specify the new pattern of the Google request, you can use a `PromptTemplate()`.
# The variables for the prompt can be set with `kwargs` in the constructor.
# Some pre-formated request are proposed (use `{query}`, `{folder_id}` and/or `{mime_type}`):
# 
# You can customize the criteria to select the files. A set of predefined filter are proposed:
# 
# | template                               | description                                                           |
# | -------------------------------------- | --------------------------------------------------------------------- |
# | gdrive-all-in-folder                   | Return all compatible files from a `folder_id`                        |
# | gdrive-query                           | Search `query` in all drives                                          |
# | gdrive-by-name                         | Search file with name `query`                                        |
# | gdrive-query-in-folder                 | Search `query` in `folder_id` (and sub-folders if `recursive=true`)  |
# | gdrive-mime-type                       | Search a specific `mime_type`                                         |
# | gdrive-mime-type-in-folder             | Search a specific `mime_type` in `folder_id`                          |
# | gdrive-query-with-mime-type            | Search `query` with a specific `mime_type`                            |
# | gdrive-query-with-mime-type-and-folder | Search `query` with a specific `mime_type` and in `folder_id`         |
# 

# In[ ]:


loader = GoogleDriveLoader(
    folder_id=folder_id,
    recursive=False,
    template="gdrive-query",  # Default template to use
    query="machine learning",
    num_results=2,  # Maximum number of file to load
    supportsAllDrives=False,  # GDrive `list()` parameter
)
for doc in loader.load():
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# You can customize your pattern.

# In[ ]:


from langchain_core.prompts.prompt import PromptTemplate

loader = GoogleDriveLoader(
    folder_id=folder_id,
    recursive=False,
    template=PromptTemplate(
        input_variables=["query", "query_name"],
        template="fullText contains '{query}' and name contains '{query_name}' and trashed=false",
    ),  # Default template to use
    query="machine learning",
    query_name="ML",
    num_results=2,  # Maximum number of file to load
)
for doc in loader.load():
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# The conversion can manage in Markdown format:
# - bullet
# - link
# - table
# - titles
# 
# Set the attribut `return_link` to `True` to export links.
# 
# #### Modes for GSlide and GSheet
# The parameter mode accepts different values:
# 
# - "document": return the body of each document
# - "snippets": return the description of each file (set in metadata of Google Drive files).
# 
# 
# The parameter `gslide_mode` accepts different values:
# 
# - "single" : one document with &lt;PAGE BREAK&gt;
# - "slide" : one document by slide
# - "elements" : one document for each elements.
# 

# In[ ]:


loader = GoogleDriveLoader(
    template="gdrive-mime-type",
    mime_type="application/vnd.google-apps.presentation",  # Only GSlide files
    gslide_mode="slide",
    num_results=2,  # Maximum number of file to load
)
for doc in loader.load():
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# The parameter `gsheet_mode` accepts different values:
# - `"single"`: Generate one document by line
# - `"elements"` : one document with markdown array and &lt;PAGE BREAK&gt; tags.

# In[ ]:


loader = GoogleDriveLoader(
    template="gdrive-mime-type",
    mime_type="application/vnd.google-apps.spreadsheet",  # Only GSheet files
    gsheet_mode="elements",
    num_results=2,  # Maximum number of file to load
)
for doc in loader.load():
    print("---")
    print(doc.page_content.strip()[:60] + "...")


# ### Advanced usage
# All Google File have a 'description' in the metadata. This field can be used to memorize a summary of the document or others indexed tags (See method `lazy_update_description_with_summary()`).
# 
# If you use the `mode="snippet"`, only the description will be used for the body. Else, the `metadata['summary']` has the field.
# 
# Sometime, a specific filter can be used to extract some information from the filename, to select some files with specific criteria. You can use a filter.
# 
# Sometimes, many documents are returned. It's not necessary to have all documents in memory at the same time. You can use the lazy versions of methods, to get one document at a time. It's better to use a complex query in place of a recursive search. For each folder, a query must be applied if you activate `recursive=True`.

# In[ ]:


import os

loader = GoogleDriveLoader(
    gdrive_api_file=os.environ["GOOGLE_ACCOUNT_FILE"],
    num_results=2,
    template="gdrive-query",
    filter=lambda search, file: "#test" not in file.get("description", ""),
    query="machine learning",
    supportsAllDrives=False,
)
for doc in loader.load():
    print("---")
    print(doc.page_content.strip()[:60] + "...")

