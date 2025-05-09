#!/usr/bin/env python
# coding: utf-8

# ---
# sidebar_label: OpenGradient
# ---

# # OpenGradient
# [OpenGradient](https://www.opengradient.ai/) is a decentralized AI computing network enabling globally accessible, permissionless, and verifiable ML model inference.
# 
# The OpenGradient langchain package currently offers a toolkit that allows developers to build their own custom ML inference tools for models on the OpenGradient network. This was previously a challenge because of the context-window polluting nature of large model parameters -- imagine having to give your agent a 200x200 array of floating-point data!
# 
# The toolkit solves this problem by encapsulating all data processing logic within the tool definition itself. This approach keeps the agent's context window clean while giving developers complete flexibility to implement custom data processing and live-data retrieval for their ML models.

# ## Installation and Setup
# Ensure that you have an OpenGradient API key in order to access the OpenGradient network. If you already have an API key, simply set the environment variable:

# In[ ]:


get_ipython().system('export OPENGRADIENT_PRIVATE_KEY="your-api-key"')


# If you need to set up a new API key, download the opengradient SDK and follow the instructions to initialize a new configuration.

# In[ ]:


get_ipython().system('pip install opengradient')
get_ipython().system('opengradient config init')


# Once you have set up your API key, install the langchain-opengradient package.

# In[ ]:


pip install -U langchain-opengradient


# ## OpenGradient Toolkit
# The OpenGradientToolkit empowers developers to create specialized tools based on [ML models](https://hub.opengradient.ai/models) and [workflows](https://docs.opengradient.ai/developers/sdk/ml_workflows.html) deployed on the OpenGradient decentralized network. This integration enables LangChain agents to access powerful ML capabilities while maintaining efficient context usage.
# 
# ### Key Benefits
# * 🔄 Real-time data integration - Process live data feeds within your tools
# 
# * 🎯 Dynamic processing - Custom data pipelines that adapt to specific agent inputs
# 
# * 🧠 Context efficiency - Handle complex ML operations without flooding your context window
# 
# * 🔌 Seamless deployment - Easy integration with models already on the OpenGradient network
# 
# * 🔧 Full customization - Create and deploy your own specific models through the [OpenGradient SDK](https://docs.opengradient.ai/developers/sdk/model_management.html), then build custom tools from them
# 
# * 🔐 Verifiable inference - All inferences run on the decentralized OpenGradient network, allowing users to choose various flavors of security such as ZKML and TEE for trustless, verifiable model execution
# 
# For detailed examples and implementation guides, check out our [comprehensive tutorial](/docs/integrations/tools/opengradient_toolkit.ipynb).
