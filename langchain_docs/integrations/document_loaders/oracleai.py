#!/usr/bin/env python
# coding: utf-8

# # Oracle AI Vector Search: Document Processing
# Oracle AI Vector Search is designed for Artificial Intelligence (AI) workloads that allows you to query data based on semantics, rather than keywords.
# One of the biggest benefits of Oracle AI Vector Search is that semantic search on unstructured data can be combined with relational search on business data in one single system.
# This is not only powerful but also significantly more effective because you don't need to add a specialized vector database, eliminating the pain of data fragmentation between multiple systems.
# 
# In addition, your vectors can benefit from all of Oracle Database’s most powerful features, like the following:
# 
#  * [Partitioning Support](https://www.oracle.com/database/technologies/partitioning.html)
#  * [Real Application Clusters scalability](https://www.oracle.com/database/real-application-clusters/)
#  * [Exadata smart scans](https://www.oracle.com/database/technologies/exadata/software/smartscan/)
#  * [Shard processing across geographically distributed databases](https://www.oracle.com/database/distributed-database/)
#  * [Transactions](https://docs.oracle.com/en/database/oracle/oracle-database/23/cncpt/transactions.html)
#  * [Parallel SQL](https://docs.oracle.com/en/database/oracle/oracle-database/21/vldbg/parallel-exec-intro.html#GUID-D28717E4-0F77-44F5-BB4E-234C31D4E4BA)
#  * [Disaster recovery](https://www.oracle.com/database/data-guard/)
#  * [Security](https://www.oracle.com/security/database-security/)
#  * [Oracle Machine Learning](https://www.oracle.com/artificial-intelligence/database-machine-learning/)
#  * [Oracle Graph Database](https://www.oracle.com/database/integrated-graph-database/)
#  * [Oracle Spatial and Graph](https://www.oracle.com/database/spatial/)
#  * [Oracle Blockchain](https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/dbms_blockchain_table.html#GUID-B469E277-978E-4378-A8C1-26D3FF96C9A6)
#  * [JSON](https://docs.oracle.com/en/database/oracle/oracle-database/23/adjsn/json-in-oracle-database.html)
# 
# 
# The guide demonstrates how to use Document Processing Capabilities within Oracle AI Vector Search to load and chunk documents using OracleDocLoader and OracleTextSplitter respectively.

# If you are just starting with Oracle Database, consider exploring the [free Oracle 23 AI](https://www.oracle.com/database/free/#resources) which provides a great introduction to setting up your database environment. While working with the database, it is often advisable to avoid using the system user by default; instead, you can create your own user for enhanced security and customization. For detailed steps on user creation, refer to our [end-to-end guide](https://github.com/langchain-ai/langchain/blob/master/cookbook/oracleai_demo.ipynb) which also shows how to set up a user in Oracle. Additionally, understanding user privileges is crucial for managing database security effectively. You can learn more about this topic in the official [Oracle guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/admqs/administering-user-accounts-and-security.html#GUID-36B21D72-1BBB-46C9-A0C9-F0D2A8591B8D) on administering user accounts and security.

# ### Prerequisites
# 
# Please install Oracle Python Client driver to use Langchain with Oracle AI Vector Search. 

# In[ ]:


# pip install oracledb


# ### Connect to Oracle Database
# The following sample code will show how to connect to Oracle Database. By default, python-oracledb runs in a ‘Thin’ mode which connects directly to Oracle Database. This mode does not need Oracle Client libraries. However, some additional functionality is available when python-oracledb uses them. Python-oracledb is said to be in ‘Thick’ mode when Oracle Client libraries are used. Both modes have comprehensive functionality supporting the Python Database API v2.0 Specification. See the following [guide](https://python-oracledb.readthedocs.io/en/latest/user_guide/appendix_a.html#featuresummary) that talks about features supported in each mode. You might want to switch to thick-mode if you are unable to use thin-mode.

# In[ ]:


import sys

import oracledb

# please update with your username, password, hostname and service_name
username = "<username>"
password = "<password>"
dsn = "<hostname>/<service_name>"

try:
    conn = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connection successful!")
except Exception as e:
    print("Connection failed!")
    sys.exit(1)


# Now let's create a table and insert some sample docs to test.

# In[ ]:


