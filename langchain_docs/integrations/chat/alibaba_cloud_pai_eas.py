#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Alibaba Cloud PAI EAS
---
# # Alibaba Cloud PAI EAS
# 
# >[Alibaba Cloud PAI (Platform for AI)](https://www.alibabacloud.com/help/en/pai/?spm=a2c63.p38356.0.0.c26a426ckrxUwZ) is a lightweight and cost-efficient machine learning platform that uses cloud-native technologies. It provides you with an end-to-end modelling service. It accelerates model training based on tens of billions of features and hundreds of billions of samples in more than 100 scenarios.
# 
# >[Machine Learning Platform for AI of Alibaba Cloud](https://www.alibabacloud.com/help/en/machine-learning-platform-for-ai/latest/what-is-machine-learning-pai) is a machine learning or deep learning engineering platform intended for enterprises and developers. It provides easy-to-use, cost-effective, high-performance, and easy-to-scale plug-ins that can be applied to various industry scenarios. With over 140 built-in optimization algorithms, `Machine Learning Platform for AI` provides whole-process AI engineering capabilities including data labelling (`PAI-iTAG`), model building (`PAI-Designer` and `PAI-DSW`), model training (`PAI-DLC`), compilation optimization, and inference deployment (`PAI-EAS`).
# >
# >`PAI-EAS` supports different types of hardware resources, including CPUs and GPUs, and features high throughput and low latency. It allows you to deploy large-scale complex models with a few clicks and perform elastic scale-ins and scale-outs in real-time. It also provides a comprehensive O&M and monitoring system.

# ## Setup EAS Service
# 
# Set up environment variables to init EAS service URL and token.
# Use [this document](https://www.alibabacloud.com/help/en/pai/user-guide/service-deployment/) for more information.
# 
# ```bash
# export EAS_SERVICE_URL=XXX
# export EAS_SERVICE_TOKEN=XXX
# ```
# Another option is to use this code:

# In[9]:


import os

from langchain_community.chat_models import PaiEasChatEndpoint
from langchain_core.language_models.chat_models import HumanMessage

os.environ["EAS_SERVICE_URL"] = "Your_EAS_Service_URL"
os.environ["EAS_SERVICE_TOKEN"] = "Your_EAS_Service_Token"
chat = PaiEasChatEndpoint(
    eas_service_url=os.environ["EAS_SERVICE_URL"],
    eas_service_token=os.environ["EAS_SERVICE_TOKEN"],
)


# ## Run Chat Model
# 
# You can use the default settings to call EAS service as follows:

# In[ ]:


output = chat.invoke([HumanMessage(content="write a funny joke")])
print("output:", output)


# Or, call EAS service with new inference params:

# In[ ]:


kwargs = {"temperature": 0.8, "top_p": 0.8, "top_k": 5}
output = chat.invoke([HumanMessage(content="write a funny joke")], **kwargs)
print("output:", output)


# Or, run a stream call to get a stream response:

# In[ ]:


outputs = chat.stream([HumanMessage(content="hi")], streaming=True)
for output in outputs:
    print("stream output:", output)

