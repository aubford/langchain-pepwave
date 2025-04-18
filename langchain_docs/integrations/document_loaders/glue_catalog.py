#!/usr/bin/env python
# coding: utf-8

# # Glue Catalog
# 
# 
# The [AWS Glue Data Catalog](https://docs.aws.amazon.com/en_en/glue/latest/dg/catalog-and-crawler.html) is a centralized metadata repository that allows you to manage, access, and share metadata about your data stored in AWS. It acts as a metadata store for your data assets, enabling various AWS services and your applications to query and connect to the data they need efficiently.
# 
# When you define data sources, transformations, and targets in AWS Glue, the metadata about these elements is stored in the Data Catalog. This includes information about data locations, schema definitions, runtime metrics, and more. It supports various data store types, such as Amazon S3, Amazon RDS, Amazon Redshift, and external databases compatible with JDBC. It is also directly integrated with Amazon Athena, Amazon Redshift Spectrum, and Amazon EMR, allowing these services to directly access and query the data.
# 
# The Langchain GlueCatalogLoader will get the schema of all tables inside the given Glue database in the same format as Pandas dtype.

# ## Setting up
# 
# - Follow [instructions to set up an AWS account](https://docs.aws.amazon.com/athena/latest/ug/setting-up.html).
# - Install the boto3 library: `pip install boto3`
# 

# ## Example

# In[ ]:


from langchain_community.document_loaders.glue_catalog import GlueCatalogLoader


# In[ ]:


database_name = "my_database"
profile_name = "my_profile"

loader = GlueCatalogLoader(
    database=database_name,
    profile_name=profile_name,
)

schemas = loader.load()
print(schemas)


# ## Example with table filtering
# 
# Table filtering allows you to selectively retrieve schema information for a specific subset of tables within a Glue database. Instead of loading the schemas for all tables, you can use the `table_filter` argument to specify exactly which tables you're interested in.

# In[ ]:


from langchain_community.document_loaders.glue_catalog import GlueCatalogLoader


# In[ ]:


database_name = "my_database"
profile_name = "my_profile"
table_filter = ["table1", "table2", "table3"]

loader = GlueCatalogLoader(
    database=database_name, profile_name=profile_name, table_filter=table_filter
)

schemas = loader.load()
print(schemas)

