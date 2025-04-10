#!/usr/bin/env python
# coding: utf-8

# # Yuan2.0
# 
# [Yuan2.0](https://github.com/IEIT-Yuan/Yuan-2.0) is a new generation Fundamental Large Language Model developed by IEIT System. We have published all three models, Yuan 2.0-102B, Yuan 2.0-51B, and Yuan 2.0-2B. And we provide relevant scripts for pretraining, fine-tuning, and inference services for other developers. Yuan2.0 is based on Yuan1.0, utilizing a wider range of high-quality pre training data and instruction fine-tuning datasets to enhance the model's understanding of semantics, mathematics, reasoning, code, knowledge, and other aspects.
# 
# This example goes over how to use LangChain to interact with `Yuan2.0`(2B/51B/102B) Inference for text generation.
# 
# Yuan2.0 set up an inference service so user just need request the inference api to get result, which is introduced in [Yuan2.0 Inference-Server](https://github.com/IEIT-Yuan/Yuan-2.0/blob/main/docs/inference_server.md).

# In[ ]:


from langchain.chains import LLMChain
from langchain_community.llms.yuan2 import Yuan2


# In[ ]:


# default infer_api for a local deployed Yuan2.0 inference server
infer_api = "http://127.0.0.1:8000/yuan"

# direct access endpoint in a proxied environment
# import os
# os.environ["no_proxy"]="localhost,127.0.0.1,::1"

yuan_llm = Yuan2(
    infer_api=infer_api,
    max_tokens=2048,
    temp=1.0,
    top_p=0.9,
    use_history=False,
)

# turn on use_history only when you want the Yuan2.0 to keep track of the conversation history
# and send the accumulated context to the backend model api, which make it stateful. By default it is stateless.
# llm.use_history = True


# In[24]:


question = "请介绍一下中国。"


# In[ ]:


print(yuan_llm.invoke(question))

