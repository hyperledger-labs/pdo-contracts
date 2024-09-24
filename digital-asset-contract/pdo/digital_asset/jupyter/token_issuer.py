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

import ipywidgets
import logging
import re
import tempfile
import IPython.display as ip_display

import pdo.client.builder as pbuilder

import pdo.contracts.jupyter as pc_jupyter
from pdo.contracts.jupyter.keys import PrivateKeySelectionWidget
from pdo.contracts.jupyter.groups import ServiceGroupSelectionWidget

pc_jupyter.load_contract_families(digital_asset='da', exchange='ex')

_logger = logging.getLogger(__name__)

__all__ = [
    'DigitalAssetIssuerWidget',
]


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class DigitalAssetIssuerWidget(ipywidgets.VBox) :
    """
    """
    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        self.state = state
        self.bindings = bindings

        # Use a private key selection widget to pick the identity to use
        self.issuer_identity_w = PrivateKeySelectionWidget(state, bindings)

        # Use the service group selection widget to get service groups
        self.eservice_group_w = ServiceGroupSelectionWidget(state, bindings, 'eservice')
        self.pservice_group_w = ServiceGroupSelectionWidget(state, bindings, 'pservice')
        self.sservice_group_w = ServiceGroupSelectionWidget(state, bindings, 'sservice')

        self.token_class_w = ipywidgets.Text(description='Token Class')
        self.token_description_w = ipywidgets.Text(description='Token Description')
        self.count_w = ipywidgets.IntSlider(description="Number of Tokens", min=1, max=50, value=5)

        self.image_file_w = ipywidgets.FileUpload(accept='.bmp', description='Image File')
        self.border_width_w = ipywidgets.IntSlider(description="Privacy Border", min=0, max=10, value=5)

        self.create_button = ipywidgets.Button(description='Create Issuer', button_style='primary')
        self.create_button.on_click(self.create_button_click)

        self.feedback = ipywidgets.Output()

        tab1_children = [
            self.token_class_w,
            self.token_description_w,
            self.count_w,
            self.image_file_w,
            self.border_width_w,
        ]

        tab2_children = [
            self.issuer_identity_w,
            self.eservice_group_w,
            self.pservice_group_w,
            self.sservice_group_w,
        ]

        super().__init__([
            ipywidgets.Tab(
                children=[ipywidgets.VBox(tab1_children), ipywidgets.VBox(tab2_children)],
                titles=['Asset Token Information', 'Service Information']),
            self.create_button,
            self.feedback,
            ])

    def create_button_click(self, b) :
        self.feedback.clear_output()

        # input verification: token_class
        token_class = self.token_class_w.value
        if not token_class or not re.match(r'^\w+$', token_class) :
            with self.feedback :
                print("must specify value for token class")
            return

        # input verification: selection widgets
        # note that these are assertions because the widgets should already force
        # selection values to exist
        assert self.eservice_group_w.selection and self.pservice_group_w.selection and self.sservice_group_w.selection
        assert self.issuer_identity_w.selection

        # build the image file
        datadir = self.bindings.expand("${data}")
        with tempfile.NamedTemporaryFile(mode="wb", dir=datadir, suffix='.bmp', delete=False) as fp :
            image_file_name = fp.name
            fp.write(self.image_file_w.value[0].content)

        instance_parameters = {
            'token_owner' : self.issuer_identity_w.selection,
            'token_class' : token_class,
            'token_description' : self.token_description_w.value,
            'count' : int(self.count_w.value),
            'eservice_group' : self.eservice_group_w.selection,
            'pservice_group' : self.pservice_group_w.selection,
            'sservice_group' : self.sservice_group_w.selection,
            'border_width' : int(self.border_width_w.value),
            'image_file' : image_file_name,
        }

        instance_file = pc_jupyter.instantiate_notebook_from_template(token_class, 'token_issuer', instance_parameters)
        with self.feedback :
            ip_display.display(
                ip_display.Markdown('[Token Issuer]({})'.format(instance_file)))
