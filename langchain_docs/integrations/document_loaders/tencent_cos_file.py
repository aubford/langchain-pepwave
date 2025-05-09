#!/usr/bin/env python
# coding: utf-8

# # Tencent COS File
# 
# >[Tencent Cloud Object Storage (COS)](https://www.tencentcloud.com/products/cos) is a distributed 
# > storage service that enables you to store any amount of data from anywhere via HTTP/HTTPS protocols. 
# > `COS` has no restrictions on data structure or format. It also has no bucket size limit and 
# > partition management, making it suitable for virtually any use case, such as data delivery, 
# > data processing, and data lakes. `COS` provides a web-based console, multi-language SDKs and APIs, 
# > command line tool, and graphical tools. It works well with Amazon S3 APIs, allowing you to quickly 
# > access community tools and plugins.
# 
# This covers how to load document object from a `Tencent COS File`.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  cos-python-sdk-v5')


# In[2]:


from langchain_community.document_loaders import TencentCOSFileLoader
from qcloud_cos import CosConfig


# In[3]:


conf = CosConfig(
    Region="your cos region",
    SecretId="your cos secret_id",
    SecretKey="your cos secret_key",
)
loader = TencentCOSFileLoader(conf=conf, bucket="you_cos_bucket", key="fake.docx")


# In[ ]:


loader.load()


# 
