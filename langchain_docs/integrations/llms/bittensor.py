#!/usr/bin/env python
# coding: utf-8

# # Bittensor
# 
# >[Bittensor](https://bittensor.com/) is a mining network, similar to Bitcoin, that includes built-in incentives designed to encourage miners to contribute compute + knowledge.
# >
# >`NIBittensorLLM` is developed by [Neural Internet](https://neuralinternet.ai/), powered by `Bittensor`.
# 
# >This LLM showcases true potential of decentralized AI by giving you the best response(s) from the `Bittensor protocol`, which consist of various AI models such as `OpenAI`, `LLaMA2` etc.
# 
# Users can view their logs, requests, and API keys on the [Validator Endpoint Frontend](https://api.neuralinternet.ai/). However, changes to the configuration are currently prohibited; otherwise, the user's queries will be blocked.
# 
# If you encounter any difficulties or have any questions, please feel free to reach out to our developer on [GitHub](https://github.com/Kunj-2206), [Discord](https://discordapp.com/users/683542109248159777) or join our discord server for latest update and queries [Neural Internet](https://discord.gg/neuralinternet).
# 

# ## Different Parameter and response handling for NIBittensorLLM 

# In[ ]:


import json
from pprint import pprint

from langchain.globals import set_debug
from langchain_community.llms import NIBittensorLLM

set_debug(True)

# System parameter in NIBittensorLLM is optional but you can set whatever you want to perform with model
llm_sys = NIBittensorLLM(
    system_prompt="Your task is to determine response based on user prompt.Explain me like I am technical lead of a project"
)
sys_resp = llm_sys(
    "What is bittensor and What are the potential benefits of decentralized AI?"
)
print(f"Response provided by LLM with system prompt set is : {sys_resp}")

# The top_responses parameter can give multiple responses based on its parameter value
# This below code retrieve top 10 miner's response all the response are in format of json

# Json response structure is
""" {
    "choices":  [
                    {"index": Bittensor's Metagraph index number,
                    "uid": Unique Identifier of a miner,
                    "responder_hotkey": Hotkey of a miner,
                    "message":{"role":"assistant","content": Contains actual response},
                    "response_ms": Time in millisecond required to fetch response from a miner} 
                ]
    } """

multi_response_llm = NIBittensorLLM(top_responses=10)
multi_resp = multi_response_llm.invoke("What is Neural Network Feeding Mechanism?")
json_multi_resp = json.loads(multi_resp)
pprint(json_multi_resp)


# ##  Using NIBittensorLLM with LLMChain and PromptTemplate

# In[ ]:


from langchain.chains import LLMChain
from langchain.globals import set_debug
from langchain_community.llms import NIBittensorLLM
from langchain_core.prompts import PromptTemplate

set_debug(True)

template = """Question: {question}

Answer: Let's think step by step."""


prompt = PromptTemplate.from_template(template)

# System parameter in NIBittensorLLM is optional but you can set whatever you want to perform with model
llm = NIBittensorLLM(
    system_prompt="Your task is to determine response based on user prompt."
)

llm_chain = LLMChain(prompt=prompt, llm=llm)
question = "What is bittensor?"

llm_chain.run(question)


# ##  Using NIBittensorLLM with Conversational Agent and Google Search Tool

# In[ ]:


from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

search = GoogleSearchAPIWrapper()

tool = Tool(
    name="Google Search",
    description="Search Google for recent results.",
    func=search.run,
)


# In[ ]:


from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import NIBittensorLLM

tools = [tool]

prompt = hub.pull("hwchase17/react")


llm = NIBittensorLLM(
    system_prompt="Your task is to determine a response based on user prompt"
)

memory = ConversationBufferMemory(memory_key="chat_history")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)

response = agent_executor.invoke({"input": prompt})

