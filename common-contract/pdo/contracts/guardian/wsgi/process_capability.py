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
This file defines the InvokeApp class, a WSGI interface class for
handling contract method invocation requests.
"""

from http import HTTPStatus
import importlib
import json

from pdo.contracts.guardian.common.utility import ValidateJSON
from pdo.contracts.guardian.common.secrets import recv_secret
from pdo.common.wsgi import ErrorResponse, UnpackJSONRequest

import logging
logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class ProcessCapabilityApp(object) :
    __input_schema__ = {
        "type" : "object",
        "properties" : {
            "minted_identity" : { "type" : "string" },
            "operation" : {
                "type" : "object",
                "properties" : {
                    "encrypted_session_key" : { "type" : "string" },
                    "session_key_iv" : { "type" : "string" },
                    "encrypted_message" : { "type" : "string" },
                },
                "required" : [ "encrypted_session_key", "session_key_iv", "encrypted_message" ]
            },
        },
        "required" : [ "minted_identity", "operation" ],
    }

    __operation_schema__ = {
        "type" : "object",
        "properties" : {
            "nonce" : { "type" : "string" },
            "request_identifier" : { "type" : "string" },
            "method_name" : { "type" : "string" },
            "parameters" : { "type" : "object" },
        },
        "required" : [ "nonce", "method_name", "parameters" ],
    }

    # -----------------------------------------------------------------
    def __init__(self, config, capability_store, endpoint_registry) :
        self.config = config
        self.capability_store = capability_store
        self.endpoint_registry = endpoint_registry
        self.request_registry = {}        # map of sets, used to check for duplicate requests

        try :
            operation_module_name = config['GuardianService']['Operations']
        except KeyError as ke :
            logger.error('No operation map configured')
            raise

        operation_module = importlib.import_module(operation_module_name)

        self.capability_handler_map = {}
        for (op, handler) in operation_module.capability_handler_map.items() :
            self.capability_handler_map[op] = handler(config)

    # -----------------------------------------------------------------
    def __call__(self, environ, start_response) :
        # unpack the request, this is WSGI magic
        try :
            request = UnpackJSONRequest(environ)
            if not ValidateJSON(request, self.__input_schema__) :
                return ErrorResponse(start_response, "invalid JSON, malformed request")

            minted_identity = request['minted_identity']
            capability_key = self.capability_store.get_capability_key(minted_identity)

            operation_message = recv_secret(capability_key, request['operation'])
            if not ValidateJSON(operation_message, self.__operation_schema__) :
                return ErrorResponse(start_response, "invalid JSON, malformed operation")

        except KeyError as ke :
            logger.info(f'missing field in request: {ke}')
            return ErrorResponse(start_response, f'missing field in request: {ke}')
        except Exception as e :
            logger.error(f'unknown exception unpacking request (ProcessCapability); {e}')
            return ErrorResponse(start_response, "unknown exception while unpacking request")

        # find the operation, we've already validated the JSON so no errors here
        method_name = operation_message['method_name']
        parameters = operation_message['parameters']

        logger.info("process capability operation %s with parameters %s", method_name, parameters)

        try :
            operation = self.capability_handler_map[method_name]
        except KeyError as ke :
            logger.info(f'unknown operation {ke}')
            return ErrorResponse(start_response, f'unknown operation {ke}', HTTPStatus.NOT_FOUND)

        # check for request replays
        try :
            if hasattr(operation, 'unique_requests') and operation.unique_requests is True :
                request_identifier = operation_message.get('request_identifier')
                if request_identifier is None :
                    logger.info('missing request identifier for unique operation')
                    return ErrorResponse(start_response, "missing request identifier for unique operation")

                # add the minted identity to the registry if it does not exist
                if self.request_registry.get(minted_identity) is None :
                    self.request_registry[minted_identity] = set()

                # check if the request identifier is already in the registry for this minted identity
                if request_identifier in self.request_registry[minted_identity] :
                    logger.info('duplicate request for unique operation')
                    return ErrorResponse(start_response, 'duplicate request for unique operation', HTTPStatus.UNAUTHORIZED)

                # add the request identifier to the registry for this minted identity
                self.request_registry[minted_identity].add(request_identifier)
        except Exception as e :
            logger.error(f'unexpected error checking for duplicate request; {e}')
            return ErrorResponse(start_response, "unexpected error checking for duplicate request")

        # dispatch the operation
        try :
            operation_result = operation(parameters)
            if operation_result is None :
                return ErrorResponse(start_response, "operation failed", HTTPStatus.UNPROCESSABLE_ENTITY)
        except Exception as e :
            logger.error(f'unknown exception performing operation (ProcessCapability); {e}')
            return ErrorResponse(start_response, "unknown exception while performing operation")

        # and process the result
        result = bytes(json.dumps(operation_result), 'utf8')
        status = "{0} {1}".format(HTTPStatus.OK.value, HTTPStatus.OK.name)
        headers = [
                   ('Content-Type', 'application/octet-stream'),
                   ('Content-Transfer-Encoding', 'utf-8'),
                   ('Content-Length', str(len(result)))
                   ]
        start_response(status, headers)
        return [result]
