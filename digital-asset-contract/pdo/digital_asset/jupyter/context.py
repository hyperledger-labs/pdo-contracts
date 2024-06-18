# Copyright 2024 Intel Corporation
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

import pdo.contracts.common as jp_common
import pdo.exchange.jupyter as ex_jupyter

_logger = logging.getLogger(__name__)

__all__ = [
    'guardian_context',
    'token_object_context',
    'initialize_token_context',
]

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
guardian_context = jp_common.ContextTemplate('guardian', {
    'module' : 'pdo.digital_asset.plugins.guardian',
    'identity' : "${..token_issuer.identity}",
    'source' : '${ContractFamily.DigitalAsset.data_guardian.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
    'image_file' : '${image_file}',
    'image_border' : 1,
})

token_object_context = jp_common.ContextTemplate('token_object', {
    'module' : 'pdo.digital_asset.plugins.token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.DigitalAsset.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})


# -----------------------------------------------------------------
# -----------------------------------------------------------------
def initialize_token_context(state, bindings, context_file : str, prefix : str, **kwargs) :
    """Initialize a context for minting tokens

    The context is create from asset type, vetting, guardian,
    token_issuer and token_object contexts.

    @type state: pdo.client.builder.state.State
    @param state: client state
    @type bindings: pdo.client.builder.bindings.Bindings
    @param bindings: current interpreter bindings
    @param context_file: name of the context file
    @param prefix: prefix for paths in the context
    @keyword kwargs: dictionary of string (paths) to values that override context
    @rtype: pdo.client.builder.context.Context
    @return: the initialized context
    """
    contexts = [
        ex_jupyter.asset_type_context,
        ex_jupyter.vetting_context,
        guardian_context,
        ex_jupyter.token_issuer_context,
        token_object_context
    ]
    return jp_common.initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
