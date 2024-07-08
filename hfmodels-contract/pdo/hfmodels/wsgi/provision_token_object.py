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
from pdo.hfmodels.common.secrets import send_secret, recv_secret
from pdo.common.wsgi import ErrorResponse, UnpackJSONRequest
from pdo.common.keys import EnclaveKeys

import logging
logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class ProvisionTokenObjectApp(object) :
    __secret_schema__ = {
        "type" : "object",
        "properties" : {
            "minted_identity" : { "type" : "string" },
            "token_description" : { "type" : "string" },
            "token_object_encryption_key" : { "type" : "string" },
            "token_object_verifying_key" : { "type" : "string" },
            "token_metadata": {"type" : "object" },
        },
    }

    # -----------------------------------------------------------------
    def __init__(self, config, capability_store, endpoint_registry) :
        self.capability_store = capability_store
        self.endpoint_registry = endpoint_registry

    # -----------------------------------------------------------------
    def __call__(self, environ, start_response) :
        # unpack the request, this is WSGI magic
        try :
            request = UnpackJSONRequest(environ)
            # the incoming message is in standard secret format, the session key
            # should be encrypted with the management capability key
            secret_message = recv_secret(self.capability_store.mgmt_capability_key, request)

            if not ValidateJSON(secret_message, self.__secret_schema__) :
                return ErrorResponse(start_response, "invalid JSON")

        except KeyError as ke :
            logger.error('missing field in request: %s', ke)
            return ErrorResponse(start_response, 'missing field {0}'.format(ke))
        except Exception as e :
            logger.error("unknown exception unpacking request (Invoke); %s", str(e))
            return ErrorResponse(start_response, "unknown exception while unpacking request")

        # create and save the token object capability key
        capability_key = self.capability_store.create_capability_key(secret_message['minted_identity'])
        token_object_package = dict()
        token_object_package['minted_identity'] = secret_message['minted_identity']
        token_object_package['token_description'] = secret_message['token_description']
        token_object_package['token_metadata'] = secret_message['token_metadata']
        token_object_package['capability_generation_key'] = capability_key.encryption_key


        # the provisioning package for the token object is encrypted with the
        # token object's encryption key
        token_object_keys = EnclaveKeys(
            secret_message['token_object_verifying_key'],
            secret_message['token_object_encryption_key'])
        secret_package = send_secret(token_object_keys, token_object_package)

        # create the result
        result = bytes(json.dumps(secret_package), 'utf8')
        status = "{0} {1}".format(HTTPStatus.OK.value, HTTPStatus.OK.name)
        headers = [
                   ('Content-Type', 'application/octet-stream'),
                   ('Content-Transfer-Encoding', 'utf-8'),
                   ('Content-Length', str(len(result)))
                   ]
        start_response(status, headers)
        return [result]