try:
    cursor = conn.cursor()

    drop_table_sql = """drop table if exists demo_tab"""
    cursor.execute(drop_table_sql)

    create_table_sql = """create table demo_tab (id number, data clob)"""
    cursor.execute(create_table_sql)

    insert_row_sql = """insert into demo_tab values (:1, :2)"""
    rows_to_insert = [
        (
            1,
            "If the answer to any preceding questions is yes, then the database stops the search and allocates space from the specified tablespace; otherwise, space is allocated from the database default shared temporary tablespace.",
        ),
        (
            2,
            "A tablespace can be online (accessible) or offline (not accessible) whenever the database is open.\nA tablespace is usually online so that its data is available to users. The SYSTEM tablespace and temporary tablespaces cannot be taken offline.",
        ),
        (
            3,
            "The database stores LOBs differently from other data types. Creating a LOB column implicitly creates a LOB segment and a LOB index. The tablespace containing the LOB segment and LOB index, which are always stored together, may be different from the tablespace containing the table.\nSometimes the database can store small amounts of LOB data in the table itself rather than in a separate LOB segment.",
        ),
    ]
    cursor.executemany(insert_row_sql, rows_to_insert)

    conn.commit()

    print("Table created and populated.")
    cursor.close()
except Exception as e:
    print("Table creation failed.")
    cursor.close()
    conn.close()
    sys.exit(1)


# ### Load Documents
# 
# Users have the flexibility to load documents from either the Oracle Database, a file system, or both, by appropriately configuring the loader parameters. For comprehensive details on these parameters, please consult the [Oracle AI Vector Search Guide](https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/dbms_vector_chain1.html#GUID-73397E89-92FB-48ED-94BB-1AD960C4EA1F).
# 
# A significant advantage of utilizing OracleDocLoader is its capability to process over 150 distinct file formats, eliminating the need for multiple loaders for different document types. For a complete list of the supported formats, please refer to the [Oracle Text Supported Document Formats](https://docs.oracle.com/en/database/oracle/oracle-database/23/ccref/oracle-text-supported-document-formats.html).
# 
# Below is a sample code snippet that demonstrates how to use OracleDocLoader

# In[ ]:


from langchain_community.document_loaders.oracleai import OracleDocLoader
from langchain_core.documents import Document

"""
# loading a local file
loader_params = {}
loader_params["file"] = "<file>"

# loading from a local directory
loader_params = {}
loader_params["dir"] = "<directory>"
"""

# loading from Oracle Database table
loader_params = {
    "owner": "<owner>",
    "tablename": "demo_tab",
    "colname": "data",
}

""" load the docs """
loader = OracleDocLoader(conn=conn, params=loader_params)
docs = loader.load()

""" verify """
print(f"Number of docs loaded: {len(docs)}")
# print(f"Document-0: {docs[0].page_content}") # content


# ### Split Documents
# The documents may vary in size, ranging from small to very large. Users often prefer to chunk their documents into smaller sections to facilitate the generation of embeddings. A wide array of customization options is available for this splitting process. For comprehensive details regarding these parameters, please consult the [Oracle AI Vector Search Guide](https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/dbms_vector_chain1.html#GUID-4E145629-7098-4C7C-804F-FC85D1F24240).
# 
# Below is a sample code illustrating how to implement this:

# In[ ]:


from langchain_community.document_loaders.oracleai import OracleTextSplitter
from langchain_core.documents import Document

"""
# Some examples
# split by chars, max 500 chars
splitter_params = {"split": "chars", "max": 500, "normalize": "all"}

# split by words, max 100 words
splitter_params = {"split": "words", "max": 100, "normalize": "all"}

# split by sentence, max 20 sentences
splitter_params = {"split": "sentence", "max": 20, "normalize": "all"}
"""

# split by default parameters
splitter_params = {"normalize": "all"}

# get the splitter instance
splitter = OracleTextSplitter(conn=conn, params=splitter_params)

list_chunks = []
for doc in docs:
    chunks = splitter.split_text(doc.page_content)
    list_chunks.extend(chunks)

""" verify """
print(f"Number of Chunks: {len(list_chunks)}")
# print(f"Chunk-0: {list_chunks[0]}") # content


# ### End to End Demo
# Please refer to our complete demo guide [Oracle AI Vector Search End-to-End Demo Guide](https://github.com/langchain-ai/langchain/tree/master/cookbook/oracleai_demo.ipynb) to build an end to end RAG pipeline with the help of Oracle AI Vector Search.
# 
