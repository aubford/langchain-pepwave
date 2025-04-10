#!/usr/bin/env python
# coding: utf-8

# # Databricks
# 
# > [Databricks](https://www.databricks.com/) Lakehouse Platform unifies data, analytics, and AI on one platform.
# 
# 
# This notebook provides a quick overview for getting started with Databricks [LLM models](https://python.langchain.com/docs/concepts/text_llms). For detailed documentation of all features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/llms/langchain_community.llms.databricks.Databricks.html).
# 
# ## Overview
# 
# `Databricks` LLM class wraps a completion endpoint hosted as either of these two endpoint types:
# 
# * [Databricks Model Serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html), recommended for production and development,
# * Cluster driver proxy app, recommended for interactive development.
# 
# This example notebook shows how to wrap your LLM endpoint and use it as an LLM in your LangChain application.

# ## Limitations
# 
# The `Databricks` LLM class is *legacy* implementation and has several limitations in the feature compatibility.
# 
# * Only supports synchronous invocation. Streaming or async APIs are not supported.
# * `batch` API is not supported.
# 
# To use those features, please use the new [ChatDatabricks](https://python.langchain.com/docs/integrations/chat/databricks) class instead. `ChatDatabricks` supports all APIs of `ChatModel` including streaming, async, batch, etc.
# 

# ## Setup
# 
# To access Databricks models you'll need to create a Databricks account, set up credentials (only if you are outside Databricks workspace), and install required packages.
# 
# ### Credentials (only if you are outside Databricks)
# 
# If you are running LangChain app inside Databricks, you can skip this step.
# 
# Otherwise, you need manually set the Databricks workspace hostname and personal access token to `DATABRICKS_HOST` and `DATABRICKS_TOKEN` environment variables, respectively. See [Authentication Documentation](https://docs.databricks.com/en/dev-tools/auth/index.html#databricks-personal-access-tokens) for how to get an access token.

# In[ ]:


import getpass
import os

os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"
if "DATABRICKS_TOKEN" not in os.environ:
    os.environ["DATABRICKS_TOKEN"] = getpass.getpass(
        "Enter your Databricks access token: "
    )


# Alternatively, you can pass those parameters when initializing the `Databricks` class.

# In[ ]:


from langchain_community.llms import Databricks

databricks = Databricks(
    host="https://your-workspace.cloud.databricks.com",
    # We strongly recommend NOT to hardcode your access token in your code, instead use secret management tools
    # or environment variables to store your access token securely. The following example uses Databricks Secrets
    # to retrieve the access token that is available within the Databricks notebook.
    token=dbutils.secrets.get(scope="YOUR_SECRET_SCOPE", key="databricks-token"),  # noqa: F821
)


# ### Installation
# 
# The LangChain Databricks integration lives in the `langchain-community` package. Also, `mlflow >= 2.9 ` is required to run the code in this notebook.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community mlflow>=2.9.0')


# ## Wrapping Model Serving Endpoint
# 
# ### Prerequisites:
# 
# * An LLM was registered and deployed to [a Databricks serving endpoint](https://docs.databricks.com/machine-learning/model-serving/index.html).
# * You have ["Can Query" permission](https://docs.databricks.com/security/auth-authz/access-control/serving-endpoint-acl.html) to the endpoint.
# 
# The expected MLflow model signature is:
# 
#   * inputs: `[{"name": "prompt", "type": "string"}, {"name": "stop", "type": "list[string]"}]`
#   * outputs: `[{"type": "string"}]`
# 

# ### Invocation

# In[ ]:


from langchain_community.llms import Databricks

llm = Databricks(endpoint_name="YOUR_ENDPOINT_NAME")
llm.invoke("How are you?")


# In[ ]:


llm.invoke("How are you?", stop=["."])


# ### Transform Input and Output
# 
# Sometimes you may want to wrap a serving endpoint that has imcompatible model signature or you want to insert extra configs. You can use the `transform_input_fn` and `transform_output_fn` arguments to define additional pre/post process.

# In[ ]:


# Use `transform_input_fn` and `transform_output_fn` if the serving endpoint
# expects a different input schema and does not return a JSON string,
# respectively, or you want to apply a prompt template on top.


def transform_input(**request):
    full_prompt = f"""{request["prompt"]}
    Be Concise.
    """
    request["prompt"] = full_prompt
    return request


def transform_output(response):
    return response.upper()


llm = Databricks(
    endpoint_name="YOUR_ENDPOINT_NAME",
    transform_input_fn=transform_input,
    transform_output_fn=transform_output,
)

llm.invoke("How are you?")

