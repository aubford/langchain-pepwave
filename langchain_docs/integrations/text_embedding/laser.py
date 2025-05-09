#!/usr/bin/env python
# coding: utf-8

# # LASER Language-Agnostic SEntence Representations Embeddings by Meta AI
# 
# >[LASER](https://github.com/facebookresearch/LASER/) is a Python library developed by the Meta AI Research team and used for creating multilingual sentence embeddings for over 147 languages as of 2/25/2024 
# >- List of supported languages at https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200

# ## Dependencies
# 
# To use LaserEmbed with LangChain, install the `laser_encoders` Python package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install laser_encoders')


# ## Imports

# In[2]:


from langchain_community.embeddings.laser import LaserEmbeddings


# ## Instantiating Laser
#    
# ### Parameters
# - `lang: Optional[str]`
#     >If empty will default
#     to using a multilingual LASER encoder model (called "laser2").
#     You can find the list of supported languages and lang_codes [here](https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200)
#     and [here](https://github.com/facebookresearch/LASER/blob/main/laser_encoders/language_list.py)
# .

# In[ ]:


# Ex Instantiationz
embeddings = LaserEmbeddings(lang="eng_Latn")


# ## Usage
# 
# ### Generating document embeddings

# In[ ]:


document_embeddings = embeddings.embed_documents(
    ["This is a sentence", "This is some other sentence"]
)


# ### Generating query embeddings

# In[ ]:


query_embeddings = embeddings.embed_query("This is a query")

