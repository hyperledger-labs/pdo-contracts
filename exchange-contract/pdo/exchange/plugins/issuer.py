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

import pdo.common.utility as putils
from pdo.contract import invocation_request

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.exchange.plugins.asset_type as asset_type
import pdo.exchange.plugins.vetting as vetting

__all__ = [
    'op_initialize',
    'op_get_authority',
    'op_get_balance',
    'op_get_entry',
    'op_issue',
    'op_transfer',
    'op_escrow',
    'op_release',
    'op_claim',
    'op_get_asset_type_identifier',
    'op_approve_issuer',
    'op_get_issuer_authority',
    'op_get_verifying_key',
    'cmd_create_issuer',
    'cmd_initialize_issuer',
    'cmd_issue_assets',
    'cmd_get_balance',
    'cmd_transfer_assets',
    'do_issuer',
    'do_issuer_contract',
    'load_commands',
]

op_get_asset_type_identifier = asset_type.op_get_asset_type_identifier
op_approve_issuer = vetting.op_approve_issuer
op_get_issuer_authority = vetting.op_get_issuer_authority
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


    @classmethod
    def invoke(cls, state, session_params, authority, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('initialize', asset_authority_chain=authority)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_authority(pcontract.contract_op_base) :

    name = "get_authority"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('get_authority')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_balance(pcontract.contract_op_base) :

    name = "get_balance"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('get_balance')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_entry(pcontract.contract_op_base) :

    name = "get_entry"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('get_entry')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_issue(pcontract.contract_op_base) :

    name = "issue"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-o', '--owner',
            help='identity of the issuance owner; ECDSA key',
            type=str, required=True)
        subparser.add_argument(
            '-c', '--count',
            help='amount of the issuance',
            type=int, required=True)

    @classmethod
    def invoke(cls, state, session_params, owner, count, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('issue', owner_identity=owner, count=count)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_transfer(pcontract.contract_op_base) :

    name = "transfer"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-n', '--new_owner',
            help='identity of the new owner; ECDSA key',
            type=str, required=True)
        subparser.add_argument(
            '-c', '--count',
            help='amount to transfer',
            type=int, required=True)

    @classmethod
    def invoke(cls, state, session_params, new_owner, count, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('transfer', new_owner_identity=new_owner, count=count)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_escrow(pcontract.contract_op_base) :

    name = "escrow"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--agent',
            help='identity of the escrow agent',
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-c', '--count',
            help='number of assets to escrow',
            default=0,
            type=int, required=False)

    @classmethod
    def invoke(cls, state, session_params, agent, count, **kwargs) :
        session_params['commit'] = True
        message = invocation_request('escrow', escrow_agent_identity=agent, count=count)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        session_params['commit'] = False
        message = invocation_request('escrow_attestation', escrow_agent_identity=agent)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_release(pcontract.contract_op_base) :

    name = "release"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--attestation',
            help='Release attestation from the escrow agent',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, attestation, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('release', release_request=attestation)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_claim(pcontract.contract_op_base) :

    name = "claim"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--attestation',
            help='Claim attestation from the escrow agent',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params,
               attestation, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('claim', claim_request=attestation)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_create_issuer(pcommand.contract_command_base) :
    """Create an issuer contract
    """

    name = "create"
    help = "create the issuer contract object, initialization will occur separately"

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
        save_file = pcontract_cmd.get_contract_from_context(state,context)
        if save_file :
            return save_file

        save_file = pcontract_cmd.create_contract_from_context(state, context, 'issuer_contract', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)
        verifying_key = pcontract.invoke_contract_op(
            common.op_get_verifying_key,
            state, context, session,
            **kwargs)
        verifying_key = json.loads(verifying_key)
        context['verifying_key'] = verifying_key

        cls.display('created issuer in {}'.format(save_file))
        return save_file

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_initialize_issuer(pcommand.contract_command_base) :
    """Create an issuer contract
    """

    name = "initialize_issuer"
    help = "initialize an issuer contract that has been vetted"

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('issuer contract must be created and approved')

        # get all the information necessary to register this contract as an endpoint with the guardian
        session = pbuilder.SessionParameters(save_file=save_file)
        verifying_key = context.get('verifying_key')
        if verifying_key is None :
            verifying_key = pcontract.invoke_contract_op(common.op_get_verifying_key, state, context, session)
            verifying_key = json.loads(verifying_key)

        # get the approved authority from the vetting organization
        vetting_context = context.get_context('vetting_context')
        vetting_save_file = pcontract_cmd.get_contract_from_context(state, vetting_context)
        if vetting_save_file is None :
            raise ValueError("vetting contract has not been created")

        vetting_session = pbuilder.SessionParameters(save_file=vetting_save_file)
        authority = pcontract.invoke_contract_op(
            vetting.op_get_issuer_authority,
            state, vetting_context, vetting_session,
            verifying_key)
        authority = json.loads(authority)

        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            authority)

        cls.display('initialized issuer in {}'.format(save_file))
        return True

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_issue_assets(pcommand.contract_command_base) :
    """Create an issuer contract
    """

    name = "issue_assets"
    help = ""

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument('-o', '--owner', help='identity of the issuance owner; key file name', type=str, required=True)
        parser.add_argument('-c', '--count', help='amount of the issuance', type=int, required=True)

    @classmethod
    def invoke(cls, state, context, owner, count, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('issuer contract must be created and initialized')

        # get all the information necessary to register this contract as an endpoint with the guardian
        keypath = state.get(['Key', 'SearchPath'])
        keyfile = putils.find_file_in_path("{0}_public.pem".format(owner), keypath)
        with open (keyfile, "r") as myfile:
            verifying_key = myfile.read()

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_issue,
            state, context, session,
            verifying_key,
            count,
            **kwargs)

        cls.display('issued {} assets to {}'.format(count, owner))
        return True

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_get_balance(pcommand.contract_command_base) :
    """Check the balance of an issueance
    """

    name = "balance"
    help = "check the balance of an issuance"

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        # if not kwargs.get('identity') :
        #     kwargs['identity'] = state.identity
        #     kwargs['key_file'] = state.private_key_file

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('issuer contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)
        balance = pcontract.invoke_contract_op(
            op_get_balance,
            state, context, session,
            **kwargs)

        cls.display('current balance of {} for {} is {}'.format(context.path, state.identity, balance))
        return balance

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_transfer_assets(pcommand.contract_command_base) :
    """Check the transfer of an issueance
    """

    name = "transfer"
    help = "check the transfer of an issuance"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-n', '--new-owner',
            help='identity of the issuance owner; key file name',
            type=str, required=True)
        parser.add_argument(
            '-c', '--count',
            help='amount of the issuance',
            type=int, required=True)

    @classmethod
    def invoke(cls, state, context, new_owner, count, **kwargs) :
        # if not kwargs.get('identity') :
        #     kwargs['identity'] = state.identity
        #     kwargs['key_file'] = state.private_key_file

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('issuer contract must be created and initialized')

        keypath = state.get(['Key', 'SearchPath'])
        new_owner_key_file = putils.find_file_in_path("{0}_public.pem".format(new_owner), keypath)
        with open (new_owner_key_file, "r") as myfile:
            new_owner_key = myfile.read()

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_transfer,
            state, context, session,
            new_owner=new_owner_key,
            count=count,
            **kwargs)

        cls.display('transfered {} assets to {}'.format(count, new_owner))
        return True

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_get_authority,
    op_get_balance,
    op_get_entry,
    op_issue,
    op_transfer,
    op_escrow,
    op_release,
    op_claim,
    op_get_asset_type_identifier,
    op_approve_issuer,
    op_get_issuer_authority,
    op_get_verifying_key,
]

do_issuer_contract = pcontract.create_shell_command('issuer_contract', __operations__)

__commands__ = [
    cmd_create_issuer,
    cmd_initialize_issuer,
    cmd_issue_assets,
    cmd_get_balance,
    cmd_transfer_assets,
    vetting.cmd_approve_issuer,
]

do_issuer = pcommand.create_shell_command('issuer', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'issuer', do_issuer)
    pshell.bind_shell_command(cmdclass, 'issuer_contract', do_issuer_contract)
