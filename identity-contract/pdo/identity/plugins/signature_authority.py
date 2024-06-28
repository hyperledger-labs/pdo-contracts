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

import json
import logging

from pdo.contract import invocation_request

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.identity.plugins.identity as identity

__all__ = [
    'op_initialize',
    'op_get_verifying_key',
    'op_register_signing_context',
    'op_describe_signing_context',
    'op_sign',
    'op_verify',
    'op_sign_credential',
    'op_verify_credential',
    'do_signature_authority',
    'do_signature_authority_contract',
    'load_commands',
]

op_initialize = identity.op_initialize
op_get_verifying_key = identity.op_get_verifying_key
op_register_signing_context = identity.op_register_signing_context
op_describe_signing_context = identity.op_describe_signing_context
op_sign = identity.op_sign
op_verify = identity.op_verify

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_sign_credential(pcontract.contract_op_base) :

    name = "sign_credential"
    help = "Sign a credential and generate the associated verifiable credential"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--credential',
            help='The credential to sign (JSON)',
            type=pbuilder.invocation_parameter,
            required=True)
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)

    @classmethod
    def invoke(cls, state, session_params, credential, path, **kwargs) :
        session_params['commit'] = False

        params = {
            'credential' : credential,
            'context_path' : path,
        }

        message = invocation_request('sign_credential', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_verify_credential(pcontract.contract_op_base) :

    name = "verify_credential"
    help = "Verify the signature on a signed (verifiable) credential"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--credential',
            help='The signed credential to verify (JSON)',
            type=pbuilder.invocation_parameter,
            required=True)

    @classmethod
    def invoke(cls, state, session_params, credential, **kwargs) :
        session_params['commit'] = False

        params = {
            'credential' : credential
        }

        message = invocation_request('verify_credential', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_sign_credential(pcommand.contract_command_base) :
    name = "sign_credential"
    help = "Sign a credential and generate the associated verifiable credential"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--credential',
            help='The name of the file containing the credential to sign',
            type=str,
            required=True)
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)
        subparser.add_argument(
            '-s', '--signed-credential',
            help='Name of the file where the signed credential will be saved',
            type=str,
            required=True)

    @classmethod
    def invoke(cls, state, context, credential, path, signed_credential, **kwargs) :
        with open(credential, "r") as fp :
            credential_data = json.load(fp)

        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('signature authority contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)
        signed_credential_data = pcontract.invoke_contract_op(
            op_sign_credential,
            state, context, session,
            credential=credential_data,
            path=path,
            **kwargs)

        with open(signed_credential, "w") as fp :
            json.dump(signed_credential_data, fp)

        cls.display('saved credential to {}'.format(signed_credential))
        return True

# -----------------------------------------------------------------
# Create the generic, shell independent version of the aggregate command
# -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_get_verifying_key,
    op_register_signing_context,
    op_describe_signing_context,
    op_sign,
    op_verify,
    op_sign_credential,
    op_verify_credential,
]

do_signature_authority_contract = pcontract.create_shell_command('signature_authority_contract', __operations__)

__commands__ = [
    cmd_sign_credential,
]

do_signature_authority = pcommand.create_shell_command('signature_authority', __commands__)

# -----------------------------------------------------------------
# Enable binding of the shell independent version to a pdo-shell command
# -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'signature_authority', do_signature_authority)
    pshell.bind_shell_command(cmdclass, 'signature_authority_contract', do_signature_authority_contract)
