#!/usr/bin/env python
# coding: utf-8

# # Intel Weight-Only Quantization
# ## Weight-Only Quantization for Huggingface Models with Intel Extension for Transformers Pipelines
# 
# Hugging Face models can be run locally with Weight-Only quantization through the `WeightOnlyQuantPipeline` class.
# 
# The [Hugging Face Model Hub](https://huggingface.co/models) hosts over 120k models, 20k datasets, and 50k demo apps (Spaces), all open source and publicly available, in an online platform where people can easily collaborate and build ML together.
# 
# These can be called from LangChain through this local pipeline wrapper class.

# To use, you should have the ``transformers`` python [package installed](https://pypi.org/project/transformers/), as well as [pytorch](https://pytorch.org/get-started/locally/), [intel-extension-for-transformers](https://github.com/intel/intel-extension-for-transformers).

# In[ ]:


get_ipython().run_line_magic('pip', 'install transformers --quiet')
get_ipython().run_line_magic('pip', 'install intel-extension-for-transformers')


# ### Model Loading
# 
# Models can be loaded by specifying the model parameters using the `from_model_id` method. The model parameters include `WeightOnlyQuantConfig` class in intel_extension_for_transformers.

# In[ ]:


from intel_extension_for_transformers.transformers import WeightOnlyQuantConfig
from langchain_community.llms.weight_only_quantization import WeightOnlyQuantPipeline

conf = WeightOnlyQuantConfig(weight_dtype="nf4")
hf = WeightOnlyQuantPipeline.from_model_id(
    model_id="google/flan-t5-large",
    task="text2text-generation",
    quantization_config=conf,
    pipeline_kwargs={"max_new_tokens": 10},
)


# They can also be loaded by passing in an existing `transformers` pipeline directly

# In[ ]:


from intel_extension_for_transformers.transformers import AutoModelForSeq2SeqLM
from transformers import AutoTokenizer, pipeline

model_id = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
pipe = pipeline(
    "text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=10
)
hf = WeightOnlyQuantPipeline(pipeline=pipe)


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


# ### CPU Inference
# 
# Now intel-extension-for-transformers only support CPU device inference. Will support intel GPU soon.When running on a machine with CPU, you can specify the `device="cpu"` or `device=-1` parameter to put the model on CPU device.
# Defaults to `-1` for CPU inference.

# In[ ]:


conf = WeightOnlyQuantConfig(weight_dtype="nf4")
llm = WeightOnlyQuantPipeline.from_model_id(
    model_id="google/flan-t5-large",
    task="text2text-generation",
    quantization_config=conf,
    pipeline_kwargs={"max_new_tokens": 10},
)

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | llm

question = "What is electroencephalography?"

print(chain.invoke({"question": question}))


# ### Batch CPU Inference
# 
# You can also run inference on the CPU in batch mode.

# In[ ]:


conf = WeightOnlyQuantConfig(weight_dtype="nf4")
llm = WeightOnlyQuantPipeline.from_model_id(
    model_id="google/flan-t5-large",
    task="text2text-generation",
    quantization_config=conf,
    pipeline_kwargs={"max_new_tokens": 10},
)

chain = prompt | llm.bind(stop=["\n\n"])

questions = []
for i in range(4):
    questions.append({"question": f"What is the number {i} in french?"})

answers = chain.batch(questions)
for answer in answers:
    print(answer)


# ### Data Types Supported by Intel-extension-for-transformers
# 
# We support quantize the weights to following data types for storing(weight_dtype in WeightOnlyQuantConfig):
# 
# * **int8**: Uses 8-bit data type.
# * **int4_fullrange**: Uses the -8 value of int4 range compared with the normal int4 range [-7,7].
# * **int4_clip**: Clips and retains the values within the int4 range, setting others to zero.
# * **nf4**: Uses the normalized float 4-bit data type.
# * **fp4_e2m1**: Uses regular float 4-bit data type. "e2" means that 2 bits are used for the exponent, and "m1" means that 1 bits are used for the mantissa.
# 
# While these techniques store weights in 4 or 8 bit, the computation still happens in float32, bfloat16 or int8(compute_dtype in WeightOnlyQuantConfig):
# * **fp32**: Uses the float32 data type to compute.
# * **bf16**: Uses the bfloat16 data type to compute.
# * **int8**: Uses 8-bit data type to compute.
# 
# ### Supported Algorithms Matrix
# 
# Quantization algorithms supported in intel-extension-for-transformers(algorithm in WeightOnlyQuantConfig):
# 
# | Algorithms |   PyTorch  |    LLM Runtime    |
# |:--------------:|:----------:|:----------:|
# |       RTN      |  &#10004;  |  &#10004;  |
# |       AWQ      |  &#10004;  | stay tuned |
# |      TEQ      | &#10004; | stay tuned |
# > **RTN:** A quantification method that we can think of very intuitively. It does not require additional datasets and is a very fast quantization method. Generally speaking, RTN will convert the weight into a uniformly distributed integer data type, but some algorithms, such as Qlora, propose a non-uniform NF4 data type and prove its theoretical optimality.
# 
# > **AWQ:** Proved that protecting only 1% of salient weights can greatly reduce quantization error. the salient weight channels are selected by observing the distribution of activation and weight per channel. The salient weights are also quantized after multiplying a big scale factor before quantization for preserving.
# 
# > **TEQ:** A trainable equivalent transformation that preserves the FP32 precision in weight-only quantization. It is inspired by AWQ while providing a new solution to search for the optimal per-channel scaling factor between activations and weights.
# 
