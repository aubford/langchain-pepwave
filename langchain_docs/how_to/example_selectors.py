#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 1
---
# # How to use example selectors
# 
# If you have a large number of examples, you may need to select which ones to include in the prompt. The [Example Selector](/docs/concepts/example_selectors/) is the class responsible for doing so.
# 
# The base interface is defined as below:
# 
# ```python
# class BaseExampleSelector(ABC):
#     """Interface for selecting examples to include in prompts."""
# 
#     @abstractmethod
#     def select_examples(self, input_variables: Dict[str, str]) -> List[dict]:
#         """Select which examples to use based on the inputs."""
#         
#     @abstractmethod
#     def add_example(self, example: Dict[str, str]) -> Any:
#         """Add new example to store."""
# ```
# 
# The only method it needs to define is a ``select_examples`` method. This takes in the input variables and then returns a list of examples. It is up to each specific implementation as to how those examples are selected.
# 
# LangChain has a few different types of example selectors. For an overview of all these types, see the [below table](#example-selector-types).
# 
# In this guide, we will walk through creating a custom example selector.

# ## Examples
# 
# In order to use an example selector, we need to create a list of examples. These should generally be example inputs and outputs. For this demo purpose, let's imagine we are selecting examples of how to translate English to Italian.

# In[36]:


examples = [
    {"input": "hi", "output": "ciao"},
    {"input": "bye", "output": "arrivederci"},
    {"input": "soccer", "output": "calcio"},
]


# ## Custom Example Selector
# 
# Let's write an example selector that chooses what example to pick based on the length of the word.

# In[37]:


from langchain_core.example_selectors.base import BaseExampleSelector


class CustomExampleSelector(BaseExampleSelector):
    def __init__(self, examples):
        self.examples = examples

    def add_example(self, example):
        self.examples.append(example)

    def select_examples(self, input_variables):
        # This assumes knowledge that part of the input will be a 'text' key
        new_word = input_variables["input"]
        new_word_length = len(new_word)

        # Initialize variables to store the best match and its length difference
        best_match = None
        smallest_diff = float("inf")

        # Iterate through each example
        for example in self.examples:
            # Calculate the length difference with the first word of the example
            current_diff = abs(len(example["input"]) - new_word_length)

            # Update the best match if the current one is closer in length
            if current_diff < smallest_diff:
                smallest_diff = current_diff
                best_match = example

        return [best_match]


# In[38]:


example_selector = CustomExampleSelector(examples)


# In[39]:


example_selector.select_examples({"input": "okay"})


# In[40]:


example_selector.add_example({"input": "hand", "output": "mano"})


# In[41]:


example_selector.select_examples({"input": "okay"})


# ## Use in a Prompt
# 
# We can now use this example selector in a prompt

# In[42]:


from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

example_prompt = PromptTemplate.from_template("Input: {input} -> Output: {output}")


# In[43]:


prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    suffix="Input: {input} -> Output:",
    prefix="Translate the following words from English to Italian:",
    input_variables=["input"],
)

print(prompt.format(input="word"))


# ## Example Selector Types
# 
# | Name       | Description                                                                                 |
# |------------|---------------------------------------------------------------------------------------------|
# | Similarity | Uses semantic similarity between inputs and examples to decide which examples to choose.    |
# | MMR        | Uses Max Marginal Relevance between inputs and examples to decide which examples to choose. |
# | Length     | Selects examples based on how many can fit within a certain length                          |
# | Ngram      | Uses ngram overlap between inputs and examples to decide which examples to choose.          |

# In[ ]:




