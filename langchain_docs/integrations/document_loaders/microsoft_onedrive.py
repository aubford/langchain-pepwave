#!/usr/bin/env python
# coding: utf-8

# # Microsoft OneDrive
# 
# >[Microsoft OneDrive](https://en.wikipedia.org/wiki/OneDrive) (formerly `SkyDrive`) is a file hosting service operated by Microsoft.
# 
# This notebook covers how to load documents from `OneDrive`. By default the document loader loads `pdf`, `doc`, `docx` and `txt` files. You can load other file types by providing appropriate parsers (see more below).
# 
# ## Prerequisites
# 1. Register an application with the [Microsoft identity platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) instructions.
# 2. When registration finishes, the Azure portal displays the app registration's Overview pane. You see the Application (client) ID. Also called the `client ID`, this value uniquely identifies your application in the Microsoft identity platform.
# 3. During the steps you will be following at **item 1**, you can set the redirect URI as `http://localhost:8000/callback`
# 4. During the steps you will be following at **item 1**, generate a new password (`client_secret`) under Application Secrets section.
# 5. Follow the instructions at this [document](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-configure-app-expose-web-apis#add-a-scope) to add the following `SCOPES` (`offline_access` and `Files.Read.All`) to your application.
# 6. Visit the [Graph Explorer Playground](https://developer.microsoft.com/en-us/graph/graph-explorer) to obtain your `OneDrive ID`. The first step is to ensure you are logged in with the account associated your OneDrive account. Then you need to make a request to `https://graph.microsoft.com/v1.0/me/drive` and the response will return a payload with a field `id` that holds the ID of your OneDrive account.
# 7. You need to install the o365 package using the command `pip install o365`.
# 8. At the end of the steps you must have the following values: 
# - `CLIENT_ID`
# - `CLIENT_SECRET`
# - `DRIVE_ID`
# 
# ## 🧑 Instructions for ingesting your documents from OneDrive
# 
# ### 🔑 Authentication
# 
# By default, the `OneDriveLoader` expects that the values of `CLIENT_ID` and `CLIENT_SECRET` must be stored as environment variables named `O365_CLIENT_ID` and `O365_CLIENT_SECRET` respectively. You could pass those environment variables through a `.env` file at the root of your application or using the following command in your script.
# 
# ```python
# os.environ['O365_CLIENT_ID'] = "YOUR CLIENT ID"
# os.environ['O365_CLIENT_SECRET'] = "YOUR CLIENT SECRET"
# ```
# 
# This loader uses an authentication called [*on behalf of a user*](https://learn.microsoft.com/en-us/graph/auth-v2-user?context=graph%2Fapi%2F1.0&view=graph-rest-1.0). It is a 2 step authentication with user consent. When you instantiate the loader, it will call will print a url that the user must visit to give consent to the app on the required permissions. The user must then visit this url and give consent to the application. Then the user must copy the resulting page url and paste it back on the console. The method will then return True if the login attempt was successful.
# 
# 
# ```python
# from langchain_community.document_loaders.onedrive import OneDriveLoader
# 
# loader = OneDriveLoader(drive_id="YOUR DRIVE ID")
# ```
# 
# Once the authentication has been done, the loader will store a token (`o365_token.txt`) at `~/.credentials/` folder. This token could be used later to authenticate without the copy/paste steps explained earlier. To use this token for authentication, you need to change the `auth_with_token` parameter to True in the instantiation of the loader.
# 
# ```python
# from langchain_community.document_loaders.onedrive import OneDriveLoader
# 
# loader = OneDriveLoader(drive_id="YOUR DRIVE ID", auth_with_token=True)
# ```
# 
# ### 🗂️ Documents loader
# 
# #### 📑 Loading documents from a OneDrive Directory
# 
# `OneDriveLoader` can load documents from a specific folder within your OneDrive. For instance, you want to load all documents that are stored at `Documents/clients` folder within your OneDrive.
# 
# 
# ```python
# from langchain_community.document_loaders.onedrive import OneDriveLoader
# 
# loader = OneDriveLoader(drive_id="YOUR DRIVE ID", folder_path="Documents/clients", auth_with_token=True)
# documents = loader.load()
# ```
# 
# #### 📑 Loading documents from a list of Documents IDs
# 
# Another possibility is to provide a list of `object_id` for each document you want to load. For that, you will need to query the [Microsoft Graph API](https://developer.microsoft.com/en-us/graph/graph-explorer) to find all the documents ID that you are interested in. This [link](https://learn.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0#commonly-accessed-resources) provides a list of endpoints that will be helpful to retrieve the documents ID.
# 
# For instance, to retrieve information about all objects that are stored at the root of the Documents folder, you need make a request to: `https://graph.microsoft.com/v1.0/drives/{YOUR DRIVE ID}/root/children`. Once you have the list of IDs that you are interested in, then you can instantiate the loader with the following parameters.
# 
# 
# ```python
# from langchain_community.document_loaders.onedrive import OneDriveLoader
# 
# loader = OneDriveLoader(drive_id="YOUR DRIVE ID", object_ids=["ID_1", "ID_2"], auth_with_token=True)
# documents = loader.load()
# ```
# 
# #### 📑 Choosing supported file types and preffered parsers
# By default `OneDriveLoader` loads file types defined in [`document_loaders/parsers/registry`](https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/document_loaders/parsers/registry.py#L10-L22) using the default parsers (see below).
# ```python
# def _get_default_parser() -> BaseBlobParser:
#     """Get default mime-type based parser."""
#     return MimeTypeBasedParser(
#         handlers={
#             "application/pdf": PyMuPDFParser(),
#             "text/plain": TextParser(),
#             "application/msword": MsWordParser(),
#             "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
#                 MsWordParser()
#             ),
#         },
#         fallback_parser=None,
#     )
# ```
# You can override this behavior by passing `handlers` argument to `OneDriveLoader`. 
# Pass a dictionary mapping either file extensions (like `"doc"`, `"pdf"`, etc.) 
# or MIME types (like `"application/pdf"`, `"text/plain"`, etc.) to parsers. 
# Note that you must use either file extensions or MIME types exclusively and 
# cannot mix them.
# 
# Do not include the leading dot for file extensions.
# 
# ```python
# # using file extensions:
# handlers = {
#     "doc": MsWordParser(),
#     "pdf": PDFMinerParser(),
#     "mp3": OpenAIWhisperParser()
# }
# 
# # using MIME types:
# handlers = {
#     "application/msword": MsWordParser(),
#     "application/pdf": PDFMinerParser(),
#     "audio/mpeg": OpenAIWhisperParser()
# }
# 
# loader = OneDriveLoader(document_library_id="...",
#                             handlers=handlers # pass handlers to OneDriveLoader
#                             )
# ```
# In case multiple file extensions map to the same MIME type, the last dictionary item will
# apply.
# Example:
# ```python
# # 'jpg' and 'jpeg' both map to 'image/jpeg' MIME type. SecondParser() will be used 
# # to parse all jpg/jpeg files.
# handlers = {
#     "jpg": FirstParser(),
#     "jpeg": SecondParser()
# }
# ```
