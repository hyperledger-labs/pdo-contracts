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
import os
import sys

from pdo.contracts.common import add_context_mapping, initialize_context

_logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
_asset_type_context_ = {
    'module' : 'pdo.exchange.plugins.asset_type',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.asset_type.source}',
    'name' : 'asset_type',
    'description' : 'asset type',
    'link' : 'http://',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_vetting_context_ = {
    'module' : 'pdo.exchange.plugins.vetting',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.vetting.source}',
    'asset_type_context' : '@{..asset_type}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_issuer_context_ = {
    'module' : 'pdo.exchange.plugins.issuer',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.issuer.source}',
    'asset_type_context' : '@{..asset_type}',
    'vetting_context' : '@{..vetting}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_guardian_context_ = {
    'module' : 'pdo.exchange.plugins.guardian',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.data_guardian.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_token_issuer_context_ = {
    'module' : 'pdo.exchange.plugins.token_issuer',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.token_issuer.source}',
    'token_object_context' : '@{..token_object}',
    'vetting_context' : '@{..vetting}',
    'guardian_context' : '@{..guardian}',
    'description' : 'issuer for token',
    'token_metadata' : {
        'opaque' : '',
    },
    'count' : 10,
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_token_object_context_ = {
    'module' : 'pdo.exchange.plugins.token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.Exchange.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_order_context_ = {
    'module' : 'pdo.exchange.plugins.exchange',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.exchange.source}',
    'offer' : {
        'issuer_context' : '@{...offer.issuer}',
        'count' : 1,
    },
    'request' : {
        'issuer_context' : '@{...request.issuer}',
        'count' : 1,
    },
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

# add each of these to the global mapping
_context_map_ = {
    'asset_type' : _asset_type_context_,
    'vetting' : _vetting_context_,
    'issuer' : _issuer_context_,
    'guardian' : _guardian_context_,
    'token_issuer' : _token_issuer_context_,
    'token_object' : _token_object_context_,
    'order' : _order_context_,
}

for k, t in _context_map_.items() :
    add_context_mapping(k, t)

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
    contexts = ['asset_type', 'vetting', 'issuer']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

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
    contexts = ['asset_type', 'vetting', 'guardian', 'token_issuer', 'token_object']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

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
    contexts = ['order']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
