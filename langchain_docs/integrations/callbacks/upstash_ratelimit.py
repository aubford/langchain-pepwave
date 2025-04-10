#!/usr/bin/env python
# coding: utf-8

# # Upstash Ratelimit Callback
# 
# In this guide, we will go over how to add rate limiting based on number of requests or the number of tokens using `UpstashRatelimitHandler`. This handler uses [ratelimit library of Upstash](https://github.com/upstash/ratelimit-py/), which utilizes [Upstash Redis](https://upstash.com/docs/redis/overall/getstarted).
# 
# Upstash Ratelimit works by sending an HTTP request to Upstash Redis everytime the `limit` method is called. Remaining tokens/requests of the user are checked and updated. Based on the remaining tokens, we can stop the execution of costly operations like invoking an LLM or querying a vector store:
# 
# ```py
# response = ratelimit.limit()
# if response.allowed:
#     execute_costly_operation()
# ```
# 
# `UpstashRatelimitHandler` allows you to incorporate the ratelimit logic into your chain in a few minutes.
# 
# First, you will need to go to [the Upstash Console](https://console.upstash.com/login) and create a redis database ([see our docs](https://upstash.com/docs/redis/overall/getstarted)). After creating a database, you will need to set the environment variables:
# 
# ```
# UPSTASH_REDIS_REST_URL="****"
# UPSTASH_REDIS_REST_TOKEN="****"
# ```
# 
# Next, you will need to install Upstash Ratelimit and Redis library with:
# 
# ```
# pip install upstash-ratelimit upstash-redis
# ```
# 
# You are now ready to add rate limiting to your chain!
# 
# ## Ratelimiting Per Request
# 
# Let's imagine that we want to allow our users to invoke our chain 10 times per minute. Achieving this is as simple as:

# In[21]:


# set env variables
import os

os.environ["UPSTASH_REDIS_REST_URL"] = "****"
os.environ["UPSTASH_REDIS_REST_TOKEN"] = "****"

from langchain_community.callbacks import UpstashRatelimitError, UpstashRatelimitHandler
from langchain_core.runnables import RunnableLambda
from upstash_ratelimit import FixedWindow, Ratelimit
from upstash_redis import Redis

# create ratelimit
ratelimit = Ratelimit(
    redis=Redis.from_env(),
    # 10 requests per window, where window size is 60 seconds:
    limiter=FixedWindow(max_requests=10, window=60),
)

# create handler
user_id = "user_id"  # should be a method which gets the user id
handler = UpstashRatelimitHandler(identifier=user_id, request_ratelimit=ratelimit)

# create mock chain
chain = RunnableLambda(str)

# invoke chain with handler:
try:
    result = chain.invoke("Hello world!", config={"callbacks": [handler]})
except UpstashRatelimitError:
    print("Handling ratelimit.", UpstashRatelimitError)


# Note that we pass the handler to the `invoke` method instead of passing the handler when defining the chain.
# 
# For rate limiting algorithms other than `FixedWindow`, see [upstash-ratelimit docs](https://github.com/upstash/ratelimit-py?tab=readme-ov-file#ratelimiting-algorithms).
# 
# Before executing any steps in our pipeline, ratelimit will check whether the user has passed the request limit. If so, `UpstashRatelimitError` is raised.
# 
# ## Ratelimiting Per Token
# 
# Another option is to rate limit chain invokations based on:
# 1. number of tokens in prompt
# 2. number of tokens in prompt and LLM completion
# 
# This only works if you have an LLM in your chain. Another requirement is that the LLM you are using should return the token usage in it's `LLMOutput`.
# 
# ### How it works
# 
# The handler will get the remaining tokens before calling the LLM. If the remaining tokens is more than 0, LLM will be called. Otherwise `UpstashRatelimitError` will be raised.
# 
# After LLM is called, token usage information will be used to subtracted from the remaining tokens of the user. No error is raised at this stage of the chain.
# 
# ### Configuration
# 
# For the first configuration, simply initialize the handler like this:

# In[ ]:


ratelimit = Ratelimit(
    redis=Redis.from_env(),
    # 1000 tokens per window, where window size is 60 seconds:
    limiter=FixedWindow(max_requests=1000, window=60),
)

handler = UpstashRatelimitHandler(identifier=user_id, token_ratelimit=ratelimit)


# For the second configuration, here is how to initialize the handler:

# In[ ]:


ratelimit = Ratelimit(
    redis=Redis.from_env(),
    # 1000 tokens per window, where window size is 60 seconds:
    limiter=FixedWindow(max_requests=1000, window=60),
)

handler = UpstashRatelimitHandler(
    identifier=user_id,
    token_ratelimit=ratelimit,
    include_output_tokens=True,  # set to True
)


# You can also employ ratelimiting based on requests and tokens at the same time, simply by passing both `request_ratelimit` and `token_ratelimit` parameters.
# 
# Here is an example with a chain utilizing an LLM:

# In[22]:


# set env variables
import os

os.environ["UPSTASH_REDIS_REST_URL"] = "****"
os.environ["UPSTASH_REDIS_REST_TOKEN"] = "****"
os.environ["OPENAI_API_KEY"] = "****"

from langchain_community.callbacks import UpstashRatelimitError, UpstashRatelimitHandler
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from upstash_ratelimit import FixedWindow, Ratelimit
from upstash_redis import Redis

# create ratelimit
ratelimit = Ratelimit(
    redis=Redis.from_env(),
    # 500 tokens per window, where window size is 60 seconds:
    limiter=FixedWindow(max_requests=500, window=60),
)

# create handler
user_id = "user_id"  # should be a method which gets the user id
handler = UpstashRatelimitHandler(identifier=user_id, token_ratelimit=ratelimit)

# create mock chain
as_str = RunnableLambda(str)
model = ChatOpenAI()

chain = as_str | model

# invoke chain with handler:
try:
    result = chain.invoke("Hello world!", config={"callbacks": [handler]})
except UpstashRatelimitError:
    print("Handling ratelimit.", UpstashRatelimitError)

