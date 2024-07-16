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

import pdo.common.utility as putils
from pdo.contract import invocation_request
from pdo.submitter.create import create_submitter

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.exchange.plugins.asset_type as asset_type
import pdo.exchange.plugins.guardian as guardian
import pdo.exchange.plugins.issuer as issuer
import pdo.exchange.plugins.token_issuer as token_issuer
import pdo.exchange.plugins.vetting as vetting

__all__ = [
    'op_initialize',
    'op_echo',
    'op_get_verifying_key',
    'op_get_contract_metadata',
    'op_get_contract_code_metadata',
    'op_get_asset_type_identifier',
    'op_get_issuer_authority',
    'op_get_authority',
    'op_get_balance',
    'op_transfer',
    'op_escrow',
    'op_release',
    'op_claim',
    'cmd_mint_tokens',
    'cmd_transfer_assets',
    'cmd_echo',
    'do_token_object',
    'do_token_object_contract',
    'load_commands',
]

op_get_verifying_key = common.op_get_verifying_key
op_get_contract_metadata = common.op_get_contract_metadata
op_get_contract_code_metadata = common.op_get_contract_code_metadata
op_get_asset_type_identifier = asset_type.op_get_asset_type_identifier
op_get_issuer_authority = vetting.op_get_issuer_authority
op_get_authority = issuer.op_get_authority
op_get_balance = issuer.op_get_balance
op_transfer = issuer.op_transfer
op_escrow = issuer.op_escrow
op_release = issuer.op_release
op_claim = issuer.op_claim

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize the token object with the package received from the data guardian"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--authority',
            help='serialized authority from the vetting organization',
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-i', '--initialization-package',
            help="the token issuer initialization package from the guardian",
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-l', '--ledger-key',
            help='ledger verifying key',
            type=pbuilder.invocation_parameter, required=True)


    @classmethod
    def invoke(cls, state, session_params, ledger_key, initialization_package, authority, **kwargs) :
        session_params['commit'] = True

        params = {}
        params['ledger_verifying_key'] = ledger_key
        params['initialization_package'] = initialization_package
        params['asset_authority_chain'] = authority

        message = invocation_request('initialize', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_echo(pcontract.contract_op_base) :

    name = "echo"
    help = "echo operation that is used exclusively for testing the token object/guardian interface"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-m', '--message',
            help='identity of the escrow agent',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, message, **kwargs) :
        session_params['commit'] = False

        params = {}
        params['message'] = message

        message = invocation_request('echo', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_mint_tokens(pcommand.contract_command_base) :
    """Mint token objects
    For now the required context is the token object context.
    """

    name = "mint_tokens"
    help = "mint tokens for a token issuer"

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
    def mint_one_token(cls, state, to_context, ti_context, dg_context, ledger_submitter, **kwargs) :
        """Mint a token from the token issuer

        @param state : configuration for current session
        @param ti_session : information for interacting with the token issuer
        @param to_save_file : name of the file to store the token object contract
        @param to_source : name of the file that contains token object contract source
        """

        ledger_key = ledger_submitter.get_ledger_info()

        to_save_file = pcontract_cmd.create_contract_from_context(state, to_context, 'token_object', **kwargs)
        to_session = pbuilder.SessionParameters(save_file=to_save_file, wait=True)

        to_contract = pcontract_cmd.get_contract(state, to_save_file)

        # set up the attested connection between the token object and the token
        # issuer, we need to collect a bunch of information from the contract and ledger
        ledger_attestation = ledger_submitter.get_contract_info(to_contract.contract_id)

        to_metadata = pcontract.invoke_contract_op(
            common.op_get_contract_metadata,
            state, to_context, to_session)
        to_metadata = json.loads(to_metadata)

        to_code_metadata = pcontract.invoke_contract_op(
            common.op_get_contract_code_metadata,
            state, to_context, to_session)
        to_code_metadata = json.loads(to_code_metadata)

        ti_save_file = pcontract_cmd.get_contract_from_context(state, ti_context)
        if ti_save_file is None :
            raise ValueError('must create token issuer prior to minting tokens')

        ti_session = pbuilder.SessionParameters(save_file=ti_save_file)

        pcontract.invoke_contract_op(
            token_issuer.op_add_endpoint,
            state, ti_context, ti_session,
            to_contract.contract_id,
            ledger_attestation,
            to_metadata,
            to_code_metadata)

        pcontract.invoke_contract_op(
            token_issuer.op_mint_token_object,
            state, ti_context, ti_session.clone(wait=True),
            to_contract.contract_id)

        # get the token information package to hand to the data guardian, this
        # will cause the guardian to create the capability generation key
        ti_contract = pcontract_cmd.get_contract(state, ti_save_file)
        state_attestation = ledger_submitter.get_current_state_hash(ti_contract.contract_id)
        dg_package = pcontract.invoke_contract_op (
            token_issuer.op_provision_token_object,
            state, ti_context, ti_session,
            to_contract.contract_id,
            state_attestation['signature'])
        dg_package = json.loads(dg_package)

        # the token object is an issuer, this is kind of weird in a sense but it
        # makes buying & selling token objects fit with the rest of the contract family
        # that is, token objects can be used in exchanges and auctions as you would expect
        pcontract.invoke_contract_op(
            token_issuer.op_approve_issuer,
            state, ti_context, ti_session,
            to_metadata['verifying_key'])
        authority = pcontract.invoke_contract_op(
            token_issuer.op_get_issuer_authority,
            state, ti_context, ti_session,
            to_metadata['verifying_key'])
        authority = json.loads(authority)

        # get the token initialization package from the data guardian
        to_package = pcommand.invoke_contract_cmd(
            guardian.cmd_provision_token_object,
            state, dg_context,
            dg_package,
            **kwargs)

        # and push the token initialization package into the token object
        pcontract.invoke_contract_op(
            op_initialize,
            state, to_context, to_session,
            ledger_key,
            to_package,
            authority,
            **kwargs)
        return to_save_file

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)

        token_issuer_context = context.get_context('token_issuer_context')
        if token_issuer_context['identity'] != context['identity'] :
            raise ValueError('token issuer and token object must be created by the same identity')

        data_guardian_context = context.get_context('data_guardian_context')
        if data_guardian_context['identity'] != context['identity'] :
            raise ValueError('data guardian and token object must be created by the same identity')

        token_count = token_issuer_context.get('count', 0)
        if token_count == 0 :
            raise ValueError('invalid configuration, missing token count')

        minted_tokens = context.get('token_save_file_list', [])

        # need the ledger key as the root of trust for binding to the issuer
        ledger_submitter = create_submitter(state.get(['Ledger']))

        while len(minted_tokens) < token_count :
            to_save_file = cls.mint_one_token(
                state,
                context,
                token_issuer_context,
                data_guardian_context,
                ledger_submitter,
                **kwargs)
            minted_tokens.append(to_save_file)
            context['token_{}'.format(len(minted_tokens))] = {
                'module' : '${..module}',
                'identity' : '${..identity}',
                'source' : '${..source}',
                'token_issuer_context' : '@{..token_issuer_context}',
                'data_guardian_context' : '@{..data_guardian_context}',
                'save_file' : to_save_file
            }

            cls.display('created token object in {}'.format(to_save_file))

        context['token_save_file_list'] = minted_tokens
        return minted_tokens

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_transfer_assets(pcommand.contract_command_base) :
    """Transfer ownership of a token object
    """

    name = "transfer"
    help = "transfer ownership of a token"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-n', '--new-owner',
            help='identity of the issuance owner; key file name',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, context, new_owner, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('issuer contract must be created and initialized')

        keypath = state.get(['Key', 'SearchPath'])
        keyfile = putils.find_file_in_path("{0}_public.pem".format(new_owner), keypath)
        with open (keyfile, "r") as myfile:
            verifying_key = myfile.read()

        # in case count was specified, it must be 1 and we must remove it since it is set explicitly
        # in the op invocation below
        if 'count' in kwargs :
            if kwargs['count'] != 1 :
                raise ValueError('unexpected count for token transfer')
            kwargs.pop('count')

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(issuer.op_transfer, state, context, session, verifying_key, 1, **kwargs)

        cls.display('transfered token to {}'.format(new_owner))
        return save_file

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_echo(pcommand.contract_command_base) :
    """Invoke the echo method on the guardian using a capability
    generated by the token object
    """

    name = "echo"
    help = "invoke the echo method on the guardian"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-m', '--message',
            help='identity of the escrow agent',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, context, message, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('token object contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)
        echo_capability = pcontract.invoke_contract_op(op_echo, state, context, session, message, **kwargs)
        echo_capability = json.loads(echo_capability)

        dg_context = context.get_context('data_guardian_context')
        if dg_context['identity'] != context['identity'] :
            raise ValueError('data guardian and token object must be created by the same identity')

        dg_save_file = pcontract_cmd.get_contract_from_context(state, dg_context)
        if dg_save_file is None :
            raise ValueError('must create data guardian')

        dg_session = pbuilder.SessionParameters(save_file=dg_save_file)
        result = pcontract.invoke_contract_op(
            guardian.op_process_capability, state, dg_context, dg_session, echo_capability, **kwargs)

        cls.display('echo capability returned: {}'.format(result))
        return result

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_echo, # note that this is for the test contract only
    op_get_verifying_key,
    op_get_contract_metadata,
    op_get_contract_code_metadata,
    op_get_asset_type_identifier,
    op_get_issuer_authority,
    op_get_authority,
    op_get_balance,
    op_transfer,
    op_escrow,
    op_release,
    op_claim
]

do_token_object_contract = pcontract.create_shell_command('token_object_contract', __operations__)

__commands__ = [
    cmd_mint_tokens,
    cmd_transfer_assets,
    cmd_echo,
]

do_token_object = pcommand.create_shell_command('token_object', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'token_object', do_token_object)
    pshell.bind_shell_command(cmdclass, 'token_object_contract', do_token_object_contract)
