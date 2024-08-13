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

from pdo.medperf.common.utility import ValidateJSON
from pdo.common.key_value import KeyValueStore

import logging
import requests
import urllib.request
import json
logger = logging.getLogger(__name__)


## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class DataOperation(object) :
    # -----------------------------------------------------------------
    __schema__ = {
        "type" : "object",
        "properties" : {
            "kvstore_encryption_key" : { "type" : "string" },
            "kvstore_root_block_hash" : { "type" : "string" },
            "kvstore_input_key" : { "type" : "string" },
            "dataset_id" : { "type" : "string" },
            "experiment_id" : { "type" : "string" },
            # "payload_type" : { "type" : "string" },
            # "user_inputs" : { "type" : "string" },
            # "user_inputs_schema" : { "type" : "string" },
            "associated_model_ids" : { "type" : "string" },
        }
    }


    # -----------------------------------------------------------------
    def __init__(self, config) :
        pass

    # @staticmethod
    # def inference_dataset(experiment_id, dataset_id, payload, payload_type='json'):
    #     """ 
    #     Utility function to query the Hugging Face model and get response. 
    #     If the guardian is deployed in a network with a proxy, the proxy settings are automatically picked up 
    #     as long as the proxy is set in the environment variables.   

    #     payload_type is either json or binary. If binary, the payload is expected to be a byte string.
    #     If json, the payload is expected to be a dictionary. binary payloads are used for image/audio inputs, 
    #     while json payloads are used for text inputs (e.g. used while working with language models).

    #     For example usages, refer to https://huggingface.co/docs/api-inference/en/detailed_parameters

    #     """
    #     headers = {"Authorization": f"Bearer {dataset_id}"}
    #     try:
    #         if payload_type == 'json':
    #             response = requests.post(experiment_id, headers=headers, json=payload, proxies=urllib.request.getproxies())
    #         elif payload_type == 'binary':
    #             response = requests.post(experiment_id, headers=headers, data=payload, proxies=urllib.request.getproxies())
    #         else:
    #             logger.error("Invalid payload type. Supported types are 'json' and 'binary'")
    #             return None
    #     except Exception as e:
    #         logger.error(f"Request failed: {e}")
    #         return None
        
    #     if payload_type == 'binary':
    #         return json.loads(response.content.decode("utf-8"))
        
    #     return response.json()
        

    # -----------------------------------------------------------------
    def __call__(self, params) :
        if not ValidateJSON(params, self.__schema__) :
            return None

        # get the parameters
        kvstore_encryption_key = params['kvstore_encryption_key']
        kvstore_root_block_hash = params['kvstore_root_block_hash']
        kvstore_input_key = params['kvstore_input_key']
        dataset_id = params['dataset_id']
        experiment_id = params['experiment_id']
        # payload_type = params['payload_type']
        # user_inputs = json.loads(params['user_inputs'])
        # user_inputs_schema = json.loads(params['user_inputs_schema'])
        associated_model_ids = params['associated_model_ids']
        
        
        # # If payload type is binary, get the input data from the key-value store.
        # if payload_type == 'binary':
        #     kv = KeyValueStore(kvstore_encryption_key, kvstore_root_block_hash)
        #     with kv:
        #         input_data = kv.get(kvstore_input_key, output_encoding='raw')
        #     payload = bytes(input_data)
        # elif payload_type == 'json':
        #     # check schema of user inputs, and generate payload by merging user inputs with fixed model parameters
        #     if not ValidateJSON(user_inputs, user_inputs_schema) :
        #         logger.error("Invalid user inputs")
        #         return None
        #     payload = {**associated_model_ids, **user_inputs}
        # else:
        #     logger.error("Invalid payload type. Supported types are 'json' and 'binary'")
        #     return None

        # query the Hugging Face model and return the response
        # return self.query_hf_model(experiment_id, dataset_id, payload, payload_type)
        
        test_message = "Hello from the guardian service. Assume the experiment has been run successfully."
        # put the parameters in test_message and return
        # for testing purpose
        test_message += f"\nDataset ID: {dataset_id}"
        test_message += f"\nExperiment ID: {experiment_id}"
        test_message += f"\nAssociated Model IDs: {associated_model_ids}"
        return test_message
    
        # to do: (Support for post processing)
        # Add support for optionally encrypting response before sending back to the client
        # encryption key specified by token object
        # token object can implement policies for endorsing encryption keys
        # for example: results encrypted for use within another PDO contract or even the token object itself
        # Such a feature can be used for privacy-preserving post processing of the model outputs
        # before sharing final results with the client
        # If there are generic post processing steps that can be applied to a large class of models, 
        # the code can be added here itself. 
        