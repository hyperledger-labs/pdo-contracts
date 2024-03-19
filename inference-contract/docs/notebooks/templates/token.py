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

# %% tags=["parameters"]
token_owner = 'user1'
token_class = 'mytoken'
token_name = 'token_1'
token_path = 'token.${token_class}.token_object.${token_name}'
context_file = '${etc}/${token_class}_context.toml'
service_host = 'localhost'
instance_identifier = ''

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
This can be done most easily by running the following in a shell:
#
# `$PDO_HOME/bin/pdo-create-service-groups.psh --service_host <service_host>`
#
# For the most part, no modifications should be required below.

# %%
common_bindings = {
    'host' : service_host,
    'service_host' : service_host,
    'token_owner' : token_owner,
    'token_class' : token_class,
    'token_name' : token_name,
}

(state, bindings) = pc_jupyter.initialize_environment(token_owner, **common_bindings)
print('environment initialized')

# %% [markdown]
# ### Initialize the Contract Context
#
# The contract context defines the configuration for a collection of contract
# objects that interact with one another. By default, the context file used in
# this notebook is specific to the toke class used to mint the token.
# We need the class to ensure that all of the information necessary for the token
# itself is available. If you prefer to use a common context file, edit the
# context_file variable below.
#
# For the most part, no other modifications should be required.

# %%
token_class_path = 'token.' + token_class
context_file = bindings.expand(context_file)
print("using context file {}".format(context_file))

context = pc_jupyter.ml_jupyter.initialize_token_context(state, bindings, context_file, token_class_path)
print('context initialized')

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Operate on the Contract

# %%
token_context = pc_jupyter.pbuilder.Context(state, token_path)


# %% [markdown]
# ### Invoke Inference Operation
#
# The model is an image classfication model. Use the following cell to
# provide input to the classification oepration. Current token object policy
# simply checks ownership of the token. There are no additional policy checks
# in this example.
#
# For the parameters to be provided below, if you are running the jupyter server
# via the contracts docker container, copy your test image to
# `$PDO_CONTRACTS_SRC_ROOT/docker/xfer/client/` folder and
# provide the value `/project/pdo/xfer/client` for the input `path`.
#
# Also, please note that `$PDO_CONTRACTS_SRC_ROOT/inference-contract/data` folder
# contains the sample image `zebra_wiki.jpg` that may be used for testing

# %% tags=["parameters"]
image_name = input('Name of the image file')
path = input('Path on disk where the image is located')


# %%
inference_result = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ml_inference_token_object.cmd_do_inference,
    state, token_context, image=image_name, search_path=[path])


# %% [markdown]
# ### Transfer Ownership to a New User
#
# User1 now transfers ownership of the token object (and hence its capabilities)
# to a new user. Note that the notebook assumes that user1 knows the public key
# of the new user, and is located at  `${keys}/`.

# %% tags=["parameters"]
new_user_identity = input('Name of the new User')


# %%
pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ml_inference_token_object.cmd_transfer_assets,
    state, token_context, new_owner=new_user_identity)

# %% [markdown]
# ### Test Ownership
#
# Let's ensure that user1 can no longer perform operations on the asset.
# The following asset usage command should fail:

# %%
inference_result = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ml_inference_token_object.cmd_do_inference,
    state, token_context, image=image_name, search_path=[path])

# %% [markdown]
# ### New User Performs Operations on the Asset
#
# Let's also ensure that user2 can indeed perform operations on the asset.
# Note that in the following command, we explicitly pass the identity of the caller

# %%
inference_result = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ml_inference_token_object.cmd_do_inference,
    state, token_context, image=image_name, search_path=[path], identity='user2')

# %% [markdown]
# ### Onwership Transfer Is Still Possible, But now done by user2!
#
# User2 is the current owner of the token, and can transfer asset-usage rights to
# a third person, say user3.

# %%
current_owner_identity = new_user_identity #user2
new_user_identity = 'user3'
pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.ml_inference_token_object.cmd_transfer_assets,
    state, token_context, identity = current_owner_identity, new_owner=new_user_identity)
