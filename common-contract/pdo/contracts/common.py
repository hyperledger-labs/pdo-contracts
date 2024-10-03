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

import copy
import logging
import typing

import pdo.client.builder as pbuilder

_logger = logging.getLogger(__name__)

"""Internal routines
"""

# -----------------------------------------------------------------
# the base context provides information that appears to be common
# across all contexts; contexts can reference the values in the
# base context to simplify consistent configuration
# -----------------------------------------------------------------
_base_context_ = {
    'identity' : None,
    'service_group' : 'default',          # the assumption here is that [eps]service groups all have the same name
    'eservice_group' : '${.service_group}',
    'pservice_group' : '${.service_group}',
    'sservice_group' : '${.service_group}',
}

# -----------------------------------------------------------------
# set up the context
# -----------------------------------------------------------------
class ContextTemplate(object) :
    """Capture information for a context template

    A context template captures configuration information
    generally associated with a specific contract class. For
    the moment this is very simple.
    """

    def __init__(self, key, template) :
        self.key = key
        self.template = copy.deepcopy(template)

# -----------------------------------------------------------------
# initialize_context
# -----------------------------------------------------------------
def initialize_context(
    state,
    bindings,
    context_file : str,
    prefix : str,
    contexts : typing.List[ContextTemplate],
    **kwargs) -> pbuilder.Context :

    # attempt to load the context from the context file
    try :
        pbuilder.Context.LoadContextFile(state, bindings, context_file, prefix=prefix)
    except :
        _logger.warning('failed to load context from {}'.format(context_file))

    context =  pbuilder.Context(state, prefix)
    if not context.has_key('initialized') :
        # initialize the base context with common keys
        for k, v in _base_context_.items() :
            context.set(k, copy.deepcopy(v))

        for c in contexts :
            context.set(c.key, copy.deepcopy(c.template))

        context.set('initialized', True)

    # even if the context is initialized, override the bindings
    # this is useful for personalizing a context for a contract
    # that already exists (like using a different identity)
    for (k, v) in kwargs.items() :
        context.set(k, v)

    return context
