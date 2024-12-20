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
# # Notebook to Invoke Counter Operations

# %% [markdown]
# ## Configure Counter Information
#
# %% tags=["parameters"]
counter_owner = 'user1'
counter_name = 'counter_1'
service_group = 'default'
instance_identifier = ''

# %% [markdown]
# <hr style="border:2px solid gray">
#
# ## Initialize

# %%
import os
import pdo.contracts.jupyter as pc_jupyter

pc_jupyter.load_contract_families(exchange='ex', example='example')
pc_jupyter.load_ipython_extension(get_ipython())

# %% [markdown]
# ### Initialize the PDO Environment
#
# Initialize the PDO environment. This assumes that a functional PDO configuration is in place and
# that the PDO virtual environment has been activated.
#
# For the most part, no modifications should be required below.
# %%
common_bindings = {
    'counter_owner' : counter_owner,
    'counter_name' : counter_name,
    'instance' : instance_identifier,
}

try : state
except NameError :
    (state, bindings) = pc_jupyter.initialize_environment(counter_owner, **common_bindings)

print('environment initialized')

# %% [markdown]
# ### Initialize the Contract Context
#
# The contract context defines the configuration for a collection of contract objects that interact
# with one another. In the case of the counter contract, there are no interactions and the context
# is very simple.

# %%
context_file = bindings.expand('${etc}/context/${counter_name}_${instance}.toml')
print("using context file {}".format(context_file))

context_bindings = {
    'identity' : counter_owner,
    'service_group' : service_group,
}

counter_path = 'counter.' + counter_name
context = pc_jupyter.example_jupyter.initialize_counter_context(
    state, bindings, context_file, counter_path, **context_bindings)
print('context initialized')

counter_context = pc_jupyter.pbuilder.Context(state, counter_path + '.counter')
counter_save_file = pc_jupyter.pcommand.invoke_contract_cmd(
    pc_jupyter.example_counter.cmd_create_counter, state, counter_context)
pc_jupyter.pbuilder.Context.SaveContextFile(state, context_file, prefix=counter_path)
print('saved counter contract in {}'.format(counter_save_file))

# %% [markdown]
# <hr style="border:2px solid gray">
# ## Operate on the Counter
#

# %% [markdown]
# ### Get Counter Value
#
# %%
def get_counter_value() :
    return pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.example_counter.cmd_get_value, state, counter_context)
# %%
# %%skip True
print("The current value of the counter is {}".format(get_counter_value()))

# %% [markdown]
# ### Increment the Counter Value
#
# %%
def inc_counter_value() :
    return pc_jupyter.pcommand.invoke_contract_cmd(
        pc_jupyter.example_counter.cmd_inc_value, state, counter_context)
# %%
# %%skip True
inc_counter_value()
print("The current value of the counter is {}".format(get_counter_value()))
