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
from pdo.common.key_value import KeyValueStore
import pdo.common.utility as putils
import pdo.common.crypto as crypto

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.exchange.plugins.token_object as token_object

from pdo.inference.common.guardian_service import GuardianServiceClient

__all__ = [
    'op_initialize',
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
    'op_do_inference'
    'cmd_mint_tokens',
    'cmd_transfer_assets',
    'cmd_do_inference',
    'do_inference_token',
    'do_inference_token_contract',
    'load_commands',
]

## -----------------------------------------------------------------
## inherited operations
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
## -----------------------------------------------------------------
class op_do_inference(pcontract.contract_op_base) :
    """op_inference implements the full end-to-end inference of an image using a openvino model

    The specific inference operation depends on the model and the model script.
    """

    name = "do_inference"
    help = "inference using openvino model"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '--image',
            help='Filename of the image to use as inference input',
            type=str, required=True)

        subparser.add_argument(
            '--search-path',
            help='Directories to search for the data file',
            nargs='+', type=str, default=['.', './data'])

        subparser.add_argument(
            '-u', '--url',
            help='URL for the guardian service',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, image, search_path, url, **kwargs) :
        session_params['commit'] = False

        image_file = putils.find_file_in_path(image, search_path)
        with open(image_file, 'rb') as bf :
            image_bytes = bf.read()

        image_key = crypto.string_to_byte_array("__image__")
        image_bytes = crypto.string_to_byte_array(image_bytes)

        kv = KeyValueStore()
        with kv :
            _ = kv.set(image_key, image_bytes, input_encoding='raw', output_encoding='raw')

        # send the request to the contract to create a capability for the guardian
        params = {}
        params['image_key'] = "__image__"
        params['encryption_key'] = kv.encryption_key
        params['state_hash'] = kv.hash_identity

        message = invocation_request('do_inference', **params)
        capability = pcontract_cmd.send_to_contract(state,  message, **session_params)
        
        capability = json.loads(capability)

        cls.log_invocation(message, capability)

        # process the capability that was created
        service_client = GuardianServiceClient(url)

        # push the KV store blocks to the storage service associated with the guardian
        kv.sync_to_block_store(service_client)

        # send the capability to the guardian, this returns a dictionary
        result = service_client.process_capability(**capability)
        return result
        
## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_do_inference(pcommand.contract_command_base) :
    """cmd_inference implements the full end-to-end inference of an image using a openvino model

    The specific inference operation depends on the model and the model script.
    """
    name = "do_inference"
    help = "inference using openvino model"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '--image',
            help='Filename of the image to use as inference input',
            type=str, required=True)

        subparser.add_argument(
            '--search-path',
            help='Directories to search for the data file',
            nargs='+', type=str, default=['.', './data'])

        subparser.add_argument(
            '-u', '--url',
            help='URL for the guardian service',
            type=str)

    @classmethod
    def invoke(cls, state, context, image, search_path, url=None, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("token has not been created")

        if url is None :
            guardian_context = context.get_context('data_guardian_context')
            url = guardian_context['url']

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_do_inference,
            state, context, session,
            image,
            search_path,
            url,
            **kwargs)

        cls.display(result)

        return result

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
    op_do_inference,
]

do_inference_token_contract = pcontract.create_shell_command('inference_token_contract', __operations__)

__commands__ = [
    cmd_mint_tokens,
    cmd_transfer_assets,
    cmd_do_inference,
]

do_inference_token = pcommand.create_shell_command('inference_token', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'inference_token', do_inference_token)
    pshell.bind_shell_command(cmdclass, 'inference_token_contract', do_inference_token_contract)
                                                                                             