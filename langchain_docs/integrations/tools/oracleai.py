#!/usr/bin/env python
# coding: utf-8

# # Oracle AI Vector Search: Generate Summary
# 
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
# The guide demonstrates how to use Summary Capabilities within Oracle AI Vector Search to generate summary for your documents using OracleSummary.

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


# ### Generate Summary
# The Oracle AI Vector Search Langchain library offers a suite of APIs designed for document summarization. It supports multiple summarization providers such as Database, OCIGENAI, HuggingFace, among others, allowing users to select the provider that best meets their needs. To utilize these capabilities, users must configure the summary parameters as specified. For detailed information on these parameters, please consult the [Oracle AI Vector Search Guide book](https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/dbms_vector_chain1.html#GUID-EC9DDB58-6A15-4B36-BA66-ECBA20D2CE57).

# ***Note:*** The users may need to set proxy if they want to use some 3rd party summary generation providers other than Oracle's in-house and default provider: 'database'. If you don't have proxy, please remove the proxy parameter when you instantiate the OracleSummary.

# In[ ]:


# proxy to be used when we instantiate summary and embedder object
proxy = "<proxy>"


# The following sample code will show how to generate summary:

# In[ ]:


from langchain_community.utilities.oracleai import OracleSummary
from langchain_core.documents import Document

"""
# using 'ocigenai' provider
summary_params = {
    "provider": "ocigenai",
    "credential_name": "OCI_CRED",
    "url": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/summarizeText",
    "model": "cohere.command",
}

# using 'huggingface' provider
summary_params = {
    "provider": "huggingface",
    "credential_name": "HF_CRED",
    "url": "https://api-inference.huggingface.co/models/",
    "model": "facebook/bart-large-cnn",
    "wait_for_model": "true"
}
"""

# using 'database' provider
summary_params = {
    "provider": "database",
    "glevel": "S",
    "numParagraphs": 1,
    "language": "english",
}

# get the summary instance
# Remove proxy if not required
summ = OracleSummary(conn=conn, params=summary_params, proxy=proxy)
summary = summ.get_summary(
    "In the heart of the forest, "
    + "a lone fox ventured out at dusk, seeking a lost treasure. "
    + "With each step, memories flooded back, guiding its path. "
    + "As the moon rose high, illuminating the night, the fox unearthed "
    + "not gold, but a forgotten friendship, worth more than any riches."
)

print(f"Summary generated by OracleSummary: {summary}")


# ### End to End Demo
# Please refer to our complete demo guide [Oracle AI Vector Search End-to-End Demo Guide](https://github.com/langchain-ai/langchain/tree/master/cookbook/oracleai_demo.ipynb) to build an end to end RAG pipeline with the help of Oracle AI Vector Search.
# 
