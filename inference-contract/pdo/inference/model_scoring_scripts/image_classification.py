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
This file defines the ImageClassification class & defines the methods in InferenceAppCustomOptions
for handling ImageClassification Models. The input preprocessing and output postprocessing parts of
this module are based on the image classification demo example contained within the
OpenVINO model server repository. For details, please see
https://github.com/openvinotoolkit/model_server/tree/main/demos/image_classification
"""


import cv2
import numpy as np

from pdo.inference.common.utility import ValidateJSON, CropResize
from pdo.inference.model_scoring_scripts.model_scoring_script_base import ModelScoringScriptBase
from pdo.inference.model_scoring_scripts.image_classes import imagenet_classes

import logging
logger = logging.getLogger(__name__)


## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
class ImageClassification(ModelScoringScriptBase) :
    # -----------------------------------------------------------------

    # these are parameters NOT signed over by the TO
    __misc_params_schema__ = {
        "type" : "object",
        "properties" : {
            "size" : { "type" : "integer" },
            "rgb_image" : { "type" : "integer" },
        }
    }

    # -----------------------------------------------------------------
    def __init__(self, config) :

        super().__init__()

        params = dict()
        params['size'] = config['Model']['InputImageCropSize']
        params['rgb_image'] = config['Model']['InputImageIsRGB']
        self.set_misc_params(params)

    # -----------------------------------------------------------------
    def set_misc_params(self,
        misc_params,
        **extra_params):
        """ check schema of misc_params necessary to use the model"""

        if not ValidateJSON(misc_params, self.__misc_params_schema__) :
            return False

        self.misc_params = misc_params
        return True

    # -----------------------------------------------------------------
    def preprocess_image(self,
        image_bytes,
        **extra_params):
        """ image in bytes format. return cv2 image Mat format"""

        img = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        size = self.misc_params['size']
        rgb_image = self.misc_params['rgb_image']

        img = CropResize(img, size, size)
        img = img.astype('float32')
        #convert to RGB instead of BGR if required by model
        if rgb_image:
            img = img[:, :, [2, 1, 0]]
        # switch from HWC to CHW and reshape to 1,3,size,size for model blob input requirements
        img = img.transpose(2,0,1).reshape(1,3,size,size)

        return img

    # -----------------------------------------------------------------
    def postprocess_inference_output(self,
        img,
        output,
        **extra_params):
        """ return result dict that should be part of dict returned back to the caller of the inference App.
        Specifically, returns the the classification label for the image"""

        result = {}

        nu = np.array(output)
        offset = 0
        if nu.shape[1] == 1001:
            offset = 1
        ma = np.argmax(nu) - offset
        classification_label = imagenet_classes[int(ma)]
        result['image_class'] = classification_label

        return result
