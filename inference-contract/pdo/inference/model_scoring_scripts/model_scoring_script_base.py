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
This module specifies the InferenceAppCustomOptions meta class containing API definitions that be be defined by 
model-specific . These must be overridden by child class
(see FaceDetection or ImageClassification). The purpose of having these as abstractmethods
is to fix the APIs. 
"""

import logging
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)

class ModelScoringScriptBase(object):

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        pass

# -----------------------------------------------------------------
# Following APIs are provided by the InferenceAppCustomOptions. These must be overridden by child class
# (see FaceDetection or ImageClassification). The purpose of having these as abstractmethods
# is to fix the APIs. 

# -----------------------------------------------------------------
    @abstractmethod
    def set_misc_params(self, misc_params, **extra_params):
        """ check schema of misc_params necessary to use the model"""
        raise NotImplementedError("Must override check_schema_misc_params")
    
# -----------------------------------------------------------------
    @abstractmethod
    def preprocess_image(self, image, **extra_params):
        """ image in cv2 Mat format. return cv2 image Mat format"""
        raise NotImplementedError("Must override preprocess_image")


# -----------------------------------------------------------------
    @abstractmethod
    def postprocess_inference_output(self, image, inference_output, **extra_params):
        """ return result dict that should be part of dict returned back to the caller of the inference App"""
        raise NotImplementedError("Must override postprocess_inference_output")
