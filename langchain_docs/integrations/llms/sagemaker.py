#!/usr/bin/env python
# coding: utf-8

# # SageMakerEndpoint
# 
# [Amazon SageMaker](https://aws.amazon.com/sagemaker/) is a system that can build, train, and deploy machine learning (ML) models for any use case with fully managed infrastructure, tools, and workflows.
# 
# This notebooks goes over how to use an LLM hosted on a `SageMaker endpoint`.

# In[ ]:


get_ipython().system('pip3 install langchain boto3')


# ## Set up

# You have to set up following required parameters of the `SagemakerEndpoint` call:
# - `endpoint_name`: The name of the endpoint from the deployed Sagemaker model.
#     Must be unique within an AWS Region.
# - `credentials_profile_name`: The name of the profile in the ~/.aws/credentials or ~/.aws/config files, which
#     has either access keys or role information specified.
#     If not specified, the default credential profile or, if on an EC2 instance,
#     credentials from IMDS will be used.
#     See: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

# ## Example

# In[2]:


from langchain_core.documents import Document


# In[3]:


example_doc_1 = """
Peter and Elizabeth took a taxi to attend the night party in the city. While in the party, Elizabeth collapsed and was rushed to the hospital.
Since she was diagnosed with a brain injury, the doctor told Peter to stay besides her until she gets well.
Therefore, Peter stayed with her at the hospital for 3 days without leaving.
"""

docs = [
    Document(
        page_content=example_doc_1,
    )
]


# ## Example to initialize with external boto3 session
# 
# ### for cross account scenarios

# In[ ]:


import json
from typing import Dict

import boto3
from langchain.chains.question_answering import load_qa_chain
from langchain_aws.llms import SagemakerEndpoint
from langchain_aws.llms.sagemaker_endpoint import LLMContentHandler
from langchain_core.prompts import PromptTemplate

query = """How long was Elizabeth hospitalized?
"""

prompt_template = """Use the following pieces of context to answer the question at the end.

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

roleARN = "arn:aws:iam::123456789:role/cross-account-role"
sts_client = boto3.client("sts")
response = sts_client.assume_role(
    RoleArn=roleARN, RoleSessionName="CrossAccountSession"
)

client = boto3.client(
    "sagemaker-runtime",
    region_name="us-west-2",
    aws_access_key_id=response["Credentials"]["AccessKeyId"],
    aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
    aws_session_token=response["Credentials"]["SessionToken"],
)


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]


content_handler = ContentHandler()

chain = load_qa_chain(
    llm=SagemakerEndpoint(
        endpoint_name="endpoint-name",
        client=client,
        model_kwargs={"temperature": 1e-10},
        content_handler=content_handler,
    ),
    prompt=PROMPT,
)

chain({"input_documents": docs, "question": query}, return_only_outputs=True)


# In[ ]:


import json
from typing import Dict

from langchain.chains.question_answering import load_qa_chain
from langchain_aws.llms import SagemakerEndpoint
from langchain_aws.llms.sagemaker_endpoint import LLMContentHandler
from langchain_core.prompts import PromptTemplate

query = """How long was Elizabeth hospitalized?
"""

prompt_template = """Use the following pieces of context to answer the question at the end.

{context}

Question: {question}
Answer:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]


content_handler = ContentHandler()

chain = load_qa_chain(
    llm=SagemakerEndpoint(
        endpoint_name="endpoint-name",
        credentials_profile_name="credentials-profile-name",
        region_name="us-west-2",
        model_kwargs={"temperature": 1e-10},
        content_handler=content_handler,
    ),
    prompt=PROMPT,
)

chain({"input_documents": docs, "question": query}, return_only_outputs=True)

