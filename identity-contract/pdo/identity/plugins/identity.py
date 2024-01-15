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
import pdo.exchange.plugins.asset_type as asset_type

import pdo.common.crypto as pcrypto

__all__ = [
    'op_initialize',
    'op_register_signing_context',
    'op_describe_signing_context',
    'op_sign',
    'op_verify',
    'op_add_credential',
    'op_remove_credential',
    'op_create_presentation',
    'do_identity',
    'do_identity_contract',
    'load_commands',
]

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
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

## -----------------------------------------------------------------
## -----------------------------------------------------------------
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

## -----------------------------------------------------------------
## -----------------------------------------------------------------
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

## -----------------------------------------------------------------
## -----------------------------------------------------------------
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

## -----------------------------------------------------------------
## -----------------------------------------------------------------
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

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_add_credential(pcontract.contract_op_base) :

    name = "add_credential"
    help = "Store a credential in the wallet"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--credential',
            help='Base64 encoded credential',
            type=str,
            required=True)
        subparser.add_argument(
            '-i', '--identifier',
            help='Identifier for the credential for future operations',
            type=str,
            required=True)

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('add_credential')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_remove_credential(pcontract.contract_op_base) :

    name = "remove_credential"
    help = "Remove a credential from the wallet"

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('remove_credential')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_create_presentation(pcontract.contract_op_base) :

    name = "create_presentation"
    help = "Prepare a credential presentation"

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('create_presentation')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_register_signing_context,
    op_describe_signing_context,
    op_sign,
    op_verify,
    op_add_credential,
    op_remove_credential,
    op_create_presentation,
]

do_identity_contract = pcontract.create_shell_command('identity_contract', __operations__)

__commands__ = [
]

do_identity = pcommand.create_shell_command('identity', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'identity_wallet', do_identity)
    pshell.bind_shell_command(cmdclass, 'identity_wallet_contract', do_identity_contract)
