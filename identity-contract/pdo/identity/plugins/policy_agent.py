# Copyright 2023 Intel Corporation
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

import pdo.common.crypto as pcrypto


import pdo.identity.plugins.identity as identity_plugin
import pdo.identity.plugins.signature_authority as signature_plugin

__all__ = [
    'op_initialize',
    'op_get_verifying_key',
    'op_get_extended_verifying_key',
    'op_register_signing_context',
    'op_describe_signing_context',
    'op_sign',
    'op_verify',
    'op_verify_credential',
    'op_register_trusted_issuer',
    'op_issue_policy_credential',
    'cmd_create_policy_agent',
    'do_policy_agent',
    'do_policy_agent_contract',
    'load_commands',
]

op_initialize = identity_plugin.op_initialize
op_get_verifying_key = identity_plugin.op_get_verifying_key
op_get_extended_verifying_key = identity_plugin.op_get_extended_verifying_key
op_register_signing_context = identity_plugin.op_register_signing_context
op_describe_signing_context = identity_plugin.op_describe_signing_context
op_sign = identity_plugin.op_sign
op_verify = signature_plugin.op_verify
op_verify_credential = signature_plugin.op_verify_credential

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_register_trusted_issuer(pcontract.contract_op_base) :

    name = "register_trusted_issuer"
    help = "register a trusted issuer of input credentials"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--chaincode',
            help='The chain code of the issuer to register (base64 encoded)',
            type=str,
            required=True)

        subparser.add_argument(
            '-i', '--issuer',
            help='The issuer to register (issuer contract identifier)',
            type=str,
            required=True)

        subparser.add_argument(
            '-k', '--key',
            help='The extended public key of the issuer to register',
            type=pbuilder.invocation_parameter,
            required=True)

        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='*',
            default=[],
            required=False)


    @classmethod
    def invoke(cls, state, session_params, issuer, path, key, chaincode, **kwargs) :
        session_params['commit'] = True

        params = {
            'chain_code' : chaincode,
            'issuer_identity' : issuer,
            'public_key' : key,
            'context_path' : path,
        }

        message = invocation_request('register_trusted_issuer', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_issue_policy_credential(pcontract.contract_op_base) :

    name = "issue_policy_credential"
    help = "process input credentials and issue a policy credential"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--credential',
            help='Input credential for the policy (JSON)',
            type=pbuilder.invocation_parameter,
            required=True)

    @classmethod
    def invoke(cls, state, session_params, credential, **kwargs) :
        session_params['commit'] = True

        params = {
            'credential' : credential,
        }

        message = invocation_request('issue_policy_credential', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# class cmd_issue_policy_credential(pcommand.contract_command_base) :
#     name = "sign_credential"
#     help = "Sign a credential and generate the associated verifiable credential"

#     @classmethod
#     def add_arguments(cls, subparser) :
#         subparser.add_argument(
#             '-c', '--credential',
#             help='The name of the file containing the credential to sign',
#             type=str,
#             required=True)
#         subparser.add_argument(
#             '-s', '--signed-credential',
#             help='Name of the file where the signed credential will be saved',
#             type=str,
#             required=True)

#     @classmethod
#     def invoke(cls, state, context, credential, path, signed_credential, **kwargs) :
#         with open(credential, "r") as fp :
#             credential_data = json.load(fp)

#         save_file = pcontract_cmd.get_contract_from_context(state, context)
#         if not save_file :
#             raise ValueError('signature authority contract must be created and initialized')

#         session = pbuilder.SessionParameters(save_file=save_file)
#         signed_credential_data = pcontract.invoke_contract_op(
#             op_issue_policy_credential,
#             state, context, session,
#             credential=credential_data,
#             **kwargs)

#         with open(signed_credential, "w") as fp :
#             json.dump(signed_credential_data, fp)

#         cls.display('saved credential to {}'.format(signed_credential))
#         return True

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_create_policy_agent(pcommand.contract_command_base) :
    name = "create"
    help = "script to create a new policy agent"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument('-c', '--contract-class', help='Name of the contract class', type=str)
        subparser.add_argument('-e', '--eservice-group', help='Name of the enclave service group to use', type=str)
        subparser.add_argument('-f', '--save-file', help='File where contract data is stored', type=str)
        subparser.add_argument('-p', '--pservice-group', help='Name of the provisioning service group to use', type=str)
        subparser.add_argument('-r', '--sservice-group', help='Name of the storage service group to use', type=str)
        subparser.add_argument('--source', help='File that contains contract source code', type=str)
        subparser.add_argument('--extra', help='Extra data associated with the contract file', nargs=2, action='append')

        subparser.add_argument(
            '-d', '--description',
            help='Description of the asset described by the identity',
            type=str,
            required=True)

    @classmethod
    def invoke(cls, state, context, description, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if save_file :
            return save_file

        # create the vetting organization type
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'policy_agent', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            description,
            **kwargs)

        cls.display('created policy agent in {}'.format(save_file))
        return save_file

# -----------------------------------------------------------------
# Create the generic, shell independent version of the aggregate command
# -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_get_verifying_key,
    op_get_extended_verifying_key,
    op_register_signing_context,
    op_describe_signing_context,
    op_sign,
    op_verify,
    op_verify_credential,
    op_register_trusted_issuer,
    op_issue_policy_credential,
]

do_policy_agent_contract = pcontract.create_shell_command('identity_contract', __operations__)

__commands__ = [
    cmd_create_policy_agent,
    # cmd_issue_policy_credential,
    # cmd_register_trusted_issuer,
]

do_policy_agent = pcommand.create_shell_command('identity', __commands__)

# -----------------------------------------------------------------
# Enable binding of the shell independent version to a pdo-shell command
# -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'policy_agent', do_policy_agent)
    pshell.bind_shell_command(cmdclass, 'policy_agent_contract', do_policy_agent_contract)
