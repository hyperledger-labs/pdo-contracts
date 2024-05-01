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

import pdo.contracts.common as jp_common

_logger = logging.getLogger(__name__)

__all__ = [
  'asset_type_context',
  'vetting_context',
  'issuer_context',
  'guardian_context',
  'token_issuer_context',
  'token_object_context',
  'order_context',
  'initialize_asset_context',
  'initialize_token_context',
  'initialize_order_context',
]

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
asset_type_context = jp_common.ContextTemplate('asset_type', {
    'module' : 'pdo.exchange.plugins.asset_type',
    'identity' : '${..identity}',
    'source' : '${ContractFamily.Exchange.asset_type.source}',
    'name' : 'asset_type',
    'description' : 'asset type',
    'link' : 'http://',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

vetting_context = jp_common.ContextTemplate('vetting', {
    'module' : 'pdo.exchange.plugins.vetting',
    'identity' : '${..identity}',
    'source' : '${ContractFamily.Exchange.vetting.source}',
    'asset_type_context' : '@{..asset_type}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

issuer_context = jp_common.ContextTemplate('issuer', {
    'module' : 'pdo.exchange.plugins.issuer',
    'identity' : '${..identity}',
    'source' : '${ContractFamily.Exchange.issuer.source}',
    'asset_type_context' : '@{..asset_type}',
    'vetting_context' : '@{..vetting}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

guardian_context = jp_common.ContextTemplate('guardian', {
    'module' : 'pdo.exchange.plugins.guardian',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.data_guardian.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

token_issuer_context = jp_common.ContextTemplate('token_issuer', {
    'module' : 'pdo.exchange.plugins.token_issuer',
    'identity' : '${..identity}',
    'source' : '${ContractFamily.Exchange.token_issuer.source}',
    'token_object_context' : '@{..token_object}',
    'vetting_context' : '@{..vetting}',
    'guardian_context' : '@{..guardian}',
    'description' : 'issuer for token',
    'token_metadata' : {
        'opaque' : '',
    },
    'count' : 10,
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

token_object_context = jp_common.ContextTemplate('token_object', {
    'module' : 'pdo.exchange.plugins.token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

order_context = jp_common.ContextTemplate('exchange', {
    'module' : 'pdo.exchange.plugins.exchange',
    'identity' : '${..identity}',
    'source' : '${ContractFamily.Exchange.exchange.source}',
    'offer' : {
        'issuer_context' : '@{...offer.issuer}',
        'count' : 1,
    },
    'request' : {
        'issuer_context' : '@{...request.issuer}',
        'count' : 1,
    },
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

def initialize_asset_context(state, bindings, context_file : str, prefix : str, **kwargs) :
    """Initialize a context for issuing assets

    The context is create from asset type, vetting and issuer contexts.

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
    contexts = [asset_type_context, vetting_context, issuer_context]
    return jp_common.initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

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
    contexts = [asset_type_context, vetting_context, guardian_context, token_issuer_context, token_object_context]
    return jp_common.initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_order_context(state, bindings, context_file, prefix, **kwargs) :
    """Initialize a context for creating an order to exchange assets

    The context is create from order context.

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
    contexts = [order_context]
    return jp_common.initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
