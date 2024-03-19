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
asset_type_context = {
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

vetting_context = {
    'module' : 'pdo.exchange.plugins.vetting',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.vetting.source}',
    'asset_type_context' : '@{..asset_type}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

issuer_context = {
    'module' : 'pdo.exchange.plugins.issuer',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.issuer.source}',
    'asset_type_context' : '@{..asset_type}',
    'vetting_context' : '@{..vetting}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

guardian_context = {
    'module' : 'pdo.inference.plugins.inference_guardian',
    'identity' : '${..token_issuer.identity}',
    'token_issuer_context' : '@{..token_issuer}',
    'service_only' : True,
    'url' : 'http://localhost:7900',
}

token_issuer_context = {
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

token_object_context = {
    'module' : 'pdo.inference.plugins.inference_token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.inference.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

order_context = {
    'module' : 'pdo.exchange.plugins.exchange',
    'identity' : None,
    'source' : '${ContractFamily.Exchange.exchange.source}',
    'offer' : {
        'issuer_context' : '@{context.${offer_issuer}}',
        'count' : 1,
    },
    'request' : {
        'issuer_context' : '@{context.${request_issuer}}',
        'count' : 1,
    },
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
}

_context_map_ = {
    'asset_type' : asset_type_context,
    'vetting' : vetting_context,
    'issuer' : issuer_context,
    'guardian' : guardian_context,
    'token_issuer' : token_issuer_context,
    'token_object' : token_object_context,
    'order' : order_context,
}

for k, t in _context_map_.items() :
    add_context_mapping(k, t)

def initialize_asset_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = ['asset_type', 'vetting', 'issuer']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_token_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = ['asset_type', 'vetting', 'guardian', 'token_issuer', 'token_object']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)

def initialize_order_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = ['order']
    return initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
