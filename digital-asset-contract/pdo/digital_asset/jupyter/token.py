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
import os
import re
import tempfile
import IPython.display as ip_display

import pdo.client.builder as pbuilder

import pdo.contracts.jupyter as pc_jupyter
import pdo.contracts.jupyter.keys as jp_keys
import pdo.contracts.jupyter.utility as jp_util

_logger = logging.getLogger(__name__)

__all__ = [
    'DigitalAssetImportWidget',
]


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class DigitalAssetImportWidget(ipywidgets.VBox) :
    """Define a widget class for importing a digital asset token

    The widget consists of several parts: the identity (public key) of
    the account to use for interacting with the asset, a name for the
    token class (this name is local and need not match the issuer's name
    for the asset), the token name (this is a specific token name) and
    the contract collections file for the issuer contracts that define
    the asset type. A button for performing the actual import and a
    feedback panel are included as well.
    """
    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings) :

        self.state = state
        self.bindings = bindings

        self.identity = ipywidgets.Dropdown(description='Identity')
        self.identity.options = jp_keys.build_private_key_list(self.state, self.bindings) or ['unspecified']
        self.identity.value = self.identity.options[0]

        self.import_file = ipywidgets.FileUpload(accept='.zip', description='Contract File')

        self.token_class = ipywidgets.Text(description='Token Class')

        self.import_button = ipywidgets.Button(description='Import Contract', button_style='primary')
        self.import_button.on_click(self.import_button_click)

        self.refresh = ipywidgets.Button(description="Refresh", button_style='info')
        self.refresh.on_click(self.refresh_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__(
            [
                ipywidgets.HBox([self.identity, self.import_file]),
                self.token_class,
                ipywidgets.HBox([self.import_button, self.refresh]),
                self.feedback
            ])

    def refresh_button_click(self, b) :
        """Recompute the balance list and update the widget
        """
        self.clear_widget()
        self.feedback.clear_output()
        self.identity.options = jp_keys.build_private_key_list(self.state, self.bindings) or ['unspecified']
        self.identity.value = self.identity.options[0]

    def clear_widget(self) :
        self.token_class.value = ''
        self.import_file.value = ()

    def import_button_click(self, b) :
        self.feedback.clear_output()

        # validate the inputs
        if not self.token_class.value or not re.match(r'^\w+$', self.token_class.value) :
            with self.feedback :
                print('Asset name must be a alphanumeric')
            return
        if not self.import_file.value :
            with self.feedback :
                print('No file specified')
            return

        # import the contract file
        context_file = os.path.join(self.bindings.expand('${etc}'), "{}_context.toml".format(self.token_class.value))

        try :
            with tempfile.NamedTemporaryFile() as import_fp :
                import_file = import_fp.name
                import_fp.write(self.import_file.value[0].content)

                token_context = jp_util.import_contract_collection(self.state, self.bindings, context_file, import_file)

        except Exception as e :
            with self.feedback :
                print("failed to import the file; {}".format(e))
            return

        token_name = token_context.get('token_name')
        parameters = {
            'token_owner' : self.identity.value,
            'token_class' : self.token_class.value,
            'token_name' : token_name,
            'context_file' : context_file,
        }

        instance_file = pc_jupyter.instantiate_notebook_from_template(self.token_class.value, 'token', parameters)
        with self.feedback :
            ip_display.display(ip_display.Markdown('[Token {}]({})'.format(parameters['token_name'], instance_file)))

        self.clear_widget()
