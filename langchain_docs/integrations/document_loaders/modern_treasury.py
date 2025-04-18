#!/usr/bin/env python
# coding: utf-8

# # Modern Treasury
# 
# >[Modern Treasury](https://www.moderntreasury.com/) simplifies complex payment operations. It is a unified platform to power products and processes that move money.
# >- Connect to banks and payment systems
# >- Track transactions and balances in real-time
# >- Automate payment operations for scale
# 
# This notebook covers how to load data from the `Modern Treasury REST API` into a format that can be ingested into LangChain, along with example usage for vectorization.

# In[1]:


from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders import ModernTreasuryLoader


# The Modern Treasury API requires an organization ID and API key, which can be found in the Modern Treasury dashboard within developer settings.
# 
# This document loader also requires a `resource` option which defines what data you want to load.
# 
# Following resources are available:
# 
# `payment_orders` [Documentation](https://docs.moderntreasury.com/reference/payment-order-object)
# 
# `expected_payments` [Documentation](https://docs.moderntreasury.com/reference/expected-payment-object)
# 
# `returns` [Documentation](https://docs.moderntreasury.com/reference/return-object)
# 
# `incoming_payment_details` [Documentation](https://docs.moderntreasury.com/reference/incoming-payment-detail-object)
# 
# `counterparties` [Documentation](https://docs.moderntreasury.com/reference/counterparty-object)
# 
# `internal_accounts` [Documentation](https://docs.moderntreasury.com/reference/internal-account-object)
# 
# `external_accounts` [Documentation](https://docs.moderntreasury.com/reference/external-account-object)
# 
# `transactions` [Documentation](https://docs.moderntreasury.com/reference/transaction-object)
# 
# `ledgers` [Documentation](https://docs.moderntreasury.com/reference/ledger-object)
# 
# `ledger_accounts` [Documentation](https://docs.moderntreasury.com/reference/ledger-account-object)
# 
# `ledger_transactions` [Documentation](https://docs.moderntreasury.com/reference/ledger-transaction-object)
# 
# `events` [Documentation](https://docs.moderntreasury.com/reference/events)
# 
# `invoices` [Documentation](https://docs.moderntreasury.com/reference/invoices)
# 

# In[ ]:


modern_treasury_loader = ModernTreasuryLoader("payment_orders")


# In[ ]:


# Create a vectorstore retriever from the loader
# see https://python.langchain.com/en/latest/modules/data_connection/getting_started.html for more details

index = VectorstoreIndexCreator().from_loaders([modern_treasury_loader])
modern_treasury_doc_retriever = index.vectorstore.as_retriever()

