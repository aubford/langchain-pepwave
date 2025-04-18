#!/usr/bin/env python
# coding: utf-8

# # Passio NutritionAI
# 
# To best understand how NutritionAI can give your agents super food-nutrition powers, let's build an agent that can find that information via Passio NutritionAI.
# 
# ## Define tools
# 
# We first need to create [the Passio NutritionAI tool](/docs/integrations/tools/passio_nutrition_ai).

# ### [Passio Nutrition AI](/docs/integrations/tools/passio_nutrition_ai)
# 
# We have a built-in tool in LangChain to easily use Passio NutritionAI to find food nutrition facts.
# Note that this requires an API key - they have a free tier.
# 
# Once you create your API key, you will need to export that as:
# 
# ```bash
# export NUTRITIONAI_SUBSCRIPTION_KEY="..."
# ```
# 
# ... or provide it to your Python environment via some other means such as the `dotenv` package.  You an also explicitly control the key via constructor calls.

# In[10]:


from dotenv import load_dotenv
from langchain_core.utils import get_from_env

load_dotenv()

nutritionai_subscription_key = get_from_env(
    "nutritionai_subscription_key", "NUTRITIONAI_SUBSCRIPTION_KEY"
)


# In[11]:


from langchain_community.tools.passio_nutrition_ai import NutritionAI
from langchain_community.utilities.passio_nutrition_ai import NutritionAIAPI


# In[12]:


nutritionai_search = NutritionAI(api_wrapper=NutritionAIAPI())


# In[ ]:


nutritionai_search.invoke("chicken tikka masala")


# In[ ]:


nutritionai_search.invoke("Schnuck Markets sliced pepper jack cheese")


# ### Tools
# 
# Now that we have the tool, we can create a list of tools that we will use downstream.

# In[15]:


tools = [nutritionai_search]


# ## Create the agent
# 
# Now that we have defined the tools, we can create the agent. We will be using an OpenAI Functions agent - for more information on this type of agent, as well as other options, see [this guide](/docs/concepts/agents)
# 
# First, we choose the LLM we want to be guiding the agent.

# In[16]:


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


# Next, we choose the prompt we want to use to guide the agent.

# In[17]:


from langchain import hub

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages


# Now, we can initialize the agent with the LLM, the prompt, and the tools. The agent is responsible for taking in input and deciding what actions to take. Crucially, the Agent does not execute those actions - that is done by the AgentExecutor (next step). For more information about how to think about these components, see our [conceptual guide](/docs/concepts/agents)

# In[18]:


from langchain.agents import create_openai_functions_agent

agent = create_openai_functions_agent(llm, tools, prompt)


# Finally, we combine the agent (the brains) with the tools inside the AgentExecutor (which will repeatedly call the agent and execute tools). For more information about how to think about these components, see our [conceptual guide](/docs/concepts/agents)

# In[19]:


from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# ## Run the agent
# 
# We can now run the agent on a few queries! Note that for now, these are all **stateless** queries (it won't remember previous interactions).

# In[20]:


agent_executor.invoke({"input": "hi!"})


# In[ ]:


agent_executor.invoke({"input": "how many calories are in a slice pepperoni pizza?"})


# If we want to keep track of these messages automatically, we can wrap this in a RunnableWithMessageHistory. For more information on how to use this, see [this guide](/docs/how_to/message_history)

# In[ ]:


agent_executor.invoke(
    {"input": "I had bacon and eggs for breakfast.  How many calories is that?"}
)


# In[ ]:


agent_executor.invoke(
    {
        "input": "I had sliced pepper jack cheese for a snack.  How much protein did I have?"
    }
)


# In[ ]:


agent_executor.invoke(
    {
        "input": "I had sliced colby cheese for a snack. Give me calories for this Schnuck Markets product."
    }
)


# In[ ]:


agent_executor.invoke(
    {
        "input": "I had chicken tikka masala for dinner.  how much calories, protein, and fat did I have with default quantity?"
    }
)


# ## Conclusion
# 
# That's a wrap! In this quick start we covered how to create a simple agent that is able to incorporate food-nutrition information into its answers. Agents are a complex topic, and there's lot to learn!

# 
