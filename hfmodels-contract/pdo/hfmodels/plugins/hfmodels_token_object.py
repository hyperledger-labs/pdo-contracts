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
import time

from pdo.submitter.create import create_submitter
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
from pdo.common.keys import ServiceKeys


from pdo.hfmodels.common.guardian_service import GuardianServiceClient

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
    'op_get_modelinfo',
    'op_use_hfmodel',
    'op_get_capability',
    'cmd_mint_hf_tokens',
    'cmd_mint_tokens',
    'cmd_transfer_assets',
    'cmd_use_hfmodel',
    'cmd_get_modelinfo',
    'do_hfmodels_token',
    'do_hfmodels_token_contract',
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
cmd_mint_tokens = token_object.cmd_mint_tokens
cmd_transfer_assets = token_object.cmd_transfer_assets

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
        subparser.add_argument('--hf_auth_token', help='Name of the contract class', type=str)
        subparser.add_argument('--hf_endpoint_url', help='Name of the enclave service group to use', type=str)
        subparser.add_argument('--fixed_model_params', help='File where contract data is stored', type=str)
        subparser.add_argument('--user_inputs_schema', help='Name of the provisioning service group to use', type=str)
        subparser.add_argument('--payload_type', help='Name of the storage service group to use', type=str)
        subparser.add_argument('--hfmodel_usage_info', help='File that contains contract source code', type=str)
        subparser.add_argument('--max_use_count', help='File that contains contract source code', type=int)


    @classmethod
    def invoke(cls, state, session_params, ledger_key, initialization_package, authority, **kwargs) :
        session_params['commit'] = True

        params = {}
        params['ledger_verifying_key'] = ledger_key
        params['initialization_package'] = initialization_package
        params['asset_authority_chain'] = authority

        # Add params from kwargs
        params['hf_auth_token'] = kwargs.get('hf_auth_token')
        params['hf_endpoint_url'] = kwargs.get('hf_endpoint_url')
        params['fixed_model_params'] = kwargs.get('fixed_model_params')
        params['user_inputs_schema'] = kwargs.get('user_inputs_schema')
        params['payload_type'] = kwargs.get('payload_type', 'json')
        params['hfmodel_usage_info'] = kwargs.get('hfmodel_usage_info')
        params['max_use_count'] = kwargs.get('max_use_count', 1)

        message = invocation_request('initialize', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_modelinfo(pcontract.contract_op_base) :
    """op_get_modelinfo implements the method to get the info about the  Hugging Face model stored in the token object
    """

    name = "op_get_modelinfo"
    help = "get info about the Hugging Face model stored in the token object"

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        params = {}
        message = invocation_request('get_model_info', **params)
        result = pcontract_cmd.send_to_contract(state,  message, **session_params)
        cls.log_invocation(message, result)

        return result
        


## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_use_hfmodel(pcontract.contract_op_base) :
    """op_use_hfmodel implements step 1 for the usage of a Hugging Face model via the guardian service
    The specific operation depends on the model. This method is used to fix all the parameters required to generate
    the capability that will be sent to the guardian service. the capability itself is not returned by this method
    the capability is returned only after proof of commit is received from the ledger after this method.
    Step 2 obtains the capability from the token object and sends it to the guardian service.
    """

    name = "op_use_hfmodel"
    help = "implement step 1 of inference using Hugging Face model"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '--kvstore_encryption_key',
            help='Encryption key for the KV store if payload is binary',
            type=str)
        
        subparser.add_argument(
            '--kvstore_input_key',
            help='Data file input key for the KV store if payload is binary',
            type=str)
        
        subparser.add_argument(
            '--kvstore_root_block_hash',
            help='KV store hashed identity if payload is binary',
            type=str)
        
        subparser.add_argument(
            '--user_inputs',
            help='User inputs for the model, used when the payload is JSON',
            type=str)

    @classmethod
    def invoke(cls, state, session_params, kvstore_encryption_key, kvstore_input_key, kvstore_root_block_hash, user_inputs, **kwargs) :
        session_params['commit'] = True

        # send the request to the contract to create a capability for the guardian
        params = {}
        params['kvstore_encryption_key'] = kvstore_encryption_key
        params['kvstore_input_key'] = kvstore_input_key
        params['kvstore_root_block_hash'] = kvstore_root_block_hash
        params['user_inputs'] = user_inputs

        message = invocation_request('use_model', **params)
        try:
            result = pcontract_cmd.send_to_contract(state,  message, **session_params)
        except Exception as e:
            raise

        cls.log_invocation(message, result)
        return result
        
        

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_get_capability(pcontract.contract_op_base) :
    """op_get_capability implements step 2 for the usage of a Hugging Face model via the guardian service
    This method carries proof of commit from ledger as input, and obtains the capability from the token object.
    Step 1 fixes all the parameters required to generate the capability.
    """

    name = "op_get_capability"
    help = "implement step 2 of inference using Hugging Face model"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-l', '--ledger-attestation',
            help='attestation from the ledger that the current state of the token issuer is committed',
            type=pbuilder.invocation_parameter, required=True)

    @classmethod
    def invoke(cls, state, session_params, ledger_attestation, **kwargs) :
        session_params['commit'] = False

        params = {}
        params['ledger_signature'] = ledger_attestation

        message = invocation_request('get_capability', **params)
        capability = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, capability)

        return capability


## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_use_hfmodel(pcommand.contract_command_base) :
    """cmd_use_hfmodel implements implements the usage of a Hugging Face model via the guardian service
    """
    name = "use_hfmodel"
    help = "inference using Hugging Face model"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '--data_file',
            help='Filename of the data_file to use as inference input. this is used only if payload is binary',
            type=str)

        subparser.add_argument(
            '--search-path',
            help='Directories to search for the data file',
            nargs='+', type=str, default=['.', './data'])
        
        subparser.add_argument(
            '--user_inputs',
            help='User inputs for the model, used when the payload is JSON',
            type=str)

    @classmethod
    def invoke(cls, state, context, data_file=None, search_path=None, user_inputs=None, **kwargs) :
        
        # ensure token has been created
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("token has not been created")

        # query the token object for model info, get the payload type, and ensure that for binary payloads
        # data file is provided, and for json payloads, user inputs are provided
        session = pbuilder.SessionParameters(save_file=save_file)
        model_info_json = pcontract.invoke_contract_op(
            op_get_modelinfo,
            state, context, session,
            **kwargs)
        model_info = json.loads(model_info_json)
        payload_type = model_info['payload_type']
        
        if payload_type == 'json' and user_inputs is None:
            raise ValueError("user inputs is required for json payloads")
        
        if payload_type == 'binary' and data_file is None:
            raise ValueError("data file is required for binary payloads")
        
        # store the data file in the KV store if binary data is provided
        if payload_type == 'binary':
            data_file = putils.find_file_in_path(data_file, search_path)
            with open(data_file, 'rb') as bf :
                data_bytes = bf.read()

            data_key = crypto.string_to_byte_array("__data__")
            data_bytes = crypto.string_to_byte_array(data_bytes)

            kv = KeyValueStore()
            with kv :
                _ = kv.set(data_key, data_bytes, input_encoding='raw', output_encoding='raw')

            kvstore_encryption_key = kv.encryption_key
            kvstore_input_key = "__data__"
            kvstore_root_block_hash = kv.hash_identity
            user_inputs  = "not_used" # this is not used in this case when payload is binary
        else:
            kvstore_encryption_key = "not_used"
            kvstore_input_key = "not_used"
            kvstore_root_block_hash = "not_used"
    
        # invoke op_use_model to store the parameters required to generate the capability
        session = pbuilder.SessionParameters(save_file=save_file)
        try:
            _ = pcontract.invoke_contract_op(
                op_use_hfmodel,
                state, context, session,
                kvstore_encryption_key, 
                kvstore_input_key, 
                kvstore_root_block_hash, 
                user_inputs,
                **kwargs)
        except Exception as e:
            cls.display_error("op_use_hfmodel method evaluation failed. {}".format(e))
            return None
        
        # get proof of commit from the ledger
        time.sleep(2) # wait for the ledger to commit the transaction, not sure if any wait is needed or the 
        # correct solution is to poll the ledger until the transaction is committed

        to_contract = pcontract_cmd.get_contract(state, save_file)
        ledger_submitter = create_submitter(state.get(['Ledger']))
        state_attestation = ledger_submitter.get_current_state_hash(to_contract.contract_id)

        # get capability from the token object
        capability = pcontract.invoke_contract_op (
            op_get_capability,
            state, context, session,
            state_attestation['signature'],
            **kwargs)

        # push data file to storage service associated with the guardian if payload is binary
        guardian_context = context.get_context('data_guardian_context')
        url = guardian_context['url']
        service_client = GuardianServiceClient(url)
        if payload_type == 'binary':
            kv.sync_to_block_store(service_client)

        # send capability to guardian service
        capability = json.loads(capability)
        result = service_client.process_capability(**capability)
        cls.display(result)
        return result

        

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_mint_hf_tokens(pcommand.contract_command_base) :
    """Mint token objects
    Wrapper around the mint_tokens operation from exchange.plugins.token_object
    to be able to specify additional arguments during initialization
    """

    name = "mint_hf_tokens"
    help = "mint tokens for a token issuer"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument('--hf_auth_token', help='Name of the contract class', type=str)
        subparser.add_argument('--hf_endpoint_url', help='Name of the enclave service group to use', type=str)
        subparser.add_argument('--fixed_model_params', help='File where contract data is stored', type=str)
        subparser.add_argument('--user_inputs_schema', help='Name of the provisioning service group to use', type=str)
        subparser.add_argument('--payload_type', help='Name of the storage service group to use', type=str)
        subparser.add_argument('--hfmodel_usage_info', help='File that contains contract source code', type=str)
        subparser.add_argument('--max_use_count', help='File that contains contract source code', type=int)

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        return pcommand.invoke_contract_cmd(cmd_mint_tokens, state, context, **kwargs)
        
        

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_get_modelinfo(pcommand.contract_command_base) :
    """cmd_get_modelinfo gets the model info for which token has been created
    the model info is entirely obtained from the token object, and does not involve calls to the 
    guardian
    """
    name = "get_modelinfo"
    help = "get model info of the Hugging Face model stored in the token object"

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError("token has not been created")

        session = pbuilder.SessionParameters(save_file=save_file)
        result = pcontract.invoke_contract_op(
            op_get_modelinfo,
            state, context, session,
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
    op_use_hfmodel,
    op_get_modelinfo,
    op_get_capability
]

do_hfmodels_token_contract = pcontract.create_shell_command('hfmodels_token_contract', __operations__)

__commands__ = [
    cmd_mint_hf_tokens,
    cmd_transfer_assets,
    cmd_use_hfmodel,
    cmd_get_modelinfo,
]

do_hfmodels_token = pcommand.create_shell_command('hfmodels_token', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'hfmodels_token', do_hfmodels_token)
    pshell.bind_shell_command(cmdclass, 'hfmodels_token_contract', do_hfmodels_token_contract)
                                                                                             