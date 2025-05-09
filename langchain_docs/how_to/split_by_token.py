#!/usr/bin/env python
# coding: utf-8

# # How to split text by tokens 
# 
# Language models have a [token](/docs/concepts/tokens/) limit. You should not exceed the token limit. When you [split your text](/docs/concepts/text_splitters/) into chunks it is therefore a good idea to count the number of tokens. There are many tokenizers. When you count tokens in your text you should use the same tokenizer as used in the language model. 

# ## tiktoken
# 
# :::note
# [tiktoken](https://github.com/openai/tiktoken) is a fast `BPE` tokenizer created by `OpenAI`.
# :::
# 
# 
# We can use `tiktoken` to estimate tokens used. It will probably be more accurate for the OpenAI models.
# 
# 1. How the text is split: by character passed in.
# 2. How the chunk size is measured: by `tiktoken` tokenizer.
# 
# [CharacterTextSplitter](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.CharacterTextSplitter.html), [RecursiveCharacterTextSplitter](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html), and [TokenTextSplitter](https://python.langchain.com/api_reference/text_splitters/base/langchain_text_splitters.base.TokenTextSplitter.html) can be used with `tiktoken` directly.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-text-splitters tiktoken')


# In[1]:


from langchain_text_splitters import CharacterTextSplitter

# This is a long document we can split up.
with open("state_of_the_union.txt") as f:
    state_of_the_union = f.read()


# To split with a [CharacterTextSplitter](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.CharacterTextSplitter.html) and then merge chunks with `tiktoken`, use its `.from_tiktoken_encoder()` method. Note that splits from this method can be larger than the chunk size measured by the `tiktoken` tokenizer.
# 
# The `.from_tiktoken_encoder()` method takes either `encoding_name` as an argument (e.g. `cl100k_base`), or the `model_name` (e.g. `gpt-4`). All additional arguments like `chunk_size`, `chunk_overlap`, and `separators` are used to instantiate `CharacterTextSplitter`:

# In[6]:


text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base", chunk_size=100, chunk_overlap=0
)
texts = text_splitter.split_text(state_of_the_union)


# In[3]:


print(texts[0])


# To implement a hard constraint on the chunk size, we can use `RecursiveCharacterTextSplitter.from_tiktoken_encoder`, where each split will be recursively split if it has a larger size:

# In[4]:


from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4",
    chunk_size=100,
    chunk_overlap=0,
)


# We can also load a `TokenTextSplitter` splitter, which works with `tiktoken` directly and will ensure each split is smaller than chunk size.

# In[8]:


from langchain_text_splitters import TokenTextSplitter

text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)

texts = text_splitter.split_text(state_of_the_union)
print(texts[0])


# Some written languages (e.g. Chinese and Japanese) have characters which encode to 2 or more tokens. Using the `TokenTextSplitter` directly can split the tokens for a character between two chunks causing malformed Unicode characters. Use `RecursiveCharacterTextSplitter.from_tiktoken_encoder` or `CharacterTextSplitter.from_tiktoken_encoder` to ensure chunks contain valid Unicode strings.

# ## spaCy
# 
# :::note
# [spaCy](https://spacy.io/) is an open-source software library for advanced natural language processing, written in the programming languages Python and Cython.
# :::
# 
# LangChain implements splitters based on the [spaCy tokenizer](https://spacy.io/api/tokenizer).
# 
# 1. How the text is split: by `spaCy` tokenizer.
# 2. How the chunk size is measured: by number of characters.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  spacy')


# In[1]:


# This is a long document we can split up.
with open("state_of_the_union.txt") as f:
    state_of_the_union = f.read()


# In[4]:


from langchain_text_splitters import SpacyTextSplitter

text_splitter = SpacyTextSplitter(chunk_size=1000)

texts = text_splitter.split_text(state_of_the_union)
print(texts[0])


# ## SentenceTransformers
# 
# The [SentenceTransformersTokenTextSplitter](https://python.langchain.com/api_reference/text_splitters/sentence_transformers/langchain_text_splitters.sentence_transformers.SentenceTransformersTokenTextSplitter.html) is a specialized text splitter for use with the sentence-transformer models. The default behaviour is to split the text into chunks that fit the token window of the sentence transformer model that you would like to use.
# 
# To split text and constrain token counts according to the sentence-transformers tokenizer, instantiate a `SentenceTransformersTokenTextSplitter`. You can optionally specify:
# 
# - `chunk_overlap`: integer count of token overlap;
# - `model_name`: sentence-transformer model name, defaulting to `"sentence-transformers/all-mpnet-base-v2"`;
# - `tokens_per_chunk`: desired token count per chunk.

