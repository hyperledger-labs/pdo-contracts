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
# *WORK IN PROGRESS*
# # Token Import Factory
#
# Use this notebook to import a token from a contract collection file.

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_contract_families(digital_asset='da', exchange='ex')
pc_jupyter.load_ipython_extension(get_ipython())

try : state
except NameError:
    (state, bindings) = pc_jupyter.initialize_environment('unknown')

# %% [markdown]
# ## Configure Token Contract
#
# This section enables provides details for the token to be imported
#
# * token_owner : the identity of the owner of the token
# * token_class : the name of the token, used to simplify local access
# * token_name : the name of the minted token that will be imported
# * token_import_file : the name of the contract collections file for the token
#
# Note that the notebook assumes that there is a key file for the identity of the form:
# `${keys}/${identity}_private.pem`.

# %%
ip_display.display(pc_jupyter.da_jupyter.DigitalAssetImportWidget(state, bindings))
