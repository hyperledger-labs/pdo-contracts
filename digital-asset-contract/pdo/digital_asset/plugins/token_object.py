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

from pdo.common.crypto import byte_array_to_base64, base64_to_byte_array
from pdo.contract import invocation_request

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.exchange.plugins.token_object as token_object

__all__ = [
    'op_initialize',
    'op_echo',
    'op_get_verifying_key',
    'op_get_contract_metadata',
    'op_get_contract_code_metadata',
    'op_get_asset_type_identifier',
    'op_get_issuer_authority',
    'op_get_authority',
    'op_transfer',
    'op_escrow',
    'op_release',
    'op_claim',
    'cmd_mint_tokens',
    'cmd_transfer_assets',
    'cmd_get_image_metadata',
    'cmd_get_public_image',
    'cmd_get_original_image',
    'do_da_token',
    'do_da_token_contract',
    'load_commands',
]

## -----------------------------------------------------------------
## -----------------------------------------------------------------
op_get_verifying_key = token_object.op_get_verifying_key
op_get_contract_metadata = token_object.op_get_contract_metadata
op_get_contract_code_metadata = token_object.op_get_contract_code_metadata
op_get_asset_type_identifier = token_object.op_get_asset_type_identifier
op_get_issuer_authority = token_object.op_get_issuer_authority
op_get_authority = token_object.op_get_authority
op_transfer = token_object.op_transfer
op_escrow = token_object.op_escrow
op_release = token_object.op_release
op_claim = token_object.op_claim
op_initialize = token_object.op_initialize
cmd_mint_tokens = token_object.cmd_mint_tokens
cmd_transfer_assets = token_object.cmd_transfer_assets

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## some utility functions
## -----------------------------------------------------------------

## -----------------------------------------------------------------
def __save_image__(result, filename) :
    # not catching exceptions intentionally, we want the interpreter
    # to see and handle the exception
    parsed_result = json.loads(result)
    decoded_image_data = base64_to_byte_array(parsed_result['encoded_image'])

    with open(filename, 'wb') as fp:
        fp.write(bytes(decoded_image_data))

## -----------------------------------------------------------------
## get_image_metadata
## -----------------------------------------------------------------
class op_get_image_metadata(pcontract.contract_op_base) :

    name = "get_image_metadata"
    help = ""

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-d', '--data-guardian',
            help="contract object for the data guardian",
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, data_guardian, **kwargs) :
        params = {}

        message = invocation_request('get_image_metadata', **params)
        capability = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, capability)

        dg_session = pbuilder.SessionParameters(save_file=data_guardian)

        params = json.loads(capability)
        message = invocation_request('process_capability', **params)
        result = pcontract_cmd.send_to_contract(state, message, **dg_session)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## op_get_public_image
## -----------------------------------------------------------------
class op_get_public_image(pcontract.contract_op_base) :

    name = "get_public_image"
    help = ""

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-d', '--data-guardian',
            help="contract object for the data guardian",
            type=str, required=True)
        parser.add_argument(
            '-i', '--image-file',
            help='File where image is stored',
            type=str)

    @classmethod
    def invoke(cls, state, session_params, data_guardian, image_file, **kwargs) :
        params = {}

        message = invocation_request('get_public_image', **params)
        capability = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, capability)

        dg_session = pbuilder.SessionParameters(save_file=data_guardian)

        params = json.loads(capability)
        message = invocation_request('process_capability', **params)
        result = pcontract_cmd.send_to_contract(state, message, **dg_session)
        cls.log_invocation(message, result)

        if image_file:
            __save_image__(result, image_file)

        return result

## -----------------------------------------------------------------
## get_original_image
## -----------------------------------------------------------------
class op_get_original_image(pcontract.contract_op_base) :

    name = "get_original_image"
    help = ""

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-d', '--data-guardian',
            help="contract object for the data guardian",
            type=str, required=True)
        parser.add_argument(
            '-i', '--image-file',
            help='File where image is stored',
            type=str)

    @classmethod
    def invoke(cls, state, session_params, data_guardian, image_file, **kwargs) :
        params = {}

        message = invocation_request('get_original_image', **params)
        capability = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, capability)

        dg_session = pbuilder.SessionParameters(save_file=data_guardian)

        params = json.loads(capability)
        message = invocation_request('process_capability', **params)
        result = pcontract_cmd.send_to_contract(state, message, **dg_session)
        cls.log_invocation(message, result)

        if image_file:
            __save_image__(result, image_file)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_get_image_metadata(pcommand.contract_command_base) :
    name = "get_image_metadata"
    help = "get image metadata"

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("token has not been created")

        guardian_context = context.get_context('data_guardian_context')
        guardian_save_file = pcontract_cmd.get_contract_from_context(state, guardian_context)

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_get_image_metadata, state, context, session, guardian_save_file, **kwargs)

        cls.display(result)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_get_public_image(pcommand.contract_command_base) :
    name = "get_public_image"
    help = "get image metadata"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-i', '--image-file',
            help='File where image is stored',
            required=True,
            type=str)

    @classmethod
    def invoke(cls, state, context, image_file, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("token has not been created")

        guardian_context = context.get_context('data_guardian_context')
        guardian_save_file = pcontract_cmd.get_contract_from_context(state, guardian_context)

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_get_public_image, state, context, session, guardian_save_file, image_file, **kwargs)

        cls.display("image saved to file {}".format(image_file))

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_get_original_image(pcommand.contract_command_base) :
    name = "get_original_image"
    help = "get image metadata"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument(
            '-i', '--image-file',
            help='File where image is stored',
            required=True,
            type=str)

    @classmethod
    def invoke(cls, state, context, image_file, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("token has not been created")

        guardian_context = context.get_context('data_guardian_context')
        guardian_save_file = pcontract_cmd.get_contract_from_context(state, guardian_context)

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_get_original_image, state, context, session, guardian_save_file, image_file, **kwargs)

        cls.display("image saved to file {}".format(image_file))

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
    op_get_verifying_key,
    op_get_contract_metadata,
    op_get_contract_code_metadata,
    op_get_asset_type_identifier,
    op_get_issuer_authority,
    op_get_authority,
    op_transfer,
    op_escrow,
    op_release,
    op_claim,
    op_get_image_metadata,
    op_get_public_image,
    op_get_original_image,
]

do_da_token_contract = pcontract.create_shell_command('da_token_contract', __operations__)

__commands__ = [
    cmd_mint_tokens,
    cmd_transfer_assets,
    cmd_get_image_metadata,
    cmd_get_public_image,
    cmd_get_original_image,
]

do_da_token = pcommand.create_shell_command('da_token', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'da_token', do_da_token)
    pshell.bind_shell_command(cmdclass, 'da_token_contract', do_da_token_contract)
