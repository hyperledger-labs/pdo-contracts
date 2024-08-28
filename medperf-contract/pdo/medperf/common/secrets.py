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

import json

from pdo.medperf.common.utility import ValidateJSON
import pdo.common.crypto as crypto

import logging
logger = logging.getLogger(__name__)

__all__ = [ 'recv_secret', 'send_secret' ]

__secret_schema__ = {
    "type" : "object",
    "properties" : {
        "encrypted_session_key" : { "type" : "string" },
        "session_key_iv" : { "type" : "string" },
        "encrypted_message" : { "type" : "string" },
    },
}


# -----------------------------------------------------------------
# -----------------------------------------------------------------
def recv_secret(capability_key, secret) :
    """Process an incoming secret

    :param capability_key pdo.medperf.common.capability_keys.CapabilityKeys: decryption key
    :param secret str: the secret to be unpacked
    :returns dict: the parsed json message in the secret
    """

    if not ValidateJSON(secret, __secret_schema__) :
        return None                       # throw exception?

    encrypted_session_key = crypto.base64_to_byte_array(secret['encrypted_session_key'])
    session_key = capability_key.decrypt(encrypted_session_key, encoding='raw')
    session_iv = crypto.base64_to_byte_array(secret['session_key_iv'])
    cipher = crypto.base64_to_byte_array(secret['encrypted_message'])
    raw_message = crypto.SKENC_DecryptMessage(session_key, session_iv, cipher)
    message = crypto.byte_array_to_string(raw_message)

    return json.loads(message)


# -----------------------------------------------------------------
# send_secret
# -----------------------------------------------------------------
def send_secret(capability_key, message) :
    """Create a secret for transmission

    :param capability_key pdo.medperf.common.capability_keys.CapabilityKeys: decryption key
    :param message dict: dictionary that will be encrypted as JSON in the secret
    :returns dict: the secret
    """

    session_key = crypto.SKENC_GenerateKey()
    session_iv = crypto.SKENC_GenerateIV()
    serialized_message = crypto.string_to_byte_array(json.dumps(message))
    cipher = crypto.SKENC_EncryptMessage(session_key, session_iv, serialized_message)
    encrypted_session_key = capability_key.encrypt(session_key)

    result = dict()
    result['encrypted_session_key'] = crypto.byte_array_to_base64(encrypted_session_key)
    result['session_key_iv'] = crypto.byte_array_to_base64(session_iv)
    result['encrypted_message'] = crypto.byte_array_to_base64(cipher)

    return result
