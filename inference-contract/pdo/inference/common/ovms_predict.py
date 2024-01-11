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
This file defines the OVMSPredict base class that creates a grpc channel to the OVMS backend,
packages inference request for image inputs, and invokes the inference request. Class may be extended
later for packaging inference requests with data formats of other types such as videos.
Model Author inherits this class to implement wsgi end point for model usage. The child class
implements custom model/use-case specific operations for input pre-processing, input validty checking
output postprocessing, result packaging etc.
"""

import grpc
from tensorflow import make_tensor_proto, make_ndarray
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

import logging
logger = logging.getLogger(__name__)


import logging
logger = logging.getLogger(__name__)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class OVMSPredict(object) :

    # -----------------------------------------------------------------
    def __init__(self) :

        self.stub = None

    def create_channel_to_ovms(self, grpc_address, grpc_port) :

        address = "{}:{}".format(grpc_address, grpc_port)
        self.inferenceservice_channel = grpc.insecure_channel(address)
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.inferenceservice_channel)

    def create_request_package_for_image_input(self, model_name, input_name, img):
        """
            model_name: name of the model (to be used to process the request) as specified while starting the docker container
            input_name: Input tensor name
            img: opencv image in Mat format
        """

        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        request.inputs[input_name].CopyFrom(make_tensor_proto(img, shape=(img.shape)))

        return request

    def invoke_predict(self, request, output_name):
        """
            request : prediction request, e.g. output of create_request_for_single_image
            output_name : output tensor name
        """

        result = self.stub.Predict(request, 10.0) #what is this 10?? cannot find any reference.
                                                      #same value of 10 is used by multiple examples
        output = make_ndarray(result.outputs[output_name])

        return output
