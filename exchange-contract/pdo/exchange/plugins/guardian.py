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

import json
import logging

import pdo.common.crypto as pcrypto
from pdo.contract import ContractCode
from pdo.contract import invocation_request
from pdo.submitter.create import create_submitter

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common

__all__ = [
    'op_initialize',
    'op_provision_token_issuer',
    'op_provision_token_object',
    'op_process_capability',
    'op_add_endpoint',
    'op_get_contract_code_metadata',
    'op_get_contract_metadata',
    'op_get_ledger_key',
    'op_get_verifying_key',
    'cmd_create_guardian',
    'cmd_provision_token_issuer',
    'cmd_provision_token_object',
    'do_guardian',
    'do_guardian_contract',
    'load_commands',
]

op_add_endpoint = common.op_add_endpoint
op_get_contract_code_metadata = common.op_get_contract_code_metadata
op_get_contract_metadata = common.op_get_contract_metadata
op_get_ledger_key = common.op_get_ledger_key
op_get_verifying_key = common.op_get_verifying_key

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize the data guardian contract object"

    @classmethod
    def add_arguments(cls, parser) :
        ch_action = parser.add_mutually_exclusive_group(required=True)
        ch_action.add_argument(
            '-c', '--code-hash',
            help="token issuer code hash",
            type=pbuilder.invocation_parameter)
        ch_action.add_argument(
            '-t', '--token-issuer-code',
            help="token issuer contract code to be used to compute code hash",
            nargs=2, type=str)
        parser.add_argument(
            '-l', '--ledger-key',
            help='ledger verifying key',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, code_hash, token_issuer_code, ledger_key, **kwargs) :
        session_params['commit'] = True

        params = {}
        params['ledger_verifying_key'] = ledger_key

        if code_hash :
            params['token_issuer_code_hash'] = code_hash
        elif token_issuer_code :
            source_path = state.get(['Contract', 'SourceSearchPath'])
            (contract_class, contract_source) = token_issuer_code
            contract_code = ContractCode.create_from_file(
                contract_class, contract_source, source_path, interpreter='wawaka')

            message = contract_code.code + contract_code.name
            code_hash = pcrypto.compute_message_hash(pcrypto.string_to_byte_array(message))
            params['token_issuer_code_hash'] = pcrypto.byte_array_to_base64(code_hash)
        else :
            raise ValueError("missing required parameter; must specify verifying key")

        message = invocation_request('initialize', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_provision_token_issuer(pcontract.contract_op_base) :

    name = "provision_token_issuer"
    help = "provision the token issuer with the capability management key"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, contract_id, **kwargs) :
        session_params['commit'] = False

        params = {}
        params['contract_id'] = contract_id
        message = invocation_request('provision_token_issuer', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result
## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_provision_token_object(pcontract.contract_op_base) :

    name = "provision_token_object"
    help = "provision a token object with an identity and capability generation key"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-p', '--provisioning-package',
            help='contract secret containing the provisioning package',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, provisioning_package, **kwargs) :
        session_params['commit'] = True

        params = provisioning_package
        message = invocation_request('provision_token_object', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result
## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_process_capability(pcontract.contract_op_base) :

    name = "process_capability"
    help = "process a capability operation"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-c', '--capability',
            help='capability generated by the token object create operation interface',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, capability, **kwargs) :
        session_params['commit'] = False

        params = capability
        message = invocation_request('process_capability', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# create the guardian
# -----------------------------------------------------------------
class cmd_create_guardian(pcommand.contract_command_base) :
    """Create and initialize a guardian contract object
    """
    name = "create"
    help = "create a guardian contract object"

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

        # need the ledger key as the root of trust for binding to the issuer
        ledger_submitter = create_submitter(state.get(['Ledger']))
        ledger_key = ledger_submitter.get_ledger_info()

        # create the guardian contract
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'guardian', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)

        # and we need the issuer contract source to validate the issuer
        issuer_context = context.get_context('token_issuer_context')
        issuer_contract_source = issuer_context['source']
        issuer_contract_class = 'token_issuer'

        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            None,
            (issuer_contract_class, issuer_contract_source),
            ledger_key,
            **kwargs)

        cls.display('created guardian in {}'.format(save_file))
        return save_file

# -----------------------------------------------------------------
# provision a token issuer
# -----------------------------------------------------------------
class cmd_provision_token_issuer(pcommand.contract_command_base) :
    """Create the token issuer provisioning package

    While this may be invoked from the shell, it is more often invoked
    as part of a more complete flow (such as the protocol for fully
    provisioning token issuers and object.
    """
    name = "provision_issuer"
    help = "create the token issuer provisioning package"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--code-metadata',
            help='contract code metadata',
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)
        subparser.add_argument(
            '-l', '--ledger-attestation',
            help='attestation from the ledger',
            type=pbuilder.invocation_parameter, required=True)
        subparser.add_argument(
            '-m', '--contract-metadata',
            help='contract metadata',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, context, contract_id, ledger_attestation, contract_metadata, code_metadata, **kwargs) :

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            save_file = pcommand.invoke_contract_cmd(cmd_create_guardian, state, context, **kwargs)

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            common.op_add_endpoint,
            state, context, session,
            contract_id,
            ledger_attestation,
            contract_metadata,
            code_metadata,
            **kwargs)

        provisioning_package = pcontract.invoke_contract_op(
            op_provision_token_issuer,
            state, context, session,
            contract_id,
            **kwargs)

        cls.display('provisioned guardian for token issuer {}'.format(save_file))
        return json.loads(provisioning_package)

# -----------------------------------------------------------------
# provision a token object
# -----------------------------------------------------------------
class cmd_provision_token_object(pcommand.contract_command_base) :
    """Create the token object provisioning package

    While this may be invoked from the shell, it is more often invoked
    as part of a more complete flow (such as the protocol for fully
    provisioning token issuers and object.
    """

    name = "provision_token"
    help = "create the token object provisioning package"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-p', '--provisioning-package',
            help='contract secret containing the provisioning package',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, context, provisioning_package, **kwargs) :

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("guardian contract has not been created")

        session = pbuilder.SessionParameters(save_file=save_file)
        to_package = pcontract.invoke_contract_op(
            op_provision_token_object,
            state, context, session,
            provisioning_package,
            **kwargs)

        cls.display('provisioned token object for guardian {}'.format(save_file))
        return json.loads(to_package)

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_provision_token_issuer,
    op_provision_token_object,
    op_process_capability,
    op_add_endpoint,
    op_get_contract_code_metadata,
    op_get_contract_metadata,
    op_get_ledger_key,
    op_get_verifying_key,
]

do_guardian_contract = pcontract.create_shell_command('guardian_contract', __operations__)

__commands__ = [
    cmd_create_guardian,
    cmd_provision_token_issuer,
    cmd_provision_token_object,
]

do_guardian = pcommand.create_shell_command('guardian', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'guardian', do_guardian)
    pshell.bind_shell_command(cmdclass, 'guardian_contract', do_guardian_contract)
