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

# %% [markdown]
# # Token Family Factory
#
# This notebook simplifies the creation of an instance of a token issuer. Update the token configuration information then evaluate the notebook to create a new token issuer. That token issuer will be able to mint tokens.

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_contract_families(exchange='ex')
pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ## Configure Token Information
#
# This section enables customization of the token that will be minted. Edit the variables in the section below as necessary.
#
# * identity : the identity of the token creator
# * token_class : the name of tokens that will be generated
#
# Note that the notebook assumes that there is a key file for the identity of the form: `${keys}/${identity}_private.pem`.

# %% tags=["parameters"]
identity = input('Identity of the token issuer: ')
token_class = input('Name of the class of tokens to issue: ')
token_description = input('Description of the token [my token]') or 'my token'
count = input('Number of tokens to mint [5] ') or 5
service_group = input('Service group [default]: ') or "default"

# %% [markdown]
# ## Create the Token Issuer Notebook
#
# Create a new token issuer notebook with the specific token identified.
#

# %%
instance_parameters = {
    'token_owner' : identity,
    'token_class' : token_class,
    'token_description' : token_description,
    'count' : int(count),
    'service_group' : service_group,
}

instance_file = pc_jupyter.instantiate_notebook_from_template(token_class, 'token_issuer', instance_parameters)
ip_display.display(ip_display.Markdown('[Token Issuer]({})'.format(instance_file)))
