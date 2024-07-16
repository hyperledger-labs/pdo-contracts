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
from pdo.hfmodels.common.secrets import send_secret
from pdo.common.wsgi import ErrorResponse, UnpackJSONRequest
import pdo.common.crypto as crypto

import logging
logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class ProvisionTokenIssuerApp(object) :
    __input_schema__ = {
        "type" : "object",
        "properties" : {
            "contract_id" : {"type" : "string"},
        }
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
            if not ValidateJSON(request, self.__input_schema__) :
                return ErrorResponse(start_response, "invalid JSON")

            contract_id = request['contract_id']
            issuer_keys = self.endpoint_registry.get_endpoint(contract_id)

        except Exception as e :
            logger.error("unknown exception unpacking request (Invoke); %s", str(e))
            return ErrorResponse(start_response, "unknown exception while unpacking request")

        # get the keys
        provisioning_secret = dict()
        provisioning_secret['capability_management_key'] = self.capability_store.mgmt_capability_key.encryption_key
        provisioning_package = send_secret(issuer_keys, provisioning_secret)

        # return success
        result = json.dumps(provisioning_package).encode()
        status = "{0} {1}".format(HTTPStatus.OK.value, HTTPStatus.OK.name)
        headers = [
                   ('Content-Type', 'application/json'),
                   ('Content-Length', str(len(result)))
                   ]
        start_response(status, headers)
        return [result]
