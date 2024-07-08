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

from pdo.hfmodels.wsgi.add_endpoint import AddEndpointApp
from pdo.hfmodels.wsgi.info import InfoApp
from pdo.hfmodels.wsgi.process_capability import ProcessCapabilityApp
from pdo.hfmodels.wsgi.provision_token_issuer import ProvisionTokenIssuerApp
from pdo.hfmodels.wsgi.provision_token_object import ProvisionTokenObjectApp


__all__ = [
    'AddEndpointApp',
    'InfoApp',
    'ProcessCapabilityApp',
    'ProvisionTokenIssuerApp',
    'ProvisionTokenObjectApp'
    ]

wsgi_operation_map = {
    'add_endpoint' : AddEndpointApp,
    'info' : InfoApp,
    'process_capability' : ProcessCapabilityApp,
    'provision_token_issuer' : ProvisionTokenIssuerApp,
    'provision_token_object' : ProvisionTokenObjectApp
    }
