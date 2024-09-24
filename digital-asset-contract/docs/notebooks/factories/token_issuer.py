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
# This notebook simplifies the creation of an instance of a token issuer for a digital asset (in
# this case assets are 24bit bmp images). Update the token configuration information then evaluate
# the notebook to create a new token issuer. That token issuer will be able to mint tokens.

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
# ## Configure Token Information
#
# This section enables customization of the token that will be minted. The two main tabs on the form
# allow specification of the token properties and the configuration of the services used for the
# token contracts.
#
# The token properties include:
# * Token Class: the unique name for the token class
# * Token Description: text description of the token
# * Count: number of tokens to create for the asset
# * Image File: the image file, at the moment this must be a 24-bit BMP file
# * Privacy Border: a band of pixels that will never be exposed to verify authenticity
#
# The service properties include:
# * Identity: the identity of the token creator
# * Service Groups: information about the service groups to use for contract execution
#
# Use the key manager and groups manager to configure additional identities or services.

# %%
ip_display.display(pc_jupyter.da_jupyter.DigitalAssetIssuerWidget(state, bindings))
