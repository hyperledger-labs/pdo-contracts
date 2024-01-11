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

from pdo.inference.common.utility import ValidateJSON
from pdo.common.key_value import KeyValueStore

from pdo.inference.model_scoring_scripts import model_scoring_scripts_map
from pdo.inference.common.ovms_predict import OVMSPredict

import logging
logger = logging.getLogger(__name__)


## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class InferenceOperation(OVMSPredict) :
    # -----------------------------------------------------------------
    __schema__ = {
        "type" : "object",
        "properties" : {
            "encryption_key" : { "type" : "string" },
            "state_hash" : { "type" : "string" },
            "image_key" : { "type" : "string" },
        }
    }


    # -----------------------------------------------------------------
    def __init__(self, config) :
        # Model Parameters to be used during inference
        self.model_name = config['Model']['Name']
        self.input_tensor_name = config['Model']['InputTensorName']
        self.output_tensor_name = config['Model']['OutputTensorName']

        # Init Model Scoring Scoring Script
        scoring_script_name = config['Model']['ScoringScriptModule']
        scoring_scripts_handler = model_scoring_scripts_map[scoring_script_name]
        self.model_scorer = scoring_scripts_handler(config)

        # Create the Channel to the OpenVINO Model Server backend
        grpc_address = config['Model']['OpenVINOModelServerAddress']
        grpc_port = config['Model']['OpenVINOModelServerPort']
        self.create_channel_to_ovms(grpc_address, grpc_port)

    # -----------------------------------------------------------------
    def __call__(self, params) :
        if not ValidateJSON(params, self.__schema__) :
            return None

        encryption_key = params['encryption_key']
        state_hash = params['state_hash']
        image_key = params['image_key']

        # load the input image from local storage
        kv = KeyValueStore(encryption_key, state_hash)
        with kv :
            image_bytes = kv.get(image_key,output_encoding='raw')

        # pre-process the image input using the scoring script
        img = self.model_scorer.preprocess_image(bytes(image_bytes))

        #Create the inference request package
        request = self.create_request_package_for_image_input(self.model_name, self.input_tensor_name, img)

        # do inference using the OVMS backend
        output = self.invoke_predict(request, self.output_tensor_name)

        # post-process the output using the scoring script
        return self.model_scorer.postprocess_inference_output(img, output)