# In[2]:


from langchain_text_splitters import SentenceTransformersTokenTextSplitter

splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0)
text = "Lorem "

count_start_and_stop_tokens = 2
text_token_count = splitter.count_tokens(text=text) - count_start_and_stop_tokens
print(text_token_count)


# In[4]:


token_multiplier = splitter.maximum_tokens_per_chunk // text_token_count + 1

# `text_to_split` does not fit in a single chunk
text_to_split = text * token_multiplier

print(f"tokens in text to split: {splitter.count_tokens(text=text_to_split)}")


# In[5]:


text_chunks = splitter.split_text(text=text_to_split)

print(text_chunks[1])


# ## NLTK
# 
# :::note
# [The Natural Language Toolkit](https://en.wikipedia.org/wiki/Natural_Language_Toolkit), or more commonly [NLTK](https://www.nltk.org/), is a suite of libraries and programs for symbolic and statistical natural language processing (NLP) for English written in the Python programming language.
# :::
# 
# 
# Rather than just splitting on "\n\n", we can use `NLTK` to split based on [NLTK tokenizers](https://www.nltk.org/api/nltk.tokenize.html).
# 
# 1. How the text is split: by `NLTK` tokenizer.
# 2. How the chunk size is measured: by number of characters.

# In[ ]:


# pip install nltk


# In[1]:


# This is a long document we can split up.
with open("state_of_the_union.txt") as f:
    state_of_the_union = f.read()


# In[2]:


from langchain_text_splitters import NLTKTextSplitter

text_splitter = NLTKTextSplitter(chunk_size=1000)


# In[3]:


texts = text_splitter.split_text(state_of_the_union)
print(texts[0])


# ## KoNLPY
# 
# :::note
# [KoNLPy: Korean NLP in Python](https://konlpy.org/en/latest/) is is a Python package for natural language processing (NLP) of the Korean language.
# :::
# 
# Token splitting involves the segmentation of text into smaller, more manageable units called tokens. These tokens are often words, phrases, symbols, or other meaningful elements crucial for further processing and analysis. In languages like English, token splitting typically involves separating words by spaces and punctuation marks. The effectiveness of token splitting largely depends on the tokenizer's understanding of the language structure, ensuring the generation of meaningful tokens. Since tokenizers designed for the English language are not equipped to understand the unique semantic structures of other languages, such as Korean, they cannot be effectively used for Korean language processing.
# 
# ### Token splitting for Korean with KoNLPy's Kkma Analyzer
# In case of Korean text, KoNLPY includes at morphological analyzer called `Kkma` (Korean Knowledge Morpheme Analyzer). `Kkma` provides detailed morphological analysis of Korean text. It breaks down sentences into words and words into their respective morphemes, identifying parts of speech for each token. It can segment a block of text into individual sentences, which is particularly useful for processing long texts.
# 
# ### Usage Considerations
# While `Kkma` is renowned for its detailed analysis, it is important to note that this precision may impact processing speed. Thus, `Kkma` is best suited for applications where analytical depth is prioritized over rapid text processing.

# In[28]:


# pip install konlpy


# In[23]:


# This is a long Korean document that we want to split up into its component sentences.
with open("./your_korean_doc.txt") as f:
    korean_document = f.read()


# In[24]:


from langchain_text_splitters import KonlpyTextSplitter

text_splitter = KonlpyTextSplitter()


# In[37]:


texts = text_splitter.split_text(korean_document)
# The sentences are split with "\n\n" characters.
print(texts[0])


# ## Hugging Face tokenizer
# 
# [Hugging Face](https://huggingface.co/docs/tokenizers/index) has many tokenizers.
# 
# We use Hugging Face tokenizer, the [GPT2TokenizerFast](https://huggingface.co/Ransaka/gpt2-tokenizer-fast) to count the text length in tokens.
# 
# 1. How the text is split: by character passed in.
# 2. How the chunk size is measured: by number of tokens calculated by the `Hugging Face` tokenizer.

# In[1]:


from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")


# In[2]:


# This is a long document we can split up.
with open("state_of_the_union.txt") as f:
    state_of_the_union = f.read()
from langchain_text_splitters import CharacterTextSplitter


# In[3]:


text_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer, chunk_size=100, chunk_overlap=0
)
texts = text_splitter.split_text(state_of_the_union)


# In[4]:


print(texts[0])


# In[ ]:




