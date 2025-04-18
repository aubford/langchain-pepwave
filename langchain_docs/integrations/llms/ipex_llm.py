#!/usr/bin/env python
# coding: utf-8

# # IPEX-LLM
# 
# > [IPEX-LLM](https://github.com/intel-analytics/ipex-llm) is a PyTorch library for running LLM on Intel CPU and GPU (e.g., local PC with iGPU, discrete GPU such as Arc, Flex and Max) with very low latency.
# 
# - [IPEX-LLM on Intel GPU](#ipex-llm-on-intel-gpu)
# - [IPEX-LLM on Intel CPU](#ipex-llm-on-intel-cpu)
# 
# ## IPEX-LLM on Intel GPU
# 
# This example goes over how to use LangChain to interact with `ipex-llm` for text generation on Intel GPU. 
# 
# > **Note**
# >
# > It is recommended that only Windows users with Intel Arc A-Series GPU (except for Intel Arc A300-Series or Pro A60) run Jupyter notebook directly for section "IPEX-LLM on Intel GPU". For other cases (e.g. Linux users, Intel iGPU, etc.), it is recommended to run the code with Python scripts in terminal for best experiences.
# 
# ### Install Prerequisites
# To benefit from IPEX-LLM on Intel GPUs, there are several prerequisite steps for tools installation and environment preparation.
# 
# If you are a Windows user, visit the [Install IPEX-LLM on Windows with Intel GPU Guide](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/install_windows_gpu.md), and follow [Install Prerequisites](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/install_windows_gpu.md#install-prerequisites) to update GPU driver (optional) and install Conda.
# 
# If you are a Linux user, visit the [Install IPEX-LLM on Linux with Intel GPU](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/install_linux_gpu.md), and follow [**Install Prerequisites**](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/install_linux_gpu.md#install-prerequisites) to install GPU driver, Intel® oneAPI Base Toolkit 2024.0, and Conda.
# 
# ### Setup
# 
# After the prerequisites installation, you should have created a conda environment with all prerequisites installed. **Start the jupyter service in this conda environment**:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain-community')


# Install IEPX-LLM for running LLMs locally on Intel GPU.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --pre --upgrade ipex-llm[xpu] --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/')


# > **Note**
# >
# > You can also use `https://pytorch-extension.intel.com/release-whl/stable/xpu/cn/` as the extra-indel-url.
# 
# ### Runtime Configuration
# 
# For optimal performance, it is recommended to set several environment variables based on your device:
# 
# #### For Windows Users with Intel Core Ultra integrated GPU

# In[ ]:


import os

os.environ["SYCL_CACHE_PERSISTENT"] = "1"
os.environ["BIGDL_LLM_XMX_DISABLED"] = "1"


# #### For Windows Users with Intel Arc A-Series GPU

# In[ ]:


import os

os.environ["SYCL_CACHE_PERSISTENT"] = "1"


# > **Note**
# >
# > For the first time that each model runs on Intel iGPU/Intel Arc A300-Series or Pro A60, it may take several minutes to compile.
# >
# > For other GPU type, please refer to [here](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Overview/install_gpu.md#runtime-configuration) for Windows users, and  [here](https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Overview/install_gpu.md#runtime-configuration-1) for Linux users.
# 
# 
# ### Basic Usage
# 

# In[ ]:


import warnings

from langchain.chains import LLMChain
from langchain_community.llms import IpexLLM
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore", category=UserWarning, message=".*padding_mask.*")


# Specify the prompt template for your model. In this example, we use the [vicuna-1.5](https://huggingface.co/lmsys/vicuna-7b-v1.5) model. If you're working with a different model, choose a proper template accordingly.

# In[ ]:


template = "USER: {question}\nASSISTANT:"
prompt = PromptTemplate(template=template, input_variables=["question"])


# Load the model locally using IpexLLM using `IpexLLM.from_model_id`. It will load the model directly in its Huggingface format and convert it automatically to low-bit format for inference. Set `device` to `"xpu"` in `model_kwargs` when initializing IpexLLM in order to load the LLM model to Intel GPU.

# In[ ]:


llm = IpexLLM.from_model_id(
    model_id="lmsys/vicuna-7b-v1.5",
    model_kwargs={
        "temperature": 0,
        "max_length": 64,
        "trust_remote_code": True,
        "device": "xpu",
    },
)


# Use it in Chains

# In[ ]:


llm_chain = prompt | llm

question = "What is AI?"
output = llm_chain.invoke(question)


# ### Save/Load Low-bit Model
# Alternatively, you might save the low-bit model to disk once and use `from_model_id_low_bit` instead of `from_model_id` to reload it for later use - even across different machines. It is space-efficient, as the low-bit model demands significantly less disk space than the original model. And `from_model_id_low_bit` is also more efficient than `from_model_id` in terms of speed and memory usage, as it skips the model conversion step. You can similarly set `device` to `"xpu"` in `model_kwargs` in order to load the LLM model to Intel GPU. 

# To save the low-bit model, use `save_low_bit` as follows.

# In[ ]:


saved_lowbit_model_path = "./vicuna-7b-1.5-low-bit"  # path to save low-bit model
llm.model.save_low_bit(saved_lowbit_model_path)
del llm


# Load the model from saved lowbit model path as follows. 
# > Note that the saved path for the low-bit model only includes the model itself but not the tokenizers. If you wish to have everything in one place, you will need to manually download or copy the tokenizer files from the original model's directory to the location where the low-bit model is saved.

# In[ ]:


llm_lowbit = IpexLLM.from_model_id_low_bit(
    model_id=saved_lowbit_model_path,
    tokenizer_id="lmsys/vicuna-7b-v1.5",
    # tokenizer_name=saved_lowbit_model_path,  # copy the tokenizers to saved path if you want to use it this way
    model_kwargs={
        "temperature": 0,
        "max_length": 64,
        "trust_remote_code": True,
        "device": "xpu",
    },
)


# Use the loaded model in Chains:

# In[ ]:


llm_chain = prompt | llm_lowbit


question = "What is AI?"
output = llm_chain.invoke(question)


# ## IPEX-LLM on Intel CPU
# 
# This example goes over how to use LangChain to interact with `ipex-llm` for text generation on Intel CPU.
# 
# ### Setup

# In[ ]:


# Update Langchain

get_ipython().run_line_magic('pip', 'install -qU langchain langchain-community')


# Install IEPX-LLM for running LLMs locally on Intel CPU:
# 
# #### For Windows users:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --pre --upgrade ipex-llm[all]')


# #### For Linux users:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --pre --upgrade ipex-llm[all] --extra-index-url https://download.pytorch.org/whl/cpu')


# ### Basic Usage

# In[ ]:


import warnings

from langchain.chains import LLMChain
from langchain_community.llms import IpexLLM
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore", category=UserWarning, message=".*padding_mask.*")


# Specify the prompt template for your model. In this example, we use the [vicuna-1.5](https://huggingface.co/lmsys/vicuna-7b-v1.5) model. If you're working with a different model, choose a proper template accordingly.

# In[ ]:


template = "USER: {question}\nASSISTANT:"
prompt = PromptTemplate(template=template, input_variables=["question"])


# Load the model locally using IpexLLM using `IpexLLM.from_model_id`. It will load the model directly in its Huggingface format and convert it automatically to low-bit format for inference.

# In[ ]:


llm = IpexLLM.from_model_id(
    model_id="lmsys/vicuna-7b-v1.5",
    model_kwargs={"temperature": 0, "max_length": 64, "trust_remote_code": True},
)


# Use it in Chains:

# In[ ]:


llm_chain = prompt | llm

question = "What is AI?"
output = llm_chain.invoke(question)


# ### Save/Load Low-bit Model
# 
# Alternatively, you might save the low-bit model to disk once and use `from_model_id_low_bit` instead of `from_model_id` to reload it for later use - even across different machines. It is space-efficient, as the low-bit model demands significantly less disk space than the original model. And `from_model_id_low_bit` is also more efficient than `from_model_id` in terms of speed and memory usage, as it skips the model conversion step.
# 
# To save the low-bit model, use `save_low_bit` as follows:

# In[ ]:


saved_lowbit_model_path = "./vicuna-7b-1.5-low-bit"  # path to save low-bit model
llm.model.save_low_bit(saved_lowbit_model_path)
del llm


# Load the model from saved lowbit model path as follows.
# 
# > Note that the saved path for the low-bit model only includes the model itself but not the tokenizers. If you wish to have everything in one place, you will need to manually download or copy the tokenizer files from the original model's directory to the location where the low-bit model is saved.

# In[ ]:


llm_lowbit = IpexLLM.from_model_id_low_bit(
    model_id=saved_lowbit_model_path,
    tokenizer_id="lmsys/vicuna-7b-v1.5",
    # tokenizer_name=saved_lowbit_model_path,  # copy the tokenizers to saved path if you want to use it this way
    model_kwargs={"temperature": 0, "max_length": 64, "trust_remote_code": True},
)


# Use the loaded model in Chains:

# In[ ]:


llm_chain = prompt | llm_lowbit


question = "What is AI?"
output = llm_chain.invoke(question)

