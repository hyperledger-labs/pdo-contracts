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
# # Notebook to Invoke Token Operations

# %% [markdown]
# ## Configure Token Information
#
# This section enables customization of the token. Edit the variables in the section below as necessary.
# * token_owner : the identity of the token owner
# * token_class : the name of the class of tokens that was minted
# * token_name : the name of the specific token that was minted
# * token_path : the full context path to the token
# * context_file : the name of the context file where token information is located
#
# Note that the notebook assumes that there is a key file for the identity of the form
#
# ```bash
# ${keys}/${identity}_private.pem
# ```
#

# %% editable=true slideshow={"slide_type": ""} tags=["parameters"]
token_owner = 'user1'
token_class = 'mytoken'
token_name = 'token_1'
token_path = 'token.${token_class}.token_object.${token_name}'
context_file = '${etc}/${token_class}_context.toml'
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
# Initialize the PDO environment. This assumes that a functional PDO configuration is in place and that the PDO virtual environment has been activated. In particular, ensure that the groups file and eservice database have been configured correctly. This can be done most easily by running the following in a shell:
#
# `$PDO_HOME/bin/pdo-create-service-groups.psh --service_host <service_host>`
#
# For the most part, no modifications should be required below.

# %% editable=true slideshow={"slide_type": ""}
common_bindings = {
    'host' : service_host,
    'service_host' : service_host,
    'token_owner' : token_owner,
    'token_class' : token_class,
    'token_name' : token_name,
}

(state, bindings) = pc_jupyter.initialize_environment(token_owner, **common_bindings)
print('environment initialized')

# %% [markdown] editable=true slideshow={"slide_type": ""}
# ### Initialize the Contract Context
#
# The contract context defines the configuration for a collection of contract objects that interact with one another. By default, the context file used in this notebook is specific to the toke class used to mint the token. We need the class to ensure that all of the information necessary for the token itself is availablen. If you prefer to use a common context file, edit the context_file variable below.
#
# For the most part, no other modifications should be required.

# %% editable=true slideshow={"slide_type": ""}
token_class_path = 'token.' + token_class
context_file = bindings.expand(context_file)
print("using context file {}".format(context_file))

context = pc_jupyter.ex_jupyter.initialize_token_context(state, bindings, context_file, token_class_path)
print('context initialized')

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Operate on the Contract

# %% editable=true slideshow={"slide_type": ""}
token_context = pc_jupyter.pbuilder.Context(state, token_path)

# %% [markdown]
# ### Invoke Echo Operation

# %%
# %%skip True
message = 'hello from token {}'.format(token_path)
echo_result = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ex_token_object.cmd_echo, state, token_context, message=message)

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Contract Metadata

# %% [markdown]
# ### Export Contract File
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
# %%skip True
export_file = '${{data}}/{}.zip'.format(token_class)

contexts = ['asset_type', 'vetting', 'guardian', 'token_issuer', 'token_object']
pc_jupyter.export_context_file(state, bindings, context, contexts, export_file)

# %% [markdown]
# ### Contract Save Files

# %%
# %%skip True
contract_files = {
    'token' : token_context.get('save_file'),
}

for k, f in contract_files.items() :
    ip_display.display(ip_display.JSON(root=k, filename=os.path.join(bindings.expand('${save}'), f)))

# %% [markdown]
# ### Contract Context

# %%
# %%skip True
# ip_display.display(ip_display.JSON(data=context.context, root='context'))
ip_display.display(context.context)
