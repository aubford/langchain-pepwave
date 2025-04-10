#!/usr/bin/env python
# coding: utf-8

# This notebook shows how to use the RSpace document loader to import research notes and documents from RSpace Electronic
# Lab Notebook into Langchain pipelines.
# 
# To start you'll need an RSpace account and an API key.
# 
# You can set up a free account at [https://community.researchspace.com](https://community.researchspace.com) or use your institutional RSpace.
# 
# You can get an RSpace API token from your account's profile page. 

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  rspace_client')


# It's best to store your RSpace API key as an environment variable. 
# 
#     RSPACE_API_KEY=&lt;YOUR_KEY&gt;
# 
# You'll also need to set the URL of your RSpace installation e.g.
# 
#     RSPACE_URL=https://community.researchspace.com
# 
# If you use these exact environment variable names, they will be detected automatically. 

# In[5]:


from langchain_community.document_loaders.rspace import RSpaceLoader


# You can import various items from RSpace:
# 
# * A single RSpace structured or basic document. This will map 1-1 to a Langchain document.
# * A folder or noteook. All documents inside the notebook or folder are imported as Langchain documents. 
# * If you have PDF files in the RSpace Gallery, these can be imported individually as well. Under the hood, Langchain's PDF loader will be used and this creates one Langchain document per PDF page. 

# In[ ]:


## replace these ids with some from your own research notes.
## Make sure to use  global ids (with the 2 character prefix). This helps the loader know which API calls to make
## to RSpace API.

rspace_ids = ["NB1932027", "FL1921314", "SD1932029", "GL1932384"]
for rs_id in rspace_ids:
    loader = RSpaceLoader(global_id=rs_id)
    docs = loader.load()
    for doc in docs:
        ## the name and ID are added to the 'source' metadata property.
        print(doc.metadata)
        print(doc.page_content[:500])


# If you don't want to use the environment variables as above, you can pass these into the RSpaceLoader

# In[ ]:


loader = RSpaceLoader(
    global_id=rs_id, api_key="MY_API_KEY", url="https://my.researchspace.com"
)

