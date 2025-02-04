#!/usr/bin/env python
# coding: utf-8

# # FireCrawl
# 
# [FireCrawl](https://firecrawl.dev/?ref=langchain) crawls and convert any website into LLM-ready data. It crawls all accessible subpages and give you clean markdown and metadata for each. No sitemap required.
# 
# FireCrawl handles complex tasks such as reverse proxies, caching, rate limits, and content blocked by JavaScript. Built by the [mendable.ai](https://mendable.ai) team.
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/document_loaders/web_loaders/firecrawl/)|
# | :--- | :--- | :---: | :---: |  :---: |
# | [FireCrawlLoader](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.firecrawl.FireCrawlLoader.html) | [langchain_community](https://python.langchain.com/api_reference/community/index.html) | ✅ | ❌ | ✅ | 
# ### Loader features
# | Source | Document Lazy Loading | Native Async Support
# | :---: | :---: | :---: | 
# | FireCrawlLoader | ✅ | ❌ | 
# 

# ## Setup

# In[ ]:


pip install firecrawl-py


# ## Usage

# You will need to get your own API key. See https://firecrawl.dev

# In[ ]:


from langchain_community.document_loaders.firecrawl import FireCrawlLoader


# In[ ]:


loader = FireCrawlLoader(
    api_key="YOUR_API_KEY", url="https://firecrawl.dev", mode="scrape"
)


# In[ ]:


pages = []
for doc in loader.lazy_load():
    pages.append(doc)
    if len(pages) >= 10:
        # do some paged operation, e.g.
        # index.upsert(page)

        pages = []


# In[ ]:


pages


# ## Modes
# 
# - `scrape`: Scrape single url and return the markdown.
# - `crawl`: Crawl the url and all accessible sub pages and return the markdown for each one.
# - `map`: Maps the URL and returns a list of semantically related pages.

# ### Crawl
# 
# 

# In[ ]:


loader = FireCrawlLoader(
    api_key="YOUR_API_KEY",
    url="https://firecrawl.dev",
    mode="crawl",
)


# In[ ]:


data = loader.load()


# In[ ]:


print(pages[0].page_content[:100])
print(pages[0].metadata)


# #### Crawl Options
# 
# You can also pass `params` to the loader. This is a dictionary of options to pass to the crawler. See the [FireCrawl API documentation](https://github.com/mendableai/firecrawl-py) for more information.

# ### Map

# In[ ]:


loader = FireCrawlLoader(api_key="YOUR_API_KEY", url="firecrawl.dev", mode="map")


# In[ ]:


docs = loader.load()


# In[ ]:


docs


# #### Map Options
# 
# You can also pass `params` to the loader. This is a dictionary of options to pass to the loader. See the [FireCrawl API documentation](https://github.com/mendableai/firecrawl-py) for more information.

# ## API reference
# 
# For detailed documentation of all `FireCrawlLoader` features and configurations head to the API reference: https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.firecrawl.FireCrawlLoader.html
