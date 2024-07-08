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
Client for the guardian service frontend
"""

import json
import requests
import time
from urllib.parse import urljoin

from pdo.service_client.generic import MessageException
from pdo.service_client.generic import GenericServiceClient
from pdo.service_client.storage import StorageServiceClient
import pdo.common.keys as keys

import logging
logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## CLASS: GuardianServiceClient
## -----------------------------------------------------------------
class GuardianServiceClient(GenericServiceClient) :

    default_timeout = 20.0

    # -----------------------------------------------------------------
    def __init__(self, url) :
        super().__init__(url)
        self.session = requests.Session()
        self.session.headers.update({'x-session-identifier' : self.Identifier})
        self.request_identifier = 0

        service_info = self.get_guardian_metadata()
        self.enclave_keys = keys.EnclaveKeys(service_info['verifying_key'], service_info['encryption_key'])

        self.storage_service_url = service_info['storage_service_url']
        self.storage_service_client = StorageServiceClient(self.storage_service_url)
        # ensure the local storage service used by the guardian service is running before starting the
        # guardian service.
        self._attach_storage_service_(self.storage_service_client)

    # -----------------------------------------------------------------
    @property
    def verifying_key(self) :
        return self.enclave_keys.verifying_key

    # -----------------------------------------------------------------
    @property
    def encryption_key(self) :
        return self.enclave_keys.encryption_key

    # -------------------------------------------------------
    def _attach_storage_service_(self, storage_service) :
        self.storage_service_verifying_key = storage_service.verifying_key

        self.get_block = storage_service.get_block
        self.get_blocks = storage_service.get_blocks
        self.store_block = storage_service.store_block
        self.store_blocks = storage_service.store_blocks
        self.check_block = storage_service.check_block
        self.check_blocks = storage_service.check_blocks

    # -----------------------------------------------------------------
    def __post_request__(self, path, request) :

        try :
            url = urljoin(self.ServiceURL, path)
            while True :
                response = self.session.post(url, json=request, timeout=self.default_timeout, stream=False)
                if response.status_code == 429 :
                    logger.info('prepare to resubmit the request')
                    sleeptime = min(1.0, float(response.headers.get('retry-after', 1.0)))
                    time.sleep(sleeptime)
                    continue

                response.raise_for_status()
                return response.json()

        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e :
            logger.warn('network error connecting to service (%s); %s', path, str(e))
            raise MessageException(str(e)) from e

    # -----------------------------------------------------------------
    def __get_request__(self, path) :

        try :
            url = urljoin(self.ServiceURL, path)
            while True :
                response = self.session.get(url, timeout=self.default_timeout)
                if response.status_code == 429 :
                    logger.info('prepare to resubmit the request')
                    sleeptime = min(1.0, float(response.headers.get('retry-after', 1.0)))
                    time.sleep(sleeptime)
                    continue

                response.raise_for_status()
                return response.json()

        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e :
            logger.warn('network error connecting to service (%s); %s', path, str(e))
            raise MessageException(str(e)) from e

    # -----------------------------------------------------------------
    def get_guardian_metadata(self) :
        return self.__get_request__('info')

    # -----------------------------------------------------------------
    def add_endpoint(self, **params) :
        return self.__post_request__('add_endpoint', params)

    # -----------------------------------------------------------------
    def provision_token_issuer(self, **params) :
        return self.__post_request__('provision_token_issuer', params)

    # -----------------------------------------------------------------
    def provision_token_object(self, **params) :
        return self.__post_request__('provision_token_object', params)

    # -----------------------------------------------------------------
    def process_capability(self, **params) :
        return self.__post_request__('process_capability', params)
