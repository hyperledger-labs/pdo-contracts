#!/usr/bin/env python

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

"""
This file defines the InvokeApp class, a WSGI interface class for
handling contract method invocation requests.
"""

from http import HTTPStatus
import io
import json

from pdo.medperf.common.utility import ValidateJSON
from pdo.common.wsgi import ErrorResponse, UnpackJSONRequest

import logging
logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class AddEndpointApp(object) :

    __input_schema__ = {
        "type" : "object",
        "properties" : {
            "contract_id" : {"type" : "string"},
            "ledger_attestation" : {
                "type" : "object",
                "properties": {
                    "contract_code_hash": {"type" : "string"},
                    "metadata_hash": {"type" : "string"},
                    "signature": {"type" : "string"},
                },
            },
            "contract_metadata" : {
                "type" : "object",
                "properties": {
                    "verifying_key" : {"type" : "string"},
                    "encryption_key" : {"type" : "string"},
                }
            },
            "contract_code_metadata" : {
                "type" : "object",
                "properties" : {
                    "code_hash": {"type" : "string"},
                    "code_nonce": {"type" : "string"},
                },
            },
        },
    }

    # -----------------------------------------------------------------
    def __init__(self, config, capability_store, endpoint_registry) :
        self.capability_store = capability_store
        self.endpoint_registry = endpoint_registry
        self.code_hash = config.get("TokenIssuer", {}).get("CodeHash", "")
        self.contractIDs = config.get("TokenIssuer", {}).get("ContractIDs", [])
        self.ledger_key = config.get("TokenIssuer", {}).get("LedgerKey", "")

    # -----------------------------------------------------------------
    def __call__(self, environ, start_response) :
        try :
            request = UnpackJSONRequest(environ)
            if not ValidateJSON(request, self.__input_schema__) :
                return ErrorResponse(start_response, "invalid JSON")

            contract_id = request['contract_id']
            ledger_attestation = request['ledger_attestation']
            contract_metadata = request['contract_metadata']
            contract_code_metadata = request['contract_code_metadata']

        except KeyError as ke :
            logger.error('missing field in request: %s', ke)
            return ErrorResponse(start_response, 'missing field {0}'.format(ke))
        except Exception as e :
            logger.error("unknown exception unpacking request (Invoke); %s", str(e))
            return ErrorResponse(start_response, "unknown exception while unpacking request")

        # verify the endpoint information
        ## <TBD> ##

        ## what is the policy for allowing an endpoint to be registered?
        if self.code_hash and contract_code_metadata["code_hash"] != self.code_hash :
            return ErrorResponse(start_response, 'endpoint not authorized')
        if self.contractIDs and contract_id not in self.contractIDs :
            return ErrorResponse(start_response, 'endpoint not authorized')

        # add the endpoint to the endpoint registry
        verifying_key = contract_metadata['verifying_key']
        encryption_key = contract_metadata['encryption_key']
        self.endpoint_registry.set_endpoint(contract_id, verifying_key, encryption_key)

        # return success
        result = json.dumps({'success' : True}).encode()
        status = "{0} {1}".format(HTTPStatus.OK.value, HTTPStatus.OK.name)
        headers = [
                   ('Content-Type', 'application/json'),
                   ('Content-Length', str(len(result)))
                   ]
        start_response(status, headers)
        return [result]
