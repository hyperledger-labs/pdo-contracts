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
import json

from pdo.hfmodels.common.utility import ValidateJSON
from pdo.hfmodels.common.secrets import recv_secret
from pdo.hfmodels.operations import capability_handler_map
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
            },
        }
    }

    __operation_schema__ = {
        "type" : "object",
        "properties" : {
            "nonce" : { "type" : "string" },
            "method_name" : { "type" : "string" },
            "parameters" : { "type" : "object" },
        }
    }

    # -----------------------------------------------------------------
    def __init__(self, config, capability_store, endpoint_registry) :
        self.config = config
        self.capability_store = capability_store
        self.endpoint_registry = endpoint_registry

        self.capability_handler_map = {}
        for (op, handler) in capability_handler_map.items() :
            self.capability_handler_map[op] = handler(config)

    # -----------------------------------------------------------------
    def __call__(self, environ, start_response) :
        # unpack the request, this is WSGI magic
        try :
            request = UnpackJSONRequest(environ)
            if not ValidateJSON(request, self.__input_schema__) :
                return ErrorResponse(start_response, "invalid JSON")

            capability_key = self.capability_store.get_capability_key(request['minted_identity'])

            operation_message = recv_secret(capability_key, request['operation'])
            if not ValidateJSON(operation_message, self.__operation_schema__) :
                return ErrorResponse(start_response, "invalid JSON")

        except KeyError as ke :
            logger.error('missing field in request: %s', ke)
            return ErrorResponse(start_response, 'missing field {0}'.format(ke))
        except Exception as e :
            logger.error("unknown exception unpacking request (ProcessCapability); %s", str(e))
            return ErrorResponse(start_response, "unknown exception while unpacking request")

        # dispatch the operation
        try :
            method_name = operation_message['method_name']
            parameters = operation_message['parameters']
            logger.info("process capability operation %s with parameters %s", method_name, parameters)

            operation = self.capability_handler_map[method_name]
            operation_result = operation(parameters)
            if operation_result is None :
                return ErrorResponse(start_response, "operation failed")

        except KeyError as ke :
            logger.error('unknown operation: %s', )
            return ErrorResponse(start_response, 'missing field {0}'.format(ke))
        except Exception as e :
            logger.error("unknown exception performing operation (ProcessCapability); %s", str(e))
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
