#!/usr/bin/env python
# coding: utf-8

# # How to load CSVs
# 
# A [comma-separated values (CSV)](https://en.wikipedia.org/wiki/Comma-separated_values) file is a delimited text file that uses a comma to separate values. Each line of the file is a data record. Each record consists of one or more fields, separated by commas.
# 
# LangChain implements a [CSV Loader](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.csv_loader.CSVLoader.html) that will load CSV files into a sequence of [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html#langchain_core.documents.base.Document) objects. Each row of the CSV file is translated to one document.

# In[1]:


from langchain_community.document_loaders.csv_loader import CSVLoader

file_path = "../integrations/document_loaders/example_data/mlb_teams_2012.csv"

loader = CSVLoader(file_path=file_path)
data = loader.load()

for record in data[:2]:
    print(record)


# ## Customizing the CSV parsing and loading
# 
# `CSVLoader` will accept a `csv_args` kwarg that supports customization of arguments passed to Python's `csv.DictReader`. See the [csv module](https://docs.python.org/3/library/csv.html) documentation for more information of what csv args are supported.

# In[2]:


loader = CSVLoader(
    file_path=file_path,
    csv_args={
        "delimiter": ",",
        "quotechar": '"',
        "fieldnames": ["MLB Team", "Payroll in millions", "Wins"],
    },
)

data = loader.load()
for record in data[:2]:
    print(record)


# ## Specify a column to identify the document source
# 
# The `"source"` key on [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html#langchain_core.documents.base.Document) metadata can be set using a column of the CSV. Use the `source_column` argument to specify a source for the document created from each row. Otherwise `file_path` will be used as the source for all documents created from the CSV file.
# 
# This is useful when using documents loaded from CSV files for chains that answer questions using sources.

# In[3]:


loader = CSVLoader(file_path=file_path, source_column="Team")

data = loader.load()
for record in data[:2]:
    print(record)


# ## Load from a string
# 
# Python's `tempfile` can be used when working with CSV strings directly.

# In[4]:


import tempfile
from io import StringIO

string_data = """
"Team", "Payroll (millions)", "Wins"
"Nationals",     81.34, 98
"Reds",          82.20, 97
"Yankees",      197.96, 95
"Giants",       117.62, 94
""".strip()


with tempfile.NamedTemporaryFile(delete=False, mode="w+") as temp_file:
    temp_file.write(string_data)
    temp_file_path = temp_file.name

loader = CSVLoader(file_path=temp_file_path)
data = loader.load()
for record in data[:2]:
    print(record)

