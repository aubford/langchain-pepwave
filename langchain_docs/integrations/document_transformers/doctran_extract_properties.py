#!/usr/bin/env python
# coding: utf-8

# # Doctran: extract properties
# 
# We can extract useful features of documents using the [Doctran](https://github.com/psychic-api/doctran) library, which uses OpenAI's function calling feature to extract specific metadata.
# 
# Extracting metadata from documents is helpful for a variety of tasks, including:
# 
# * **Classification:** classifying documents into different categories
# * **Data mining:** Extract structured data that can be used for data analysis
# * **Style transfer:** Change the way text is written to more closely match expected user input, improving vector search results

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  doctran')


# In[1]:


import json

from langchain_community.document_transformers import DoctranPropertyExtractor
from langchain_core.documents import Document


# In[2]:


from dotenv import load_dotenv

load_dotenv()


# ## Input
# This is the document we'll extract properties from.

# In[3]:


sample_text = """[Generated with ChatGPT]

Confidential Document - For Internal Use Only

Date: July 1, 2023

Subject: Updates and Discussions on Various Topics

Dear Team,

I hope this email finds you well. In this document, I would like to provide you with some important updates and discuss various topics that require our attention. Please treat the information contained herein as highly confidential.

Security and Privacy Measures
As part of our ongoing commitment to ensure the security and privacy of our customers' data, we have implemented robust measures across all our systems. We would like to commend John Doe (email: john.doe@example.com) from the IT department for his diligent work in enhancing our network security. Moving forward, we kindly remind everyone to strictly adhere to our data protection policies and guidelines. Additionally, if you come across any potential security risks or incidents, please report them immediately to our dedicated team at security@example.com.

HR Updates and Employee Benefits
Recently, we welcomed several new team members who have made significant contributions to their respective departments. I would like to recognize Jane Smith (SSN: 049-45-5928) for her outstanding performance in customer service. Jane has consistently received positive feedback from our clients. Furthermore, please remember that the open enrollment period for our employee benefits program is fast approaching. Should you have any questions or require assistance, please contact our HR representative, Michael Johnson (phone: 418-492-3850, email: michael.johnson@example.com).

Marketing Initiatives and Campaigns
Our marketing team has been actively working on developing new strategies to increase brand awareness and drive customer engagement. We would like to thank Sarah Thompson (phone: 415-555-1234) for her exceptional efforts in managing our social media platforms. Sarah has successfully increased our follower base by 20% in the past month alone. Moreover, please mark your calendars for the upcoming product launch event on July 15th. We encourage all team members to attend and support this exciting milestone for our company.

Research and Development Projects
In our pursuit of innovation, our research and development department has been working tirelessly on various projects. I would like to acknowledge the exceptional work of David Rodriguez (email: david.rodriguez@example.com) in his role as project lead. David's contributions to the development of our cutting-edge technology have been instrumental. Furthermore, we would like to remind everyone to share their ideas and suggestions for potential new projects during our monthly R&D brainstorming session, scheduled for July 10th.

Please treat the information in this document with utmost confidentiality and ensure that it is not shared with unauthorized individuals. If you have any questions or concerns regarding the topics discussed, please do not hesitate to reach out to me directly.

Thank you for your attention, and let's continue to work together to achieve our goals.

Best regards,

Jason Fan
Cofounder & CEO
Psychic
jason@psychic.dev
"""
print(sample_text)


# In[4]:


documents = [Document(page_content=sample_text)]
properties = [
    {
        "name": "category",
        "description": "What type of email this is.",
        "type": "string",
        "enum": ["update", "action_item", "customer_feedback", "announcement", "other"],
        "required": True,
    },
    {
        "name": "mentions",
        "description": "A list of all people mentioned in this email.",
        "type": "array",
        "items": {
            "name": "full_name",
            "description": "The full name of the person mentioned.",
            "type": "string",
        },
        "required": True,
    },
    {
        "name": "eli5",
        "description": "Explain this email to me like I'm 5 years old.",
        "type": "string",
        "required": True,
    },
]
property_extractor = DoctranPropertyExtractor(properties=properties)


# ## Output
# After extracting properties from a document, the result will be returned as a new document with properties provided in the metadata

# In[5]:


extracted_document = property_extractor.transform_documents(
    documents, properties=properties
)


# In[6]:


print(json.dumps(extracted_document[0].metadata, indent=2))


# In[ ]:




