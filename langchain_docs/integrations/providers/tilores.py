#!/usr/bin/env python
# coding: utf-8

# # Tilores
# 
# [Tilores](https://tilores.io) is a platform that provides advanced entity resolution solutions for data integration and management. Using cutting-edge algorithms, machine learning, and a user-friendly interfaces, Tilores helps organizations match, resolve, and consolidate data from disparate sources, ensuring high-quality, consistent information.

# ## Installation and Setup

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade tilores-langchain')


# To access Tilores, you need to [create and configure an instance](https://app.tilores.io). If you prefer to test out Tilores first, you can use the [read-only demo credentials](https://github.com/tilotech/identity-rag-customer-insights-chatbot?tab=readme-ov-file#1-configure-customer-data-access).

# In[11]:


import os

from tilores import TiloresAPI

os.environ["TILORES_API_URL"] = "<api-url>"
os.environ["TILORES_TOKEN_URL"] = "<token-url>"
os.environ["TILORES_CLIENT_ID"] = "<client-id>"
os.environ["TILORES_CLIENT_SECRET"] = "<client-secret>"

tilores = TiloresAPI.from_environ()


# Please refer to the [Tilores documentation](https://docs.tilotech.io/tilores/publicsaaswalkthrough/) on how to create your own instance.

# ## Toolkits
# 
# You can use the [`TiloresTools`](/docs/integrations/tools/tilores) to query data from Tilores:

# In[ ]:


from tilores_langchain import TiloresTools

