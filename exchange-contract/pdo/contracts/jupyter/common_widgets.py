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

import base64
import logging
import os

import ipywidgets

_logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class FileDownloadLink(ipywidgets.HTML) :
    """Create a HTML reference to download a file that is not in the
    Jupyter server namespace.

    The content of the file is read, base64 encoded and embedded in the
    address reference. This class can serve as a base class for
    alternative ways of displaying the link.
    """

    _address_start_template_ = '<a download="{filename}" href="data:{file_type};base64,{payload}" download>'
    _label_template_ = '{label}'
    _address_end_template_ = '</a>'

    _extensions_ = {
        '.pem' : 'application/x-pem-file',
        '.pdo' : 'application/json',
        '.toml' : 'application/toml',
        '.zip' : 'application/zip',
    }

    def __init__(self, filename : str, label : str = "Download File") :
        with open(filename, "rb") as fp :
            payload = base64.b64encode(fp.read()).decode()

        file_type = self._extensions_.get(os.path.splitext(filename)[1], 'application/octet-stream')
        template = self._address_start_template_ + self._label_template_ + self._address_end_template_

        parameters = {
            'file_type' : file_type,
            'label' : label,
            'payload' : payload,
            'filename' : os.path.basename(filename),
        }

        content = template.format(**parameters)
        super().__init__(value=content)

class FileDownloadButton(FileDownloadLink) :
    """Create a Jupyter button for a download link"""
    _label_template_ = '<button class="p-Widget jupyter-widgets jupyter-button widget-button mod-warning">{label}</button>'
