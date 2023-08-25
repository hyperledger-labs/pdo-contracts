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

__all__ = [
    'op_initialize',
    'op_get_asset_type_identifier',
    'op_describe',
    'cmd_create_asset_type',
    'do_asset_type_contract',
    'do_asset_type',
    'load_commands',
]

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize an asset type contract object"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument('-d', '--description', help='human readable description', type=str, default='')
        subparser.add_argument('-n', '--name', help='human readable name', type=str, default='')
        subparser.add_argument('-l', '--link', help='URL where more information is located', type=str, default='')

    @classmethod
    def invoke(cls, state, session_params, description, name, link, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('initialize', name=name, description=description, link=link)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_asset_type_identifier(pcontract.contract_op_base) :
    name = "get_asset_type_identifier"
    help = "return the unique identifier for the asset type"

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False
        message = invocation_request('get_asset_type_identifier')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_describe(pcontract.contract_op_base) :
    name = "describe"
    help = "retrieve the descriptive information for the type"

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('get_name')
        name = pcontract_cmd.send_to_contract(state, message, **session_params)

        message = invocation_request('get_description')
        description = pcontract_cmd.send_to_contract(state, message, **session_params)

        message = invocation_request('get_link')
        link = pcontract_cmd.send_to_contract(state, message, **session_params)

        cls.display("NAME: {0}".format(name))
        cls.display("DESC: {0}".format(description))
        cls.display("LINK: {0}".format(link))

        return True

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_create_asset_type(pcommand.contract_command_base) :
    name = "create"
    help = "script to create an asset type"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument('-c', '--contract-class', help='Name of the contract class', type=str)
        subparser.add_argument('-e', '--eservice-group', help='Name of the enclave service group to use', type=str)
        subparser.add_argument('-f', '--save-file', help='File where contract data is stored', type=str)
        subparser.add_argument('-p', '--pservice-group', help='Name of the provisioning service group to use', type=str)
        subparser.add_argument('-r', '--sservice-group', help='Name of the storage service group to use', type=str)
        subparser.add_argument('--source', help='File that contains contract source code', type=str)
        subparser.add_argument('--extra', help='Extra data associated with the contract file', nargs=2, action='append')

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if save_file :
            return save_file

        # create the asset type contract
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'asset_type', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            context['name'],
            context['description'],
            context['link'],
            **kwargs)

        cls.display('created asset type in {}'.format(save_file))
        return save_file

## -----------------------------------------------------------------
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_get_asset_type_identifier,
    op_describe,
]

do_asset_type_contract = pcontract.create_shell_command('asset_type_contract', __operations__)

__commands__ = [
    cmd_create_asset_type,
]

do_asset_type = pcommand.create_shell_command('asset_type', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'asset_type', do_asset_type)
    pshell.bind_shell_command(cmdclass, 'asset_type_contract', do_asset_type_contract)
