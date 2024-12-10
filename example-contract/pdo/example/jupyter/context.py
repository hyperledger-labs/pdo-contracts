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
    'counter_context',
    'initialize_counter_context',
]

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
counter_context = jp_common.ContextTemplate('counter', {
    'module' : 'pdo.example.plugins.counter',
    'identity' : '${..identity}',
    'source' : '${ContractFamily.Example.counter.source}',
    'eservice_group' : '${..eservice_group}',
    'pservice_group' : '${..pservice_group}',
    'sservice_group' : '${..sservice_group}',
})

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def initialize_counter_context(state, bindings, context_file : str, prefix : str, **kwargs) :
    """Initialize a context for counters

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
        counter_context,
    ]
    return jp_common.initialize_context(state, bindings, context_file, prefix, contexts, **kwargs)
