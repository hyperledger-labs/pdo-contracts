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
# # Exchange Import Factory
#
# Use this notebook to import an exchange of assets from two issuers.

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
# * exchange_import_file : the name of the contract import file for an existing exchange
# * exchange_context_file : the name of the context file to use for the exchange contract
#
# Note that the notebook assumes that there is a key file for the identity of the form: `${keys}/${identity}_private.pem`.

# %% editable=true slideshow={"slide_type": ""}
identity = input('Identity to use with the exchange: ')
exchange_import_file = input('Name of the exchange import file: ')
exchange_context_file = input('Name of the file to use for the context: ')

# %% [markdown] editable=true slideshow={"slide_type": ""}
# ## Create the Exchange Notebook
#
# Create a new exchange notebook with the specific issuers identified.

# %% editable=true slideshow={"slide_type": ""}
parameters = {
    'identity' : identity,
    'exchange_import_file' : exchange_import_file,
    'exchange_context_file' : exchange_context_file,
}

instance_file = pc_jupyter.instantiate_notebook_from_template('exchange', 'exchange_import', parameters)   
ip_display.display(ip_display.Markdown('[Exchange]({})'.format(instance_file)))
