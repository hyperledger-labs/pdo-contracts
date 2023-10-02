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
logger = logging.getLogger(__name__)

import pdo.common.crypto as pcrypto
from pdo.contract import ContractCode
from pdo.contract import invocation_request
from pdo.submitter.create import create_submitter

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.exchange.plugins.guardian as guardian_base

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
    'do_da_guardian',
    'do_da_guardian_contract',
    'load_commands',
]

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## inherited operations
## -----------------------------------------------------------------
op_add_endpoint = guardian_base.op_add_endpoint
op_get_contract_code_metadata = guardian_base.op_get_contract_code_metadata
op_get_contract_metadata = guardian_base.op_get_contract_metadata
op_get_ledger_key = guardian_base.op_get_ledger_key
op_get_verifying_key = guardian_base.op_get_verifying_key

op_provision_token_issuer = guardian_base.op_provision_token_issuer
op_provision_token_object = guardian_base.op_provision_token_object
op_process_capability = guardian_base.op_process_capability

cmd_provision_token_issuer = guardian_base.cmd_provision_token_issuer
cmd_provision_token_object = guardian_base.cmd_provision_token_object

## -----------------------------------------------------------------
## initialize
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize the guardian for an image"

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
        parser.add_argument(
            '-i', '--image',
            help="name of the file containing the image",
            type=str, required=True)
        parser.add_argument(
            '-b', '--border',
            help="size of the hidden border for public images",
            type=int, default=5)

    @classmethod
    def invoke(cls, state, session_params, code_hash, token_issuer_code, ledger_key, image, border, **kwargs) :
        session_params['commit'] = True

        gparams = {}
        gparams['ledger_verifying_key'] = ledger_key

        if code_hash :
            gparams['token_issuer_code_hash'] = code_hash
        elif token_issuer_code :
            source_path = state.get(['Contract', 'SourceSearchPath'])
            (contract_class, contract_source) = token_issuer_code
            contract_code = ContractCode.create_from_file(
                contract_class, contract_source, source_path, interpreter='wawaka')

            message = contract_code.code + contract_code.name
            code_hash = pcrypto.compute_message_hash(pcrypto.string_to_byte_array(message))
            gparams['token_issuer_code_hash'] = pcrypto.byte_array_to_base64(code_hash)
        else :
            raise ValueError("missing required parameter; must specify verifying key")

        with open(image, 'rb') as fp:
            image_data = fp.read()

        params = {}
        params['guardian'] = gparams
        params['public_border_width'] = border
        params['encoded_image'] = pcrypto.byte_array_to_base64(image_data)

        message = invocation_request('initialize', **params)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

# -----------------------------------------------------------------
# create the guardian
# -----------------------------------------------------------------
class cmd_create_guardian(pcommand.contract_command_base) :
    """Create and initialize a digital asset guardian contract object

    Initialization of the digital asset contract object includes initialization
    of the asset itself. The image
    """
    name = "create"
    help = "create a guardian for a digital asset"

    @classmethod
    def add_arguments(cls, parser) :
        parser.add_argument('-i', '--image', help="name of the file containing the image", type=str)
        parser.add_argument('-b', '--border', help="size of the hidden border for public images", type=int)

        parser.add_argument('-c', '--contract-class', help='Name of the contract class', type=str)
        parser.add_argument('-e', '--eservice-group', help='Name of the enclave service group to use', type=str)
        parser.add_argument('-f', '--save-file', help='File where contract data is stored', type=str)
        parser.add_argument('-p', '--pservice-group', help='Name of the provisioning service group to use', type=str)
        parser.add_argument('-r', '--sservice-group', help='Name of the storage service group to use', type=str)
        parser.add_argument('--source', help='File that contains contract source code', type=str)
        parser.add_argument('--extra', help='Extra data associated with the contract file', nargs=2, action='append')

    @classmethod
    def invoke(cls, state, context, image=None, border=None, **kwargs) :
        if pcontract_cmd.get_contract_from_context(state, context) :
            return

        # parameters
        if image is None :
            image = context['image_file']
        if border is None or border is 0 :
            border = context['image_border'] or 10

        # need the ledger key as the root of trust for binding to the issuer
        ledger_submitter = create_submitter(state.get(['Ledger']))
        ledger_key = ledger_submitter.get_ledger_info()

        # create the guardian contract
        save_file = pcontract_cmd.create_contract_from_context(state, context, 'da_guardian', **kwargs)
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
            image,
            border,
            **kwargs)

        cls.display('created guardian in {}'.format(save_file))
        return save_file

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

do_da_guardian_contract = pcontract.create_shell_command('da_guardian_contract', __operations__)

__commands__ = [
    cmd_create_guardian,
    cmd_provision_token_issuer,
    cmd_provision_token_object,
]

do_da_guardian = pcommand.create_shell_command('da_guardian', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'da_guardian', do_da_guardian)
    pshell.bind_shell_command(cmdclass, 'da_guardian_contract', do_da_guardian_contract)
