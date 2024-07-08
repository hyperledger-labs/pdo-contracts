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

import os

import pdo.common.crypto as crypto
import pdo.common.keys as keys

import logging
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class CapabilityKeys(keys.ServiceKeys) :

    # -------------------------------------------------------
    @classmethod
    def create_new_keys(cls) :
        signing_key = crypto.SIG_PrivateKey()
        signing_key.Generate()
        decryption_key = crypto.PKENC_PrivateKey()
        decryption_key.Generate()

        return cls(signing_key, decryption_key)

    # -------------------------------------------------------
    @classmethod
    def deserialize(cls, serialized_signing_key, serialized_decryption_key) :
        signing_key = crypto.SIG_PrivateKey(serialized_signing_key)
        decryption_key = crypto.PKENC_PrivateKey(serialized_decryption_key)
        return cls(signing_key, decryption_key)

    # -------------------------------------------------------
    def __init__(self, signing_key, decryption_key) :
        super().__init__(signing_key)
        self._decryption_key = decryption_key
        self._encryption_key = decryption_key.GetPublicKey()

    # -------------------------------------------------------
    @property
    def encryption_key(self) :
        return self._encryption_key.Serialize()

    # -------------------------------------------------------
    @property
    def decryption_key(self) :
        return self._decryption_key.Serialize()

    # -------------------------------------------------------
    def serialize(self) :
        return (self.signing_key, self.decryption_key)

    # -------------------------------------------------------
    def encrypt(self, message, encoding = 'raw') :
        """
        encrypt a message to send privately to the enclave

        :param message: text to encrypt
        :param encoding: encoding for the encrypted cipher text, one of raw, hex, b64
        """

        if type(message) is bytes :
            message_byte_array = message
        elif type(message) is tuple :
            message_byte_array = message
        else :
            message_byte_array = bytes(message, 'ascii')

        encrypted_byte_array = self._encryption_key.EncryptMessage(message_byte_array)
        if encoding == 'raw' :
            encoded_bytes = encrypted_byte_array
        elif encoding == 'hex' :
            encoded_bytes = crypto.byte_array_to_hex(encrypted_byte_array)
        elif encoding == 'b64' :
            encoded_bytes = crypto.byte_array_to_base64(encrypted_byte_array)
        else :
            raise ValueError('unknown encoding; {0}'.format(encoding))

        return encoded_bytes

    # -------------------------------------------------------
    def decrypt(self, message, encoding = 'raw') :
        """
        encrypt a message to send privately to the enclave

        :param message: text to encrypt
        :param encoding: encoding for the encrypted cipher text, one of raw, hex, b64
        """

        if type(message) is bytes :
            message_byte_array = message
        elif type(message) is tuple :
            message_byte_array = message
        else :
            message_byte_array = bytes(message, 'ascii')

        decrypted_byte_array = self._decryption_key.DecryptMessage(message_byte_array)
        if encoding == 'raw' :
            encoded_bytes = decrypted_byte_array
        elif encoding == 'hex' :
            encoded_bytes = crypto.byte_array_to_hex(decrypted_byte_array)
        elif encoding == 'b64' :
            encoded_bytes = crypto.byte_array_to_base64(decrypted_byte_array)
        else :
            raise ValueError('unknown encoding; {0}'.format(encoding))

        return encoded_bytes
