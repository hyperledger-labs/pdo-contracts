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

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.exchange.plugins.asset_type as asset_type

__all__ = [
    'op_initialize',
    'do_policy_agent',
    'do_policy_agent_contract',
    'load_commands',
]

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = "initialize an credential type contract object"

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('initialize')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_(pcontract.contract_op_base) :

    name = ""
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        pass

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_initialize,
]

do_policy_agent_contract = pcontract.create_shell_command('policy_agent_contract', __operations__)

__commands__ = [
]

do_policy_agent = pcommand.create_shell_command('policy_agent', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'policy_agent', do_policy_agent)
    pshell.bind_shell_command(cmdclass, 'policy_agent_contract', do_policy_agent_contract)
