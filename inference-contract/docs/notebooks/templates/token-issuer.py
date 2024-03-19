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
# # Token Issuer Notebook
# This section enables customization of the token that will be minted. Edit the variables in the section below as necessary. 
#
# identity : the identity of the token creator
# service_host : the host for the eservice where tokens will be minted, this will use the default service group
# token_class : the name of tokens that will be generated, this is only used to simplify local access (e.g. context file name)
# token_description : a description of the asset associated with the minted tokens
# token_metadata : additional information about the token
# count : the number of tokens to mint for the asset

# Note that the notebook assumes that there is a key file for the identity of the form: `${keys}/${identity}_private.pem`.


# %% tags=["parameters"]
token_owner = 'user1'
token_class = 'mytoken'
token_description = 'this is my token'
token_metadata = 'created by {}'.format(token_owner)
count = 1
service_host = 'localhost'
instance_identifier = ''

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Initialize

# %%
import os
import pdo.contracts.jupyter as pc_jupyter
import IPython.display as ip_display

pc_jupyter.load_ipython_extension(get_ipython())


# %% [markdown]
# ### Initialize the PDO Environment
#
# Initialize the PDO environment. This assumes that a functional PDO configuration
# is in place and that the PDO virtual environment has been activated. In particular, 
# ensure that the groups file and eservice database have been configured correctly. 
# If you do not have a service groups configuration, you can create it for a single
# service host by running the following:

# %%
# %%skip True
# %%bash -s $service_host
if [ ! -f $PDO_HOME/etc/$1_groups.toml ] ; then
    $PDO_INSTALL_ROOT/bin/pdo-shell $PDO_HOME/bin/pdo-create-service-groups.psh --service_host $1
fi


# %% [markdown]
# For the most part, no modifications should be require below.

# %%
common_bindings = {
    'host' : service_host,
    'service_host' : service_host,
    'token_owner' : token_owner,
    'token_class' : token_class,
}

(state, bindings) = pc_jupyter.initialize_environment(token_owner, **common_bindings)
print('environment initialized')

# %% [markdown]
# ### Initialize the Contract Context
#
# The contract context defines the configuration for a collection of contract objects
# that interact with one another. By default, the context file used in this notebook 
# is specific to the token. If you prefer to use a common context file, edit the 
# `context_file` variable below.
#
# For the most part, no other modifications should be required.

# %%
token_path = 'token.' + token_class
context_file = bindings.expand('${etc}/${token_class}_context.toml')
print("using context file {}".format(context_file))

context_bindings = {
    'asset_type.identity' : token_owner,
    'vetting.identity' : token_owner,
    'guardian.identity' : token_owner,
    'token_issuer.identity' : token_owner,
    'token_issuer.count' : count,
    'token_issuer.description' : token_description,
    'token_issuer.token_metadata.opaque' : token_metadata,
    'token_object.identity' : token_owner,
    'guardian.url' : 'http://' + service_host + ':7900'
}

context = pc_jupyter.ml_jupyter.initialize_token_context(state, bindings, context_file, token_path, **context_bindings)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=token_path)
print('context initialized')


# %% [markdown]
# ### Create the Token Issuer Contract
#
# The process of creating the token issuer will also create an asset type contract object, 
# a vetting organization contract object, and the guardian contract object. 
# The asset type and vetting organization contract objects are principally used 
# to complete the canonical asset interface that enables transparent value exchanges 
# with tokens and other digital assets.

# %%
token_issuer_context = pc_jupyter.pbuilder.Context(state, token_path + '.token_issuer')
token_issuer_save_file = token_issuer_context.get('save_file')
if not token_issuer_save_file :
    token_issuer_save_file = pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.ex_token_issuer.cmd_create_token_issuer, state, token_issuer_context)
    pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=token_path)
print('token issuer contract in {}'.format(token_issuer_save_file))


# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Operate on the Contract

# %% [markdown]
# ### Mint the Tokens

# %%
token_object_context = pc_jupyter.pbuilder.Context(state, token_path + '.token_object')

minted_token_save_files = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ml_inference_token_object.cmd_mint_tokens, state, token_object_context)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=token_path)

minted_token_contexts = []
for token_index in range(1, len(minted_token_save_files)+1) :
    minted_token_contexts += [ token_object_context.get_context('token_{}'.format(token_index)) ]

print("{} tokens minted".format(len(minted_token_save_files)))




# %% [markdown]
# ### Create Token Notebooks
#
# Create a token notebook for each of the minted tokens.

# %%
# %%skip True

parameters = {
    'token_owner' : token_owner,
    'token_class' : token_class,
    'context_file' : context_file,
    'service_host' : service_host,
}

for token_context in minted_token_contexts :
    parameters['token_path'] = token_context.path
    parameters['token_name'] = token_context.path.split('.')[-1]

    instance_file = pc_jupyter.instantiate_notebook_from_template(token_class, 'token', parameters)
    ip_display.display(ip_display.Markdown('[Token {}]({})'.format(parameters['token_name'], instance_file)))


# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Share Contract
#
# To share a contract with others, they need the client plugin modules,
# the context of the contract family (which describes the relationship between
# the contract objects), and the contract save files (which provides information
# about the configuration of the contract objects). Plugins are generally
# distributed separately (they are applicable to many contract objects). The
# context and contract save files can be packed into a single bundle that
# can easily be shared.
#
# In the code block below, you will likely want to change the value of the export
# path to the directory where the contract family export file will be saved. Feel
# free to change the file name as well. The default uses the asset name.

# %%
contract_identifier = '{}_{}'.format(token_class, instance_identifier)
contexts = ['asset_type', 'vetting', 'guardian', 'token_issuer', 'token_object']
contract_files = {
    'asset_type' : context.get('asset_type.save_file'),
    'vetting' : context.get('vetting.save_file'),
    'token_issuer' : token_issuer_context.get('save_file'),
}

# %%
# %%skip True
export_file = pc_jupyter.export_contract_collection(state, bindings, context, contexts, contract_identifier)
ip_display.display(pc_jupyter.create_download_link(export_file, 'Download Contract Collection File'))

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Contract Metadata
#
# The cells below provide a means inspecting information about the contract. In general
# this is useful for contract debugging.

# %% [markdown]
# ### Contract Save Files

# %% tags=["hide-input"]
# %%skip True
for k, f in contract_files.items() :
    ip_display.display(ip_display.JSON(root=k, filename=os.path.join(bindings.expand('${save}'), f)))

# %% [markdown]
# ### Contract Context

# %% tags=["hide-input"]
# %%skip True
ip_display.display(context.context)
