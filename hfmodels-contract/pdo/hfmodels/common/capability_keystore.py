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

import shelve

from pdo.hfmodels.common.capability_keys import CapabilityKeys

import logging
logger = logging.getLogger(__name__)

class CapabilityKeyStore(object) :

    # -------------------------------------------------------
    def __init__(self, filename = "keystore.db") :
        logger.info('create capability store in file %s', filename)
        self._keystore = shelve.open(filename, flag='c', writeback=True)
        try :
            self.mgmt_capability_key = self.get_capability_key('management_capability_key')
        except KeyError as ke:
            self.mgmt_capability_key = self.create_capability_key('management_capability_key')

        try :
            self.svc_capability_key = self.get_capability_key('service_capability_key')
        except KeyError as ke:
            self.svc_capability_key = self.create_capability_key('service_capability_key')

    # -------------------------------------------------------
    def close(self) :
        self._keystore.close()
        self._keystore = None

    # -------------------------------------------------------
    def get_capability_key(self, minted_identity) :
        (signing_key, decryption_key) = self._keystore[minted_identity]
        return CapabilityKeys.deserialize(signing_key, decryption_key)

    # -------------------------------------------------------
    def set_capability_key(self, minted_identity, capability_key) :
        (signing_key, decryption_key) = capability_key.serialize()
        self._keystore[minted_identity] = (signing_key, decryption_key)
        return capability_key

    # -------------------------------------------------------
    def create_capability_key(self, minted_identity) :
        capability_key = CapabilityKeys.create_new_keys()
        return self.set_capability_key(minted_identity, capability_key)
