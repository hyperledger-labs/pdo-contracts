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

import hashlib
import random
import yaml
import subprocess
from pdo.medperf.common.utility import ValidateJSON
from pdo.common.key_value import KeyValueStore

import logging
import requests
import urllib.request
import json
import os
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
        model_ids_to_evaluate = params['model_ids_to_evaluate']
        
        mlcube_script_path = "/home/wenyi1/medperf/test_resource/test.sh"
        result_path = "/home/wenyi1/medperf/test_resource/test_results"

        test_message = "Hello from the guardian service."
        # put the parameters in test_message and return
        # for testing purpose
        test_message += f"\nReceived order for:"
        test_message += f"\nDataset ID: {dataset_id}"
        test_message += f"\nModel IDs : {model_ids_to_evaluate}"
        print(test_message)
        print("================================================")
        print("Evaluating models...")
        # split model_ids_to_evaluate into a list of integers
        model_ids = model_ids_to_evaluate.split(',')
        model_ids = [int(i) for i in model_ids]
        
        for model in model_ids:
            if model == 1 or model == 2:
                print(f"Cubes available for model {model}, running the MLCube script...")
                # run the MLCube script with parameter model
                # os.system(f"bash {mlcube_script_path} {model}")
                output_result = subprocess.run(["bash", mlcube_script_path, str(model)], capture_output=True, text=True)
                print(output_result.stdout)
            else:
                print(f"Model {model} not available. Generating simulated data...")
                # generate simulated data
                sim_data = {'AUC': random.uniform(0.5, 1), 'Accuracy': random.uniform(0.5, 1)} 
                with open(f"{result_path}/{str(model)}.yaml", 'w') as file:
                    yaml.dump(sim_data, file)
                print(f"Simulated data for model {model} generated successfully.")
        
        print("================================================")
        print("Signing each file with simple SHA256 and challenge...")
        # handle each model result
        for model in model_ids:
            try:
                with open(f"{result_path}/{str(model)}.yaml", 'r+') as file:
                    result_data = yaml.safe_load(file)
                    hash_result = self.simpleSHA256withChallenge(kvstore_input_key, result_data)
                    new_data = {"hash": hash_result}
                    yaml.dump(new_data, file)
                    print(f"Model {model} result signed successfully.")
            except Exception as e:
                print(f"Error signing model {model} result: {e}")
                continue
        return test_message
    
    def simpleSHA256withChallenge(self, challenge, result_data):
        # parse result_data to string
        result_data_string = json.dumps(result_data)
        return hashlib.sha256(challenge.encode() + result_data_string.encode()).hexdigest()