#!/usr/bin/env python
# coding: utf-8

# # MLX Local Pipelines
# 
# MLX models can be run locally through the `MLXPipeline` class.
# 
# The [MLX Community](https://huggingface.co/mlx-community) hosts over 150 models, all open source and publicly available on Hugging Face Model Hub a online platform where people can easily collaborate and build ML together.
# 
# These can be called from LangChain either through this local pipeline wrapper or by calling their hosted inference endpoints through the MlXPipeline class. For more information on mlx, see the [examples repo](https://github.com/ml-explore/mlx-examples/tree/main/llms) notebook.

# To use, you should have the ``mlx-lm`` python [package installed](https://pypi.org/project/mlx-lm/), as well as [transformers](https://pypi.org/project/transformers/). You can also install `huggingface_hub`.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  mlx-lm transformers huggingface_hub')


# ### Model Loading
# 
# Models can be loaded by specifying the model parameters using the `from_model_id` method.

# In[ ]:


from langchain_community.llms.mlx_pipeline import MLXPipeline

pipe = MLXPipeline.from_model_id(
    "mlx-community/quantized-gemma-2b-it",
    pipeline_kwargs={"max_tokens": 10, "temp": 0.1},
)


# They can also be loaded by passing in an existing `transformers` pipeline directly

# In[ ]:


from mlx_lm import load

model, tokenizer = load("mlx-community/quantized-gemma-2b-it")
pipe = MLXPipeline(model=model, tokenizer=tokenizer)


# ### Create Chain
# 
# With the model loaded into memory, you can compose it with a prompt to
# form a chain.

# In[ ]:


from langchain_core.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | pipe

question = "What is electroencephalography?"

print(chain.invoke({"question": question}))

