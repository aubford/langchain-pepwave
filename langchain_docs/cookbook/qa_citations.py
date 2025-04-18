#!/usr/bin/env python
# coding: utf-8

# # Citing retrieval sources
# 
# This notebook shows how to use OpenAI functions ability to extract citations from text.

# In[1]:


from langchain.chains import create_citation_fuzzy_match_chain
from langchain_openai import ChatOpenAI


# In[2]:


question = "What did the author do during college?"
context = """
My name is Jason Liu, and I grew up in Toronto Canada but I was born in China.
I went to an arts highschool but in university I studied Computational Mathematics and physics. 
As part of coop I worked at many companies including Stitchfix, Facebook.
I also started the Data Science club at the University of Waterloo and I was the president of the club for 2 years.
"""


# In[3]:


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")


# In[4]:


chain = create_citation_fuzzy_match_chain(llm)


# In[5]:


result = chain.run(question=question, context=context)


# In[6]:


print(result)


# In[7]:


def highlight(text, span):
    return (
        "..."
        + text[span[0] - 20 : span[0]]
        + "*"
        + "\033[91m"
        + text[span[0] : span[1]]
        + "\033[0m"
        + "*"
        + text[span[1] : span[1] + 20]
        + "..."
    )


# In[8]:


for fact in result.answer:
    print("Statement:", fact.fact)
    for span in fact.get_spans(context):
        print("Citation:", highlight(context, span))
    print()


# In[ ]:




