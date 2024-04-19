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
import pdo.exchange.jupyter as ex_jupyter

_logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
guardian_context = jp_common.ContextTemplate('guardian', {
    'module' : 'pdo.inference.plugins.inference_guardian',
    'identity' : '${..token_issuer.identity}',
    'token_issuer_context' : '@{..token_issuer}',
    'service_only' : True,
    'url' : 'http://localhost:7900',
})

token_object_context = jp_common.ContextTemplate('token_object', {
    'module' : 'pdo.inference.plugins.inference_token_object',
    'identity' : '${..token_issuer.identity}',
    'source' : '${ContractFamily.inference.token_object.source}',
    'token_issuer_context' : '@{..token_issuer}',
    'data_guardian_context' : '@{..guardian}',
    'eservice_group' : 'default',
    'pservice_group' : 'default',
    'sservice_group' : 'default',
})

def initialize_token_context(state, bindings, context_file, prefix, **kwargs) :
    contexts = [
        ex_jupyter.asset_type_context,
        ex_jupyter.vetting_context,
        guardian_context,
        ex_jupyter.token_issuer_context,
        token_object_context
    ]
    return jp_common.initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
