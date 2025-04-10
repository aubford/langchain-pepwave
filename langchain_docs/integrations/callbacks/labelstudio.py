#!/usr/bin/env python
# coding: utf-8

# # Label Studio
# 
# 
# >[Label Studio](https://labelstud.io/guide/get_started) is an open-source data labeling platform that provides LangChain with flexibility when it comes to labeling data for fine-tuning large language models (LLMs). It also enables the preparation of custom training data and the collection and evaluation of responses through human feedback.
# 
# In this guide, you will learn how to connect a LangChain pipeline to `Label Studio` to:
# 
# - Aggregate all input prompts, conversations, and responses in a single `Label Studio` project. This consolidates all the data in one place for easier labeling and analysis.
# - Refine prompts and responses to create a dataset for supervised fine-tuning (SFT) and reinforcement learning with human feedback (RLHF) scenarios. The labeled data can be used to further train the LLM to improve its performance.
# - Evaluate model responses through human feedback. `Label Studio` provides an interface for humans to review and provide feedback on model responses, allowing evaluation and iteration.

# ## Installation and setup

# First install latest versions of Label Studio and Label Studio API client:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain label-studio label-studio-sdk langchain-openai langchain-community')


# Next, run `label-studio` on the command line to start the local LabelStudio instance at `http://localhost:8080`. See the [Label Studio installation guide](https://labelstud.io/guide/install) for more options.

# You'll need a token to make API calls.
# 
# Open your LabelStudio instance in your browser, go to `Account & Settings > Access Token` and copy the key.
# 
# Set environment variables with your LabelStudio URL, API key and OpenAI API key:

# In[ ]:


import os

os.environ["LABEL_STUDIO_URL"] = "<YOUR-LABEL-STUDIO-URL>"  # e.g. http://localhost:8080
os.environ["LABEL_STUDIO_API_KEY"] = "<YOUR-LABEL-STUDIO-API-KEY>"
os.environ["OPENAI_API_KEY"] = "<YOUR-OPENAI-API-KEY>"


# ## Collecting LLMs prompts and responses

# The data used for labeling is stored in projects within Label Studio. Every project is identified by an XML configuration that details the specifications for input and output data. 
# 
# Create a project that takes human input in text format and outputs an editable LLM response in a text area:
# 
# ```xml
# <View>
# <Style>
#     .prompt-box {
#         background-color: white;
#         border-radius: 10px;
#         box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
#         padding: 20px;
#     }
# </Style>
# <View className="root">
#     <View className="prompt-box">
#         <Text name="prompt" value="$prompt"/>
#     </View>
#     <TextArea name="response" toName="prompt"
#               maxSubmissions="1" editable="true"
#               required="true"/>
# </View>
# <Header value="Rate the response:"/>
# <Rating name="rating" toName="prompt"/>
# </View>
# ```
# 
# 1. To create a project in Label Studio, click on the "Create" button. 
# 2. Enter a name for your project in the "Project Name" field, such as `My Project`.
# 3. Navigate to `Labeling Setup > Custom Template` and paste the XML configuration provided above.

# You can collect input LLM prompts and output responses in a LabelStudio project, connecting it via `LabelStudioCallbackHandler`:

# In[1]:


from langchain_community.callbacks.labelstudio_callback import (
    LabelStudioCallbackHandler,
)


# In[ ]:


from langchain_openai import OpenAI

llm = OpenAI(
    temperature=0, callbacks=[LabelStudioCallbackHandler(project_name="My Project")]
)
print(llm.invoke("Tell me a joke"))


# In the Label Studio, open `My Project`. You will see the prompts, responses, and metadata like the model name. 

# ## Collecting Chat model Dialogues

# You can also track and display full chat dialogues in LabelStudio, with the ability to rate and modify the last response:
# 
# 1. Open Label Studio and click on the "Create" button.
# 2. Enter a name for your project in the "Project Name" field, such as `New Project with Chat`.
# 3. Navigate to Labeling Setup > Custom Template and paste the following XML configuration:
# 
# ```xml
# <View>
# <View className="root">
#      <Paragraphs name="dialogue"
#                value="$prompt"
#                layout="dialogue"
#                textKey="content"
#                nameKey="role"
#                granularity="sentence"/>
#   <Header value="Final response:"/>
#     <TextArea name="response" toName="dialogue"
#               maxSubmissions="1" editable="true"
#               required="true"/>
# </View>
# <Header value="Rate the response:"/>
# <Rating name="rating" toName="dialogue"/>
# </View>
# ```

# In[ ]:


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

chat_llm = ChatOpenAI(
    callbacks=[
        LabelStudioCallbackHandler(
            mode="chat",
            project_name="New Project with Chat",
        )
    ]
)
llm_results = chat_llm.invoke(
    [
        SystemMessage(content="Always use a lot of emojis"),
        HumanMessage(content="Tell me a joke"),
    ]
)


# In Label Studio, open "New Project with Chat". Click on a created task to view dialog history and edit/annotate responses.

# ## Custom Labeling Configuration

# You can modify the default labeling configuration in LabelStudio to add more target labels like response sentiment, relevance, and many [other types annotator's feedback](https://labelstud.io/tags/).
# 
# New labeling configuration can be added from UI: go to `Settings > Labeling Interface` and set up a custom configuration with additional tags like `Choices` for sentiment or `Rating` for relevance. Keep in mind that [`TextArea` tag](https://labelstud.io/tags/textarea) should be presented in any configuration to display the LLM responses.
# 
# Alternatively, you can specify the labeling configuration on the initial call before project creation:

# In[ ]:


ls = LabelStudioCallbackHandler(
    project_config="""
<View>
<Text name="prompt" value="$prompt"/>
<TextArea name="response" toName="prompt"/>
<TextArea name="user_feedback" toName="prompt"/>
<Rating name="rating" toName="prompt"/>
<Choices name="sentiment" toName="prompt">
    <Choice value="Positive"/>
    <Choice value="Negative"/>
</Choices>
</View>
"""
)


# Note that if the project doesn't exist, it will be created with the specified labeling configuration.

# ## Other parameters

# The `LabelStudioCallbackHandler` accepts several optional parameters:
# 
# - **api_key** - Label Studio API key. Overrides environmental variable `LABEL_STUDIO_API_KEY`.
# - **url** - Label Studio URL. Overrides `LABEL_STUDIO_URL`, default `http://localhost:8080`.
# - **project_id** - Existing Label Studio project ID. Overrides `LABEL_STUDIO_PROJECT_ID`. Stores data in this project.
# - **project_name** - Project name if project ID not specified. Creates a new project. Default is `"LangChain-%Y-%m-%d"` formatted with the current date.
# - **project_config** - [custom labeling configuration](#custom-labeling-configuration)
# - **mode**: use this shortcut to create target configuration from scratch:
#    - `"prompt"` - Single prompt, single response. Default.
#    - `"chat"` - Multi-turn chat mode.
# 
# 
