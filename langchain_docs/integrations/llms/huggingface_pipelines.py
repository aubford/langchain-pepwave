#!/usr/bin/env python
# coding: utf-8

# # Hugging Face Local Pipelines
# 
# Hugging Face models can be run locally through the `HuggingFacePipeline` class.
# 
# The [Hugging Face Model Hub](https://huggingface.co/models) hosts over 120k models, 20k datasets, and 50k demo apps (Spaces), all open source and publicly available, in an online platform where people can easily collaborate and build ML together.
# 
# These can be called from LangChain either through this local pipeline wrapper or by calling their hosted inference endpoints through the HuggingFaceHub class.

# To use, you should have the ``transformers`` python [package installed](https://pypi.org/project/transformers/), as well as [pytorch](https://pytorch.org/get-started/locally/). You can also install `xformer` for a more memory-efficient attention implementation.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet transformers')


# ### Model Loading
# 
# Models can be loaded by specifying the model parameters using the `from_model_id` method.

# In[ ]:


from langchain_huggingface.llms import HuggingFacePipeline

hf = HuggingFacePipeline.from_model_id(
    model_id="gpt2",
    task="text-generation",
    pipeline_kwargs={"max_new_tokens": 10},
)


# They can also be loaded by passing in an existing `transformers` pipeline directly

# In[ ]:


from langchain_huggingface.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_id = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=10)
hf = HuggingFacePipeline(pipeline=pipe)


# ### Create Chain
# 
# With the model loaded into memory, you can compose it with a prompt to
# form a chain.

# In[ ]:


from langchain_core.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | hf

question = "What is electroencephalography?"

print(chain.invoke({"question": question}))


# To get response without prompt, you can bind `skip_prompt=True` with LLM.

# In[ ]:


chain = prompt | hf.bind(skip_prompt=True)

question = "What is electroencephalography?"

print(chain.invoke({"question": question}))


# Streaming repsonse.

# In[ ]:


for chunk in chain.stream(question):
    print(chunk, end="", flush=True)


# ### GPU Inference
# 
# When running on a machine with GPU, you can specify the `device=n` parameter to put the model on the specified device.
# Defaults to `-1` for CPU inference.
# 
# If you have multiple-GPUs and/or the model is too large for a single GPU, you can specify `device_map="auto"`, which requires and uses the [Accelerate](https://huggingface.co/docs/accelerate/index) library to automatically determine how to load the model weights. 
# 
# *Note*: both `device` and `device_map` should not be specified together and can lead to unexpected behavior.

# In[ ]:


gpu_llm = HuggingFacePipeline.from_model_id(
    model_id="gpt2",
    task="text-generation",
    device=0,  # replace with device_map="auto" to use the accelerate library.
    pipeline_kwargs={"max_new_tokens": 10},
)

gpu_chain = prompt | gpu_llm

question = "What is electroencephalography?"

print(gpu_chain.invoke({"question": question}))


# ### Batch GPU Inference
# 
# If running on a device with GPU, you can also run inference on the GPU in batch mode.

# In[ ]:


gpu_llm = HuggingFacePipeline.from_model_id(
    model_id="bigscience/bloom-1b7",
    task="text-generation",
    device=0,  # -1 for CPU
    batch_size=2,  # adjust as needed based on GPU map and model size.
    model_kwargs={"temperature": 0, "max_length": 64},
)

gpu_chain = prompt | gpu_llm.bind(stop=["\n\n"])

questions = []
for i in range(4):
    questions.append({"question": f"What is the number {i} in french?"})

answers = gpu_chain.batch(questions)
for answer in answers:
    print(answer)


# ### Inference with OpenVINO backend
# 
# To deploy a model with OpenVINO, you can specify the `backend="openvino"` parameter to trigger OpenVINO as backend inference framework.
# 
# If you have an Intel GPU, you can specify `model_kwargs={"device": "GPU"}` to run inference on it.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade-strategy eager "optimum[openvino,nncf]" --quiet')


# In[ ]:


ov_config = {"PERFORMANCE_HINT": "LATENCY", "NUM_STREAMS": "1", "CACHE_DIR": ""}

ov_llm = HuggingFacePipeline.from_model_id(
    model_id="gpt2",
    task="text-generation",
    backend="openvino",
    model_kwargs={"device": "CPU", "ov_config": ov_config},
    pipeline_kwargs={"max_new_tokens": 10},
)

ov_chain = prompt | ov_llm

question = "What is electroencephalography?"

print(ov_chain.invoke({"question": question}))


# ### Inference with local OpenVINO model
# 
# It is possible to [export your model](https://github.com/huggingface/optimum-intel?tab=readme-ov-file#export) to the OpenVINO IR format with the CLI, and load the model from local folder.
# 

# In[ ]:


get_ipython().system('optimum-cli export openvino --model gpt2 ov_model_dir')


# It is recommended to apply 8 or 4-bit weight quantization to reduce inference latency and model footprint using `--weight-format`:

# In[ ]:


get_ipython().system('optimum-cli export openvino --model gpt2  --weight-format int8 ov_model_dir # for 8-bit quantization')

get_ipython().system('optimum-cli export openvino --model gpt2  --weight-format int4 ov_model_dir # for 4-bit quantization')


# In[ ]:


ov_llm = HuggingFacePipeline.from_model_id(
    model_id="ov_model_dir",
    task="text-generation",
    backend="openvino",
    model_kwargs={"device": "CPU", "ov_config": ov_config},
    pipeline_kwargs={"max_new_tokens": 10},
)

ov_chain = prompt | ov_llm

question = "What is electroencephalography?"

print(ov_chain.invoke({"question": question}))


# You can get additional inference speed improvement with Dynamic Quantization of activations and KV-cache quantization. These options can be enabled with `ov_config` as follows:

# In[ ]:


ov_config = {
    "KV_CACHE_PRECISION": "u8",
    "DYNAMIC_QUANTIZATION_GROUP_SIZE": "32",
    "PERFORMANCE_HINT": "LATENCY",
    "NUM_STREAMS": "1",
    "CACHE_DIR": "",
}


# For more information refer to [OpenVINO LLM guide](https://docs.openvino.ai/2024/learn-openvino/llm_inference_guide.html) and [OpenVINO Local Pipelines notebook](/docs/integrations/llms/openvino/).
