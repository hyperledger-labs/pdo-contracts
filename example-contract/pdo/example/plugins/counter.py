# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from pdo.contract import invocation_request

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

logger = logging.getLogger(__name__)

__all__ = [
    'op_inc_value',
    'op_get_value',
    'cmd_create_counter',
    'cmd_inc_value',
    'cmd_get_value',
    'do_example_counter',
    'do_example_counter_contract',
    'load_commands',
]

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
class op_inc_value(pcontract.contract_op_base) :
    name = "inc_value"
    help = "Increment the value of the counter by 1"

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        message = invocation_request('inc_value')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        return result

## -----------------------------------------------------------------
class op_get_value(pcontract.contract_op_base) :
    name = "get_value"
    help = "Get the current value of the counter"

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        message = invocation_request('get_value')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        return result

# -----------------------------------------------------------------
# create a counter
# -----------------------------------------------------------------
class cmd_create_counter(pcommand.contract_command_base) :
    """Create a counter
    """
    name = "create"
    help = "create a counter"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument('-c', '--contract-class', help='Name of the contract class', type=str)
        parser.add_argument('-e', '--eservice-group', help='Name of the enclave service group to use', type=str)
        parser.add_argument('-f', '--save-file', help='File where contract data is stored', type=str)
        parser.add_argument('-p', '--pservice-group', help='Name of the provisioning service group to use', type=str)
        parser.add_argument('-r', '--sservice-group', help='Name of the storage service group to use', type=str)
        parser.add_argument('--source', help='File that contains contract source code', type=str)
        parser.add_argument('--extra', help='Extra data associated with the contract file', nargs=2, action='append')

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        if pcontract_cmd.get_contract_from_context(state, context) :
            return

        # create the counter contract
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'example_counter', **kwargs)
        context['save_file'] = save_file

        return save_file

# -----------------------------------------------------------------
# increment a counter
# -----------------------------------------------------------------
class cmd_inc_value(pcommand.contract_command_base) :
    """Increment the value of a counter
    """

    name = "inc_value"
    help = "increment the counter"

    @classmethod
    def invoke(cls, state, context, **kwargs) :

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('counter contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_inc_value,
            state, context, session,
            **kwargs)

        cls.display('current value of the counter is {}'.format(result))
        return result

# -----------------------------------------------------------------
# get the value of a counter
# -----------------------------------------------------------------
class cmd_get_value(pcommand.contract_command_base) :
    """Get the value of a counter
    """

    name = "get_value"
    help = "get the current value of the counter"

    @classmethod
    def invoke(cls, state, context, **kwargs) :

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('counter contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_get_value,
            state, context, session,
            **kwargs)

        cls.display('current value of the counter is {}'.format(result))
        return result


## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_inc_value,
    op_get_value,
]

do_example_counter_contract = pcontract.create_shell_command('example_counter_contract', __operations__)

__commands__ = [
    cmd_create_counter,
    cmd_inc_value,
    cmd_get_value,
]

do_example_counter = pcommand.create_shell_command('example_counter', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'example_counter', do_example_counter)
    pshell.bind_shell_command(cmdclass, 'example_counter_contract', do_example_counter_contract)
