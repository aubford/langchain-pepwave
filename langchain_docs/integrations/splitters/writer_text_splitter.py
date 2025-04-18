#!/usr/bin/env python
# coding: utf-8

# # Writer Text Splitter
# 
# This notebook provides a quick overview for getting started with Writer's [text splitter](/docs/concepts/text_splitters/).
# 
# Writer's [context-aware splitting endpoint](https://dev.writer.com/api-guides/tools#context-aware-text-splitting) provides intelligent text splitting capabilities for long documents (up to 4000 words). Unlike simple character-based splitting, it preserves the semantic meaning and context between chunks, making it ideal for processing long-form content while maintaining coherence. In `langchain-writer`, we provide usage of Writer's context-aware splitting endpoint as a LangChain text splitter.
# 
# ## Overview
# 
# ### Integration details
# | Class                                                                                                                                    | Package          | Local | Serializable | JS support |                                        Package downloads                                         |                                        Package latest                                         |
# |:-----------------------------------------------------------------------------------------------------------------------------------------|:-----------------| :---: | :---: |:----------:|:------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------:|
# | [WriterTextSplitter](https://github.com/writer/langchain-writer/blob/main/langchain_writer/text_splitter.py#L11) | [langchain-writer](https://pypi.org/project/langchain-writer/) |      ❌       |                                       ❌                                       | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-writer?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-writer?style=flat-square&label=%20) |

# ## Setup
# 
# The `WriterTextSplitter` is available in the `langchain-writer` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --quiet -U langchain-writer')


# ### Credentials
# 
# Sign up for [Writer AI Studio](https://app.writer.com/aistudio/signup?utm_campaign=devrel) to generate an API key (you can follow this [Quickstart](https://dev.writer.com/api-guides/quickstart)). Then, set the WRITER_API_KEY environment variable:

# In[ ]:


import getpass
import os

if not os.getenv("WRITER_API_KEY"):
    os.environ["WRITER_API_KEY"] = getpass.getpass("Enter your Writer API key: ")


# It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability. If you wish to do so, you can set the `LANGSMITH_TRACING` and `LANGSMITH_API_KEY` environment variables:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ### Instantiation
# 
# Instantiate an instance of `WriterTextSplitter` with the `strategy` parameter set to one of the following:
# 
# - `llm_split`: Uses language model for precise semantic splitting
# - `fast_split`: Uses heuristic-based approach for quick splitting
# - `hybrid_split`: Combines both approaches
# 

# In[ ]:


from langchain_writer.text_splitter import WriterTextSplitter

splitter = WriterTextSplitter(strategy="fast_split")


# ## Usage
# The `WriterTextSplitter` can be used synchronously or asynchronously.
# 
# ### Synchronous usage
# To use the `WriterTextSplitter` synchronously, call the `split_text` method with the text you want to split:

# In[ ]:


text = """Reeeeeeeeeeeeeeeeeeeeeaally long text you want to divide into smaller chunks. For example you can add a poem multiple times:
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim,
Because it was grassy and wanted wear;
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way,
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I—
I took the one less traveled by,
And that has made all the difference.

Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim,
Because it was grassy and wanted wear;
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way,
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I—
I took the one less traveled by,
And that has made all the difference.

Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim,
Because it was grassy and wanted wear;
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way,
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I—
I took the one less traveled by,
And that has made all the difference.
"""

chunks = splitter.split_text(text)
chunks


# You can print the length of the chunks to see how many chunks were created:

# In[ ]:


print(len(chunks))


# ### Asynchronous usage
# To use the `WriterTextSplitter` asynchronously, call the `asplit_text` method with the text you want to split:

# In[ ]:


async_chunks = await splitter.asplit_text(text)
async_chunks


# Print the length of the chunks to see how many chunks were created:

# In[ ]:


print(len(async_chunks))


# ## API reference
# For detailed documentation of all `WriterTextSplitter` features and configurations head to the [API reference](https://python.langchain.com/api_reference/writer/text_splitter/langchain_writer.text_splitter.WriterTextSplitter.html#langchain_writer.text_splitter.WriterTextSplitter).
# 
# ## Additional resources
# You can find information about Writer's models (including costs, context windows, and supported input types) and tools in the [Writer docs](https://dev.writer.com/home).
