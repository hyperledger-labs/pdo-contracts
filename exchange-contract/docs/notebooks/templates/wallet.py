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
# # Wallet Notebook
#
# This notebook is used to manage the assets issued to an indivdual by an issuer contract. The
# notebook assumes that the asset type, vetting, and issuer contract objects have been created.

# %% [markdown] editable=true slideshow={"slide_type": ""}
# <hr style="border:2px solid gray">
#
# ## Configure Wallet Information
#
# This section enables customization of the wallet. Edit the variables in the section below as
# necessary. These may be assigned through the factory interface.
# * wallet_owner : the identity of the wallet owner, default identity for assets
# * wallet_name : a name for customizing the wallet
# * context_file : the name of the context file where asset information is located
# %% tags=["parameters"]
wallet_owner = 'user1'
wallet_name = 'wallet'
context_file = '${etc}/${wallet_name}_context.toml'
instance_identifier = ''

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Initialize
# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display
import ipywidgets

pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ### Initialize the PDO Environment
#
# Initialize the PDO environment. This assumes that a functional PDO configuration is in place and
# that the PDO virtual environment has been activated. In particular, ensure that the groups file
# and eservice database have been configured correctly.  If you do not have a service groups
# configuration, you can set it up with the
# [service groups manager](/documents/service_groups_manager.ipynb) page
# %%
try : state
except NameError:
    common_bindings = {
        'wallet_owner' : wallet_owner,
        'wallet_name' : wallet_name,
        'instance' : instance_identifier,
    }

    (state, bindings) = pc_jupyter.initialize_environment(wallet_owner, **common_bindings)

print('environment initialized')

# %% [markdown]
# ### Initialize the Wallet Context
#
# The wallet context defines the configuration for a collection of contract objects that interact
# with one another.
# %%
wallet_path = 'wallet.{}'.format(wallet_name)
context_file = bindings.expand(context_file)

context_bindings = {
    'identity' : wallet_owner,
}

context = pc_jupyter.common.initialize_context(state, bindings, context_file, wallet_path, [], **context_bindings)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=wallet_path)

print('context initialized')

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Operate on the Issuer Contract
#
# This section defines several functions that can be used to interact with the wallet:
# * import issuers -- add asset handles to the wallet
# * account balance -- list the asset balances for each handle stored in the wallet
# * transfer -- transfer assets from one identity to another

# %% [markdown]
# ### Import Asset Issuers
#
# Import asset issuer contract collections and select an identity to use with the issuer.  An asset
# handle is associated with the issuer/identity pair to simpflify other operations.  The handle can
# be any name (alphanumeric string).
#
# Note that the veracity of the imported collections is assumed to be addressed out of
# band. Correctness checks are not a part of the import process.
# %%
import_widget = pc_jupyter.ex_jupyter.ImportIssuerWidget(state, bindings, context_file, wallet_path)
ip_display.display(import_widget)

# %% [markdown]
# ### Account Balance
# %%
balance_widget = pc_jupyter.ex_jupyter.AssetBalanceWidget(state, bindings, wallet_path)
ip_display.display(balance_widget)

# %% [markdown]
# ### Transfer Assets
#
# If necessary, use the [Key Manager Notebook](/documents/key_manager.ipynb) to import or create additional
# keys that can be used for the transfer.
# %%
transfer_widget = pc_jupyter.ex_jupyter.AssetTransferWidget(state, bindings, wallet_path)
ip_display.display(transfer_widget)
