#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Zotero
---
# # ZoteroRetriever
# 
# This will help you getting started with the Zotero [retriever](/docs/concepts/retrievers). For detailed documentation of all ZoteroRetriever features and configurations head to the [Github page](https://github.com/TimBMK/langchain-zotero-retriever).
# 
# ### Integration details
# 
# 
# | Retriever | Source | Package |
# | :--- | :--- | :---: |
# [ZoteroRetriever](https://github.com/TimBMK/langchain-zotero-retriever) | [Zotero API](https://www.zotero.org/support/dev/web_api/v3/start) | langchain-community |
# 
# ## Setup
# 

# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# This retriever lives in the `langchain-zotero-retriever` package. We also require the `pyzotero` dependency:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-zotero-retriever pyzotero')


# ## Instantiation
# 
# `ZoteroRetriever` parameters include:
# - `k`: Number of results to include (Default: 50)
# - `type`: Type of search to perform. "Top" retrieves top level Zotero library items, "items" returns any Zotero library items. (Default: top)
# - `get_fulltext`: Retrieves full texts if they are attached to the items in the library. If False, or no text is attached, returns an empty string as page_content. (Default: True)
# - `library_id`: ID of the Zotero library to search. Required to connect to a library.
# - `library_type`: Type of library to search. "user" for personal library, "group" for shared group libraries. (Default: user)
# - `api_key`: Zotero API key if not set as an environment variable. Optional, required to access non-public group libraries or your personal library. Fetched automatically if provided as ZOTERO_API_KEY environment variable.
# 

# In[ ]:


from langchain_zotero_retriever.retrievers import ZoteroRetriever

retriever = ZoteroRetriever(
    k=10,
    library_id="2319375",  # a public group library that does not require an API key for access
    library_type="group",  # set this to "user" if you are using a personal library. Personal libraries require an API key
)


# ## Usage
# 
# Apart from the `query`, the retriever provides these additional search parameters:
# - `itemType`: Type of item to search for (e.g. "book" or "journalArticle")
# - `tag`: for searching over tags attached to library items (see search syntax for combining multiple tags)
# - `qmode`: Search mode to use. Changes what the query searches over. "everything" includes full-text content. "titleCreatorYear" to search over title, authors and year.
# - `since`: Return only objects modified after the specified library version. Defaults to return everything.
# 
# For Search Syntax, see Zotero API Documentation: https://www.zotero.org/support/dev/web_api/v3/basics#search_syntax
# 
# For the full API schema (including available itemTypes) see: https://github.com/zotero/zotero-schema

# In[ ]:


query = "Zuboff"

retriever.invoke(query)


# In[ ]:


tags = [
    "Surveillance",
    "Digital Capitalism",
]  # note that providing tags as a list will result in a logical AND operation

retriever.invoke("", tag=tags)


# ## Use within a chain
# 
# Due to the way the Zotero API search operates, directly passing a user question to the ZoteroRetriever will often not return satisfactory results. For use in chains or agentic frameworks, it is recommended to turn the ZoteroRetriever into a [tool](https://python.langchain.com/docs/how_to/custom_tools/#creating-tools-from-functions). This way, the LLM can turn the user query into a more concise search query for the API. Furthermore, this allows the LLM to fill in additional search parameters, such as tag or item type.

# In[ ]:


from typing import List, Optional, Union

from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.tools import StructuredTool, tool
from langchain_openai import ChatOpenAI


def retrieve(
    query: str,
    itemType: Optional[str],
    tag: Optional[Union[str, List[str]]],
    qmode: str = "everything",
    since: Optional[int] = None,
):
    retrieved_docs = retriever.invoke(
        query, itemType=itemType, tag=tag, qmode=qmode, since=since
    )
    serialized_docs = "\n\n".join(
        (
            f"Metadata: { {key: doc.metadata[key] for key in doc.metadata if key != 'abstractNote'} }\n"
            f"Abstract: {doc.metadata['abstractNote']}\n"
        )
        for doc in retrieved_docs
    )

    return serialized_docs, retrieved_docs


description = """Search and return relevant documents from a Zotero library. The following search parameters can be used:

    Args:
        query: str: The search query to be used. Try to keep this specific and short, e.g. a specific topic or author name
        itemType: Optional. Type of item to search for (e.g. "book" or "journalArticle"). Multiple types can be passed as a string separated by "||", e.g. "book || journalArticle". Defaults to all types.
        tag: Optional. For searching over tags attached to library items. If documents tagged with multiple tags are to be retrieved, pass them as a list. If documents with any of the tags are to be retrieved, pass them as a string separated by "||", e.g. "tag1 || tag2"
        qmode: Search mode to use. Changes what the query searches over. "everything" includes full-text content. "titleCreatorYear" to search over title, authors and year. Defaults to "everything".
        since: Return only objects modified after the specified library version. Defaults to return everything.
    """

retriever_tool = StructuredTool.from_function(
    func=retrieve,
    name="retrieve",
    description=description,
    return_direct=True,
)


llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18")

llm_with_tools = llm.bind_tools([retrieve])

q = "What journal articles do I have on Surveillance in the zotero library?"

chain = llm_with_tools | PydanticToolsParser(tools=[retrieve])

chain.invoke(q)


# ## API reference
# 
# For detailed documentation of all ZoteroRetriever features and configurations head to the [Github page](https://github.com/TimBMK/langchain-zotero-retriever).
# 
# For detailed documentation on the Zotero API, head to the [Zotero API reference](https://www.zotero.org/support/dev/web_api/v3/start).
