#!/usr/bin/env python
# coding: utf-8

# # Quip
# 
# >[Quip](https://quip.com) is a collaborative productivity software suite for mobile and Web. It allows groups of people to create and edit documents and spreadsheets as a group, typically for business purposes.
# 
# A loader for `Quip` docs.
# 
# Please refer [here](https://quip.com/dev/automation/documentation/current#section/Authentication/Get-Access-to-Quip's-APIs) to know how to get personal access token. 
# 
# Specify a list `folder_ids` and/or `thread_ids` to load in the corresponding docs into Document objects, if both are specified, loader will get all `thread_ids` belong to this folder based on `folder_ids`, combine with passed `thread_ids`, the union of both sets will be returned.
# 
# * How to know folder_id ? 
#   go to quip folder, right click folder and copy link, extract suffix from link as folder_id. Hint:  `https://example.quip.com/<folder_id>`
# * How to know thread_id ? 
#   thread_id is the document id. Go to quip doc, right click doc and copy link, extract suffix from link as thread_id. Hint: `https://exmaple.quip.com/<thread_id>`
#   
# You can also set `include_all_folders` as `True` will fetch group_folder_ids and 
# You can also specify a boolean `include_attachments` to include attachments, this is set to False by default, if set to True all attachments will be downloaded and QuipLoader will extract the text from the attachments and add it to the Document object. Currently supported attachment types are: `PDF`, `PNG`, `JPEG/JPG`, `SVG`, `Word` and `Excel`. Also you can sepcify a boolean `include_comments` to include comments in document, this is set to False by default, if set to True all comments in document will be fetched and QuipLoader will add them to Document objec.
# 

# Before using QuipLoader make sure you have the latest version of the quip-api package installed:

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  quip-api')


# ## Examples

# ### Personal Access Token

# In[ ]:


from langchain_community.document_loaders.quip import QuipLoader

loader = QuipLoader(
    api_url="https://platform.quip.com", access_token="change_me", request_timeout=60
)
documents = loader.load(
    folder_ids={"123", "456"},
    thread_ids={"abc", "efg"},
    include_attachments=False,
    include_comments=False,
)

