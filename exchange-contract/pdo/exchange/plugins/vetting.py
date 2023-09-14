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

import json
import logging

from pdo.contract import invocation_request

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.exchange.plugins.asset_type as asset_type

__all__ = [
    'op_initialize',
    'op_approve_issuer',
    'op_get_issuer_authority',
    'cmd_create_vetting_organization',
    'cmd_approve_issuer',
    'do_vetting',
    'do_vetting_contract',
    'load_commands',
]

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## inherited operations
## -----------------------------------------------------------------
op_get_verifying_key = common.op_get_verifying_key
op_get_asset_type_identifier = asset_type.op_get_asset_type_identifier

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize an asset type contract object"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-t', '--type_id',
            help='contract identifier for the issuer asset type',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, type_id, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('initialize', asset_type_identifier=type_id)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_approve_issuer(pcontract.contract_op_base) :

    name = "approve_issuer"
    help = "record approval of a specific issuer"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-i', '--issuer',
            help='identity of the issuer contract object; ECDSA verifying key',
            type=pbuilder.invocation_parameter, required=True)


    @classmethod
    def invoke(cls, state, session_params, issuer, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('add_approved_issuer', issuer_verifying_key=issuer)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_issuer_authority(pcontract.contract_op_base) :

    name = "get_issuer_authority"
    help = "get the verifiable authority that is assigned to an approved issuer"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-i', '--issuer',
            help='identity of the issuer contract object; ECDSA verifying key',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, issuer, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('get_issuer_authority', issuer_verifying_key=issuer)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# create a vetting organization
# -----------------------------------------------------------------
class cmd_create_vetting_organization(pcommand.contract_command_base) :
    name = "create"
    help = "script to create a vetting organization contract object"

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

        # get a link to the asset type contract
        asset_type_context = context.get_context('asset_type_context')
        asset_type_save_file = pcontract_cmd.get_contract_from_context(state, asset_type_context)

        if not asset_type_save_file :
            asset_type_save_file = pcommand.invoke_contract_cmd(
                asset_type.cmd_create_asset_type,
                state, asset_type_context,
                **kwargs)

        asset_type_session = pbuilder.SessionParameters(save_file=asset_type_save_file)
        asset_type_id = pcontract.invoke_contract_op(
            asset_type.op_get_asset_type_identifier,
            state, asset_type_context, asset_type_session,
            **kwargs)
        asset_type_id = json.loads(asset_type_id)

        # create the vetting organization type
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'vetting', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            asset_type_id,
            **kwargs)

        cls.display('created vetting organization in {}'.format(save_file))
        return save_file

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_approve_issuer(pcommand.contract_command_base) :
    """Vetting organization approves an issuer
    """

    name = "approve_issuer"
    help = "request vetting organization approval for an issuer contract object"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument('--issuer', help='context label for issuer contract', type=str)
        parser.add_argument('--verifying-key', help='verifying key for issuer contract', type=pbuilder.invocation_parameter)

    @classmethod
    def invoke(cls, state, context, verifying_key=None, issuer=None, **kwargs) :
        # the approval needs to be given by the vetting identity, this works easily
        # when the vetting & issuer identities are the same; it will require separate
        # approval when vetting is not issuer

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            save_file = pcommand.invoke_contract_cmd(
                cmd_create_vetting_organization,
                state, context,
                **kwargs)

        if verifying_key is None :
            if issuer is None :
                raise ValueError("missing required parameter for verifying key")

            issuer_context = state.get(['context'] + issuer.split('.'))
            if issuer_context is None :
                raise ValueError("no such context, {}".format(issuer_context))

            verifying_key = issuer_context.get('verifying_key')
            if verifying_key is None :
                issuer_save_file = pcontract_cmd.get_contract_from_context(issuer_context)
                if not issuer_save_file :
                    raise ValueError('issuer contract not created')

                issuer_session = pbuilder.SessionParameters(save_file=issuer_save_file)
                verifying_key = pcontract.invoke_contract_op(
                    common.op_get_verifying_key,
                    state, issuer_context, issuer_session,
                    **kwargs)
                verifying_key = json.loads(verifying_key)

                raise ValueError("missing required parameter 'verifying_key'")

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_approve_issuer,
            state, context, session,
            verifying_key,
            **kwargs)

        return save_file

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_approve_issuer,
    op_get_issuer_authority,
    asset_type.op_get_asset_type_identifier,
    common.op_get_verifying_key,
]

do_vetting_contract = pcontract.create_shell_command('vetting_contract', __operations__)

__commands__ = [
    cmd_create_vetting_organization,
    cmd_approve_issuer,
]

do_vetting = pcommand.create_shell_command('vetting', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'vetting', do_vetting)
    pshell.bind_shell_command(cmdclass, 'vetting_contract', do_vetting_contract)
