#!/usr/bin/env python

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

"""
medperf guardian plugins
"""

import json
import logging
logger = logging.getLogger(__name__)

import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
from pdo.client.builder import invocation_parameter

from pdo.medperf.common.guardian_service import GuardianServiceClient

__all__ = [
    'op_provision_token_issuer',
    'op_provision_token_object',
    'op_process_capability',
    'op_add_endpoint',
    'cmd_provision_token_issuer',
    'cmd_provision_token_object',
    'do_medperf_guardian',
    'do_medperf_guardian_service',
    'load_commands',
]

## -----------------------------------------------------------------
## add_endpoint
## -----------------------------------------------------------------
class op_add_endpoint(pcontract.contract_op_base) :

    name = "add_endpoint"
    help = "add an attested contract object endpoint to the contract"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--code-metadata',
            help='contract code metadata',
            type=invocation_parameter,
            required=True)
        subparser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)
        subparser.add_argument(
            '-l', '--ledger-attestation',
            help='attestation from the ledger',
            type=invocation_parameter,
            required=True)
        subparser.add_argument(
            '-m', '--contract-metadata',
            help='contract metadata',
            type=invocation_parameter,
            required=True)
        subparser.add_argument(
            '-u', '--url',
            help='URL for the guardian service',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, contract_id, ledger_attestation, contract_metadata, code_metadata, url, **kwargs) :

        params = dict()
        params['contract_id'] = contract_id
        params['ledger_attestation'] = ledger_attestation
        params['contract_metadata'] = contract_metadata
        params['contract_code_metadata'] = code_metadata

        service_client = GuardianServiceClient(url)
        result = service_client.add_endpoint(**params)

        return result

## -----------------------------------------------------------------
## provision_token_issuer
## -----------------------------------------------------------------
class op_provision_token_issuer(pcontract.contract_op_base) :

    name = "provision_token_issuer"
    help = "provision the token issuer with the capability management key"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)
        subparser.add_argument(
            '-u', '--url',
            help='URL for the medperf guardian service',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, contract_id, url, **kwargs) :
        params = dict()
        params['contract_id'] = contract_id

        service_client = GuardianServiceClient(url)
        raw_result = service_client.provision_token_issuer(**params)
        result = json.dumps(raw_result)
        return result

## -----------------------------------------------------------------
## provision_token_object
## -----------------------------------------------------------------
class op_provision_token_object(pcontract.contract_op_base) :

    name = "provision_token_object"
    help = "provision a token object with an identity and capability generation key"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-p', '--provisioning-package',
            help='contract secret containing the provisioning package',
            type=invocation_parameter,
            required=True)
        subparser.add_argument(
            '-u', '--url',
            help='URL for the medperf guardian service',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, provisioning_package, url, **kwargs) :
        params = provisioning_package

        service_client = GuardianServiceClient(url)
        raw_result = service_client.provision_token_object(**params)
        result = json.dumps(raw_result)
        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_process_capability(pcontract.contract_op_base) :

    name = "process_capability"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--capability',
            help='capability generated by the token object create operation interface',
            required=True)
        subparser.add_argument(
            '-u', '--url',
            help='URL for the medperf guardian service',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, session_params, capability, url, **kwargs) :
        params = capability

        service_client = GuardianServiceClient(url)
        raw_result = service_client.process_capability(**params)
        result = json.dumps(raw_result)
        return result

# -----------------------------------------------------------------
# provision a token issuer
# -----------------------------------------------------------------
class cmd_provision_token_issuer(pcommand.contract_command_base) :
    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-c', '--code-metadata',
            help='contract code metadata',
            required=True)
        subparser.add_argument(
            '-i', '--contract-id',
            help='contract identifier',
            type=str, required=True)
        subparser.add_argument(
            '-l', '--ledger-attestation',
            help='attestation from the ledger',
            required=True)
        subparser.add_argument(
            '-m', '--contract-metadata',
            help='contract metadata',
            required=True)
        subparser.add_argument(
            '-u', '--url',
            help='URL for the medperf guardian service',
            type=str)

    @classmethod
    def invoke(cls, state, context, contract_id, ledger_attestation, contract_metadata, code_metadata, url=None, **kwargs) :

        if url is None :
            url = context['url']

        session = None
        pcontract.invoke_contract_op(
            op_add_endpoint,
            state, context, session,
            contract_id,
            ledger_attestation,
            contract_metadata,
            code_metadata,
            url)

        provisioning_package = pcontract.invoke_contract_op(
            op_provision_token_issuer,
            state, context, session,
            contract_id,
            url)

        cls.display('provisioned guardian for token issuer {}'.format(url))
        return json.loads(provisioning_package)

# -----------------------------------------------------------------
# provision a token object
# -----------------------------------------------------------------
class cmd_provision_token_object(pcommand.contract_command_base) :
    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-p', '--provisioning-package',
            help='contract secret containing the provisioning package',
            required=True)
        subparser.add_argument(
            '-u', '--url',
            help='URL for the medperf guardian service',
            type=str, required=True)

    @classmethod
    def invoke(cls, state, context,  provisioning_package, url=None, **kwargs) :

        if url is None :
            url = context['url']

        session = None
        to_package = pcontract.invoke_contract_op(
            op_provision_token_object,
            state, context, session,
            provisioning_package,
            url,
            **kwargs)

        cls.display('provisioned token object for guardian {}'.format(url))
        return json.loads(to_package)


## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_provision_token_issuer,
    op_provision_token_object,
    op_process_capability,
    op_add_endpoint,
]

do_medperf_guardian_service = pcontract.create_shell_command('medperf_guardian_service', __operations__)

__commands__ = [
    cmd_provision_token_issuer,
    cmd_provision_token_object,
]

do_medperf_guardian = pcommand.create_shell_command('medperf_guardian', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'medperf_guardian', do_medperf_guardian)
    pshell.bind_shell_command(cmdclass, 'medperf_guardian_service', do_medperf_guardian_service)