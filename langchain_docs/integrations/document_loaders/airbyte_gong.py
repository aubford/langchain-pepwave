#!/usr/bin/env python
# coding: utf-8
---
sidebar_class_name: hidden
---
# # Airbyte Gong (Deprecated)

# Note: This connector-specific loader is deprecated. Please use [`AirbyteLoader`](/docs/integrations/document_loaders/airbyte) instead.
# 
# >[Airbyte](https://github.com/airbytehq/airbyte) is a data integration platform for ELT pipelines from APIs, databases & files to warehouses & lakes. It has the largest catalog of ELT connectors to data warehouses and databases.
# 
# This loader exposes the Gong connector as a document loader, allowing you to load various Gong objects as documents.

# 

# ## Installation

# First, you need to install the `airbyte-source-gong` python package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  airbyte-source-gong')


# ## Example

# Check out the [Airbyte documentation page](https://docs.airbyte.com/integrations/sources/gong/) for details about how to configure the reader.
# The JSON schema the config object should adhere to can be found on Github: [https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-gong/source_gong/spec.yaml](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-gong/source_gong/spec.yaml).
# 
# The general shape looks like this:
# ```python
# {
#   "access_key": "<access key name>",
#   "access_key_secret": "<access key secret>",
#   "start_date": "<date from which to start retrieving records from in ISO format, e.g. 2020-10-20T00:00:00Z>",
# }
# ```
# 
# By default all fields are stored as metadata in the documents and the text is set to an empty string. Construct the text of the document by transforming the documents returned by the reader.

# In[ ]:


from langchain_community.document_loaders.airbyte import AirbyteGongLoader

config = {
    # your gong configuration
}

loader = AirbyteGongLoader(
    config=config, stream_name="calls"
)  # check the documentation linked above for a list of all streams


# Now you can load documents the usual way

# In[ ]:


docs = loader.load()


# As `load` returns a list, it will block until all documents are loaded. To have better control over this process, you can also you the `lazy_load` method which returns an iterator instead:

# In[ ]:


docs_iterator = loader.lazy_load()


# Keep in mind that by default the page content is empty and the metadata object contains all the information from the record. To process documents, create a class inheriting from the base loader and implement the `_handle_records` method yourself:

# In[ ]:


from langchain_core.documents import Document


def handle_record(record, id):
    return Document(page_content=record.data["title"], metadata=record.data)


loader = AirbyteGongLoader(
    config=config, record_handler=handle_record, stream_name="calls"
)
docs = loader.load()


# ## Incremental loads
# 
# Some streams allow incremental loading, this means the source keeps track of synced records and won't load them again. This is useful for sources that have a high volume of data and are updated frequently.
# 
# To take advantage of this, store the `last_state` property of the loader and pass it in when creating the loader again. This will ensure that only new records are loaded.

# In[ ]:


last_state = loader.last_state  # store safely

incremental_loader = AirbyteGongLoader(
    config=config, stream_name="calls", state=last_state
)

new_docs = incremental_loader.load()

