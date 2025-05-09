#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Permit
---
# # Permit
# 
# Permit is an access control platform that provides fine-grained, real-time permission management using various models such as RBAC, ABAC, and ReBAC. It enables organizations to enforce dynamic policies across their applications, ensuring that only authorized users can access specific resources.
# 
# ## Overview
# 
# This package provides two Langchain tools for JWT validation and permission checking using Permit:
# 
# * LangchainJWTValidationTool: Validates JWT tokens against a JWKS endpoint
# 
# * LangchainPermissionsCheckTool: Checks user permissions using Permit
# 
# 
# ## Setup
# 
# Set up the following environment variables:
# 
# ```bash
# PERMIT_API_KEY=your_permit_api_key
# JWKS_URL=your_jwks_endpoint_url
# PERMIT_PDP_URL=your_permit_pdp_url  # Usually http://localhost:7766 for local development or your real deployment
# ```
# 
# Make sure your PDP (Policy Decision Point) is running at PERMIT_PDP_URL.
# See [Permit docs](https://docs.permit.io/concepts/pdp/overview/) for details on policy setup and how to launch the PDP container.

# ### Credentials
# 
# ```bash
# PERMIT_API_KEY=
# JWKS_URL=your_jwks_endpoint_url # or your deployed url
# PERMIT_PDP_URL=your_pdp_url # or your deployed url
# TEST_JWT_TOKEN= # for quick test purposes
# ```

# It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability:

# ## Instantiation
# 
# ### JWT Validation Tool
# The JWT Validation tool verifies JWT tokens against a JWKS (JSON Web Key Set) endpoint.
# 
# ```python
# from langchain_permit.tools import LangchainJWTValidationTool
# 
# # Initialize the tool
# jwt_validator = LangchainJWTValidationTool(
#     jwks_url=#your url endpoint
# )
# ```
# 
# ### Configuration Options
# You can initialize the tool with either:
# 
# * A JWKS URL
# * Direct JWKS JSON data
# * Environment variable (JWKS_URL)
# 
# ```python
# # Using direct JWKS JSON
# jwt_validator = LangchainJWTValidationTool(
#     jwks_json={
#         "keys": [
#             {
#                 "kid": "key-id",
#                 "kty": "RSA",
#                 ...
#             }
#         ]
#     }
# )
# ```
# 
# ### Permissions Check Tool
# The Permissions Check tool integrates with Permit.io to verify user permissions against resources.
# 
# ```python
# from permit import Permit
# from langchain_permit.tools import LangchainPermissionsCheckTool
# 
# # Initialize Permit client
# permit_client = Permit(
#     token="your_permit_api_key",
#     pdp=# Your PDP URL
# )
# 
# # Initialize the tool
# permissions_checker = LangchainPermissionsCheckTool(
#     permit=permit_client
# )
# ```
# 
# This documentation demonstrates the key features and usage patterns of both tools.

# ## Invocation
# 
# ### [Invoke directly with args](https://docs.permit.io/)
# 
# ### JWT Validation Tool
# 
# ```python
# # Validate a token
# async def validate_token():
#     claims = await jwt_validator._arun(
#         "..."  # Your JWT token
#     )
#     print("Validated Claims:", claims)
# ```
# 
# ### Permissions Check Tool
# 
# ```python
# # Check permissions
# async def check_user_permission():
#     result = await permissions_checker._arun(
#         user={
#             "key": "user-123",
#             "firstName": "John"
#         },
#         action="read",
#         resource={
#             "type": "Document",
#             "tenant": "default"
#         }
#     )
#     print("Permission granted:", result)
# ```
# 
# #### Input Formats
# The permissions checker accepts different input formats:
# 
# 1. Simple string for user (converts to user key):
# 
# ```python
# result = await permissions_checker._arun(
#     user="user-123",
#     action="read",
#     resource="Document"
# )
# ```
# 
# 2. Full user object:
# 
# ```python
# result = await permissions_checker._arun(
#     user={
#         "key": "user-123",
#         "firstName": "John",
#         "lastName": "Doe",
#         "email": "john@example.com",
#         "attributes": {"department": "IT"}
#     },
#     action="read",
#     resource={
#         "type": "Document",
#         "key": "doc-123",
#         "tenant": "techcorp",
#         "attributes": {"confidentiality": "high"}
#     }
# )
# ```
# 

# ### [Invoke with ToolCall](https://docs.permit.io/)
# 
# (TODO)

# ## Chaining
# 
# - TODO: Add user question and run cells
# 
# We can use our tool in a chain by first binding it to a [tool-calling model](https://docs.permit.io/) and then calling it:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm" />
# 

# ### Additional Demo Scripts
# 
# For fully runnable demos, check out the `/langchain_permit/examples/demo_scripts` folder in this [repository](https://github.com/permitio/langchain-permit). You’ll find:
# 
# * demo_jwt_validation.py – A quick script showing how to validate JWTs using LangchainJWTValidationTool.
# 
# * demo_permissions_check.py – A script that performs Permit.io permission checks using LangchainPermissionsCheckTool.
# 
# Just run `python demo_jwt_validation.py` or `python demo_permissions_check.py` (after setting your environment variables) to see these tools in action.

# ## API reference
# 
# For detailed documentation of all Permit features and configurations head to the API reference: https://docs.permit.io/
