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

__all__ = [
    'op_initialize',
    'op_get_verifying_key',
    'op_register_signing_context',
    'op_describe_signing_context',
    'op_sign',
    'op_verify',
    'cmd_create_identity',
    'do_identity',
    'do_identity_contract',
    'load_commands',
]

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize an identity contract object"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-d', '--description',
            help='Description of the asset described by the identity',
            type=str,
            required=True)

    @classmethod
    def invoke(cls, state, session_params, description, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('initialize', description=description)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_get_verifying_key(pcontract.contract_op_base) :

    name = "get_verifying_key"
    help = "Get the verifying key for a context"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)

    @classmethod
    def invoke(cls, state, session_params, path, **kwargs) :
        session_params['commit'] = True

        params = {
            'context_path' : path,
        }
        message = invocation_request('get_verifying_key', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_register_signing_context(pcontract.contract_op_base) :

    name = "register_signing_context"
    help = "Register a signing context"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-d', '--description',
            help='Description of the asset described by the identity',
            type=str,
            required=True)
        subparser.add_argument(
            '--extensible',
            help='Allow unregistered contexts to be used from this context',
            action='store_true')
        subparser.add_argument(
            '--fixed',
            help='Only registered contexts may be used from this context',
            action='store_false',
            dest='extensible')
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)

    @classmethod
    def invoke(cls, state, session_params, path, description, extensible, **kwargs) :
        session_params['commit'] = True

        params = {
            'context_path' : path,
            'description' : description,
            'extensible' : extensible,
        }
        message = invocation_request('register_signing_context', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_describe_signing_context(pcontract.contract_op_base) :

    name = "describe_signing_context"
    help = "Describe a signing context"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)
        pass

    @classmethod
    def invoke(cls, state, session_params, path, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('describe_signing_context', context_path=path)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_sign(pcontract.contract_op_base) :

    name = "sign"
    help = "Sign message using specified signing context"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-m', '--message',
            help='Base64 encoded string to sign',
            type=str,
            required=True)
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)

    @classmethod
    def invoke(cls, state, session_params, path, message, **kwargs) :
        session_params['commit'] = True

        bytes_message = pcrypto.string_to_byte_array(message)
        b64_message = pcrypto.byte_array_to_base64(bytes_message)
        message = invocation_request('sign', context_path=path, message=b64_message)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class op_verify(pcontract.contract_op_base) :

    name = "verify"
    help = "Verify a signature using the specified signing context"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-m', '--message',
            help='Base64 encoded string to sign',
            type=str,
            required=True)
        subparser.add_argument(
            '-p', '--path',
            help='Path to the signing context',
            type=str,
            nargs='+',
            required=True)
        subparser.add_argument(
            '--signature',
            help='Base64 encoded signature to verify',
            type=pbuilder.invocation_parameter,
            required=True)

    @classmethod
    def invoke(cls, state, session_params, path, message, signature, **kwargs) :
        session_params['commit'] = True

        bytes_message = pcrypto.string_to_byte_array(message)
        b64_message = pcrypto.byte_array_to_base64(bytes_message)

        params = {
            'message' : b64_message,
            'context_path' : path,
            'signature' : signature,
        }
        message = invocation_request('verify', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class cmd_create_identity(pcommand.contract_command_base) :
    name = "create"
    help = "script to create an identity"

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
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'identity', **kwargs)
        context['save_file'] = save_file

        session = pbuilder.SessionParameters(save_file=save_file)
        pcontract.invoke_contract_op(
            op_initialize,
            state, context, session,
            description,
            **kwargs)

        cls.display('created identity in {}'.format(save_file))
        return save_file

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
]

do_identity_contract = pcontract.create_shell_command('identity_contract', __operations__)

__commands__ = [
    cmd_create_identity,
]

do_identity = pcommand.create_shell_command('identity', __commands__)

# -----------------------------------------------------------------
# Enable binding of the shell independent version to a pdo-shell command
# -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'identity_wallet', do_identity)
    pshell.bind_shell_command(cmdclass, 'identity_wallet_contract', do_identity_contract)
