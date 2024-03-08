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
# # Issuer Factory
#
# Use this notebook to create an issuer notebook that can be used to issue assets to users.

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ## Configure Issuer Information
#
# This section enables customization of the token that will be minted. Edit the variables in the section below as necessary.
#
# * identity : the identity of the token creator
# * token_class : the name of tokens that will be generated
#
# Note that the notebook assumes that there is a key file for the identity of the form: `${keys}/${identity}_private.pem`.

# %% editable=true slideshow={"slide_type": ""}
identity = input('Identity of the issuer: ')
asset_name = input('Name of the asset:')
asset_description = input('Description of the asset: ')
asset_link = input('Link to more information about the asset [http://]: ') or 'http://'
service_host = input('Service host [localhost]: ') or 'localhost'

# %% [markdown]
# ## Create the Issuer Notebook
#
# Create a new issuer notebook with the specific asset identified.

# %%
parameters = {
    'identity' : identity,
    'asset_name' : asset_name,
    'asset_description' : asset_description,
    'asset_link' : asset_link,
    'service_host' : service_host,
}

instance_file = pc_jupyter.instantiate_notebook_from_template(asset_name, 'issuer', parameters)   
ip_display.display(ip_display.Markdown('[Issuer]({})'.format(instance_file)))
