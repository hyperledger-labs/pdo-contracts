# Copyright 2022 Intel Corporation
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

import importlib
import json
import logging

import pdo.common.crypto as crypto
from pdo.contract import ContractCode
from pdo.contract import invocation_request
from pdo.submitter.create import create_submitter

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.exchange.plugins.asset_type as asset_type
import pdo.exchange.plugins.vetting as vetting
import pdo.exchange.plugins.guardian as guardian

__all__ = [
    'op_initialize',
    'op_mint_token_object',
    'op_provision_token_object',
    'op_get_asset_type_identifier',
    'op_approve_issuer',
    'op_get_issuer_authority',
    'op_get_ledger_key',
    'op_get_contract_metadata',
    'op_get_contract_code_metadata',
    'op_add_endpoint',
    'op_get_verifying_key',
    'cmd_create_token_issuer',
    'do_token_issuer',
    'do_token_issuer_contract',
    'load_commands',
]

op_get_asset_type_identifier = asset_type.op_get_asset_type_identifier
op_approve_issuer = vetting.op_approve_issuer
op_get_issuer_authority = vetting.op_get_issuer_authority
op_get_ledger_key = common.op_get_ledger_key
op_get_contract_metadata = common.op_get_contract_metadata
op_get_contract_code_metadata = common.op_get_contract_code_metadata
op_add_endpoint = common.op_add_endpoint
op_get_verifying_key = common.op_get_verifying_key

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--authority',
            help='serialized authority from the vetting organization',
            type=pbuilder.invocation_parameter, required=True)
        ch_action = subparser.add_mutually_exclusive_group(required=True)
        ch_action.add_argument(
            '-c', '--code-hash',
            help="token object code hash",
            type=pbuilder.invocation_parameter)
        ch_action.add_argument(
            '-t', '--token-object-code',
            help="token object contract code to be used to compute code hash",
            nargs=2, type=str)
        subparser.add_argument(
            '-d', '--description',
            help="description of the digital asset associated with the token objects",
            type=str, required=True)
        subparser.add_argument(
            '--metadata',
            help="metadata that will be attached to the token object",
            type=pbuilder.invocation_parameter, default={}, required=False)
        subparser.add_argument(
            '-i', '--initialization-package',
            help="the token issuer initialization package from the guardian",
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-l', '--ledger-key',
            help='ledger verifying key',
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-m', '--max-count',
            help="maximum number of token objects that can be generated",
            type=int, required=True)

    @classmethod
    def invoke(
            cls, state, session_params, authority, code_hash,
            token_object_code, description, initialization_package,
            ledger_key, max_count, **kwargs) :
        session_params['commit'] = True

        params = {}
        params['token_description'] = description
        params['token_metadata'] = kwargs.get('metadata', {})
        params['maximum_token_count'] = max_count
        params['ledger_verifying_key'] = ledger_key
        params['initialization_package'] = initialization_package
        params['asset_authority_chain'] = authority

        if code_hash :
            params['token_object_code_hash'] = code_hash
        else :
            source_path = state.get(['Contract', 'SourceSearchPath'])
            (contract_class, contract_source) = token_object_code
            contract_code = ContractCode.create_from_file(
                contract_class, contract_source, source_path, interpreter='wawaka')

            message = contract_code.code + contract_code.name
            code_hash = crypto.compute_message_hash(crypto.string_to_byte_array(message))
            params['token_object_code_hash'] = crypto.byte_array_to_base64(code_hash)

        message = invocation_request('initialize', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result
## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_mint_token_object(pcontract.contract_op_base) :

    name = "mint_token_object"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, contract_id, **kwargs) :
        session_params['commit'] = True

        params = {}
        params['contract_id'] = contract_id

        message = invocation_request('mint_token_object', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result
## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_provision_token_object(pcontract.contract_op_base) :

    name = "provision_token_object"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)
        subparser.add_argument(
            '-l', '--ledger-attestation',
            help='attestation from the ledger that the current state of the token issuer is committed',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, contract_id, ledger_attestation, **kwargs) :
        session_params['commit'] = False

        params = {}
        params['ledger_signature'] = ledger_attestation
        params['contract_id'] = contract_id

        message = invocation_request('provision_minted_token_object', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result


# -----------------------------------------------------------------
# create the token issuer
# -----------------------------------------------------------------
class cmd_create_token_issuer(pcommand.contract_command_base) :
    name = "create"
    help = "create token issuer contract object"

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

        # create the contract
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'token_issuer', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)
        contract_object = pcontract_cmd.get_contract(state, save_file)

        # get all the information necessary to register this contract as an endpoint with the guardian
        ledger_submitter = create_submitter(state.get(['Ledger']))
        ledger_key = ledger_submitter.get_ledger_info()
        ledger_attestation = ledger_submitter.get_contract_info(contract_object.contract_id)

        contract_metadata = pcontract.invoke_contract_op(
            common.op_get_contract_metadata,
            state, context, session,
            **kwargs)
        contract_metadata = json.loads(contract_metadata)
        verifying_key = contract_metadata['verifying_key']

        code_metadata = pcontract.invoke_contract_op(
            common.op_get_contract_code_metadata,
            state, context, session,
            **kwargs)
        code_metadata = json.loads(code_metadata)

        guardian_context = context.get_context('guardian_context')

        provisioning_package = pcommand.invoke_contract_cmd(
            guardian.cmd_provision_token_issuer,
            state, guardian_context,
            contract_object.contract_id,
            ledger_attestation,
            contract_metadata,
            code_metadata,
            **kwargs)

        vetting_context = context.get_context('vetting_context')
        vetting_save_file = pcontract_cmd.get_contract_from_context(state, vetting_context)
        if not vetting_save_file :
            vetting_save_file = pcommand.invoke_contract_cmd(
                vetting.cmd_create_vetting_organization,
                state, vetting_context,
                **kwargs)
        vetting_session = pbuilder.SessionParameters(save_file=vetting_save_file)

        pcommand.invoke_contract_cmd(
            vetting.cmd_approve_issuer,
            state, vetting_context,
            verifying_key=verifying_key,
            **kwargs)

        to_context = context.get_context('token_object_context')
        to_contract_source = to_context['source']
        to_contract_class = 'token_object'

        # get the approved authority from the vetting organization
        authority = pcontract.invoke_contract_op(
            vetting.op_get_issuer_authority,
            state, vetting_context, vetting_session,
            contract_metadata['verifying_key'],
            **kwargs)
        authority = json.loads(authority)

        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            authority,
            None, (to_contract_class, to_contract_source),
            context['description'],
            provisioning_package,
            ledger_key,
            context['count'],
            metadata=context.get('token_metadata', {}),
            **kwargs)

        cls.display('created issuer in {}'.format(save_file))
        return save_file

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_mint_token_object,
    op_provision_token_object,
    op_get_asset_type_identifier,
    op_approve_issuer,
    op_get_issuer_authority,
    op_get_ledger_key,
    op_get_contract_metadata,
    op_get_contract_code_metadata,
    op_add_endpoint,
    op_get_verifying_key,
]

do_token_issuer_contract = pcontract.create_shell_command('token_issuer_contract', __operations__)

__commands__ = [
    cmd_create_token_issuer,
]

do_token_issuer = pcommand.create_shell_command('token_issuer', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'token_issuer', do_token_issuer)
    pshell.bind_shell_command(cmdclass, 'token_issuer_contract', do_token_issuer_contract)
