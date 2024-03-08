# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] editable=true slideshow={"slide_type": ""}
# # Exchange Factory
#
# Use this notebook to create an exchange of assets from two issuers.

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ## Configure Exchange and Issuer Information
#
# This section enables customization of the wallet and the issuer with which it is associated.
#
# * identity : the identity of the creator of the asset type
# * offer_context_file : the name of the context file with information about the offered asset
# * offer_count : the number of assets that will be offered
# * request_context_file : the name of the context file with information about the requested asset
# * request_count : the number of assets that are requested
#
# Note that the notebook assumes that there is a key file for the identity of the form: `${keys}/${identity}_private.pem`.

# %% editable=true slideshow={"slide_type": ""}
identity = input('Identity of the exchange creator: ')
offer_context_file = input('Path to the contract context file for the offer issuer')
offer_count = input('How many assets do you want to offer [1]') or 1
request_context_file = input('Path to the contract context file for the requested issuer')
request_count = input('How many assets do you want to receive [1]') or 1
service_host = input('Service host [localhost]: ') or "localhost"

# %% [markdown] editable=true slideshow={"slide_type": ""}
# ## Create a New Exchange Notebook
#
# Create a new exchange notebook with the specific issuers identified.

# %% editable=true slideshow={"slide_type": ""}
parameters = {
    'identity' : identity,
    'offer_context_file' : offer_context_file,
    'offer_count' : int(offer_count),
    'request_context_file' : request_context_file,
    'request_count' : int(request_count),
    'service_host' : service_host,
}

instance_file = pc_jupyter.instantiate_notebook_from_template('exchange', 'exchange_create', parameters)   
ip_display.display(ip_display.Markdown('[Exchange]({})'.format(instance_file)))
