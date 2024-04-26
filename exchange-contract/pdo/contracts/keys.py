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

import functools
import glob
import os
import re

import ipywidgets

import pdo.client.builder as pbuilder
from pdo.common.keys import ServiceKeys
from pdo.contracts.common_widgets import FileDownloadLink

__all__ = [
    'build_public_key_map',
    'build_private_key_map',
    'build_public_key_list',
    'build_private_key_list',
    'generate_key_pair',
    'KeyListWidget',
    'PublicKeyListWidget',
    'PrivateKeyListWidget',
    'KeySelectionWidget',
    'PublicKeySelectionWidget',
    'PrivateKeySelectionWidget',
    'GenerateKeyWidget',
    'UploadKeyWidget',
]

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def _build_key_map_(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings, pattern : str) -> dict :
    """Build a map for keys found in the specified search path
    """

    key_directories = state.get(['Key', 'SearchPath'])
    key_directories = list(map(lambda f : bindings.expand(f), key_directories))

    # fill the identity map, if there are duplicates then we use the
    # one found first in the search path

    key_files = map(
        lambda f : os.path.realpath(f),
        functools.reduce(lambda r, d : r + glob.glob(os.path.join(d, '*' + pattern)), key_directories, []))

    key_map = {}
    for key_file in key_files :
        identity = os.path.basename(key_file).replace(pattern, '')
        if key_map.get(identity) is None :
            key_map[identity] = key_file

    return key_map

def build_public_key_map(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) -> dict :
    return _build_key_map_(state, bindings, '_public.pem')

def build_public_key_list(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) -> list :
    key_list = list(build_public_key_map(state, bindings).keys())
    key_list.sort()

    return key_list

def build_private_key_map(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) -> dict :
    return _build_key_map_(state, bindings, '_private.pem')

def build_private_key_list(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) -> list :
    key_list = list(build_private_key_map(state, bindings).keys())
    key_list.sort()

    return key_list

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def generate_key_pair(
    state : pbuilder.state.State,
    bindings : pbuilder.bindings.Bindings,
    identity : str,
    save_path='${keys}') -> list :

    """Create a key pair that can be used for signing PDO transactions
    """
    keyfile = os.path.join(bindings.expand(save_path), identity)

    service_key = ServiceKeys.create_service_keys()
    service_key.save_to_file(keyfile)

    return (keyfile + "_private.pem", keyfile + "_public.pem")

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class KeyListWidget(ipywidgets.VBox) :
    """Define a widget class for displaying a list of available keys
    """

    table_header = """
<table border=3 cellpadding=5>
<tr>
<th style=text-align:left>Identity</th>
<th style=text-align:left>Key File</th>
</tr>
"""

    table_footer = """
</table>
"""

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 keytype : str) :

        assert keytype in ['public', 'private']

        self.state = state
        self.bindings = bindings
        self.keytype = keytype

        self.key_list = ipywidgets.HTML()
        self.key_list.value = self.create_key_list(state, bindings)

        self.refresh = ipywidgets.Button(description="Refresh Keys")
        self.refresh.on_click(self.refresh_button_click)

        super().__init__([self.key_list, self.refresh])

    def create_key_list(self, state, bindings) :
        """Create the HTML table for the keys list
        """
        if self.keytype == 'public' :
            key_map = build_public_key_map(state, bindings)
        else :
            key_map = build_private_key_map(state, bindings)

        keys = list(key_map.keys())
        keys.sort()

        result = self.table_header

        for k in keys :
            result += "<tr><td>{}</td><td>{}</td></tr>\n".format(k, FileDownloadLink(key_map[k], key_map[k]).value)

        result += self.table_footer

        return result

    def refresh_button_click(self, b) :
        """Recompute the key list and update the key_list widget
        """
        self.key_list.value = self.create_key_list(self.state, self.bindings)

class PublicKeyListWidget(KeyListWidget) :
    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        super().__init__(state, bindings, 'public')

class PrivateKeyListWidget(KeyListWidget) :
    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        super().__init__(state, bindings, 'private')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class KeySelectionWidget(ipywidgets.VBox) :
    """Define a widget class for selecting a key

    This widget has four parts: the key list, a button to refresh
    the list of keys, a button to submit the currently selected key
    to a callback function, and a feedback area. The widget should be
    created with a function to handle the selection.
    """
    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 keytype : str,
                 button_label : str,
                 button_callback) :

        assert keytype in ['public', 'private']

        self.state = state
        self.bindings = bindings
        self.keytype = keytype

        self.button_label = button_label
        self.button_callback = button_callback

        self.submit = ipywidgets.Button(description=self.button_label)
        self.submit.on_click(self.submit_button_click)

        keys = self.create_key_list(self.state, self.bindings)
        self.dropdown = ipywidgets.Dropdown(options=keys, value=keys[0], description='Keys')

        self.refresh = ipywidgets.Button(description="Refresh Keys")
        self.refresh.on_click(self.refresh_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__([ipywidgets.HBox([self.dropdown, self.refresh, self.submit]), self.feedback])

    @property
    def selection(self) :
        return self.dropdown.value

    def create_key_list(self, state, bindings) :
        """Create a list of key names
        """
        if self.keytype == 'public' :
            return build_public_key_list(state, bindings) or ['unknown']
        else :
            return build_private_key_list(state, bindings) or ['unknown']

    def refresh_button_click(self, b) :
        """Recompute the service list and update the service_list widget
        """
        keys = self.create_key_list(self.state, self.bindings)
        self.dropdown.options = keys
        self.dropdown.value = keys[0]

    def submit_button_click(self, b) :
        """Invoke the function for handling the selection
        """
        self.feedback.clear_output()
        self.button_callback(self.dropdown.value, self.feedback)

class PublicKeySelectionWidget(KeySelectionWidget) :
    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 button_label : str,
                 button_callback) :
        super().__init__(state, bindings, 'public', button_label, button_callback)

class PrivateKeySelectionWidget(KeySelectionWidget) :
    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 button_label : str,
                 button_callback) :
        super().__init__(state, bindings, 'private', button_label, button_callback)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class GenerateKeyWidget(ipywidgets.VBox) :
    """Define a widget class for creating a key pair

    This widget consists of three components: the text box for the
    new key name, the generate button for creating the key, and a
    feedback box.
    """
    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        self.state = state
        self.bindings = bindings

        self.key = ipywidgets.Text(description="Identity")

        self.generate = ipywidgets.Button(description="Generate Keys")
        self.generate.on_click(self.generate_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__([ipywidgets.HBox([self.key, self.generate]), self.feedback])

    def clear_widget(self) :
        self.feedback.clear_output()

    def generate_button_click(self, b) :
        identity = self.key.value
        if identity and re.match(r'^\w+$', identity) :
            generate_key_pair(self.state, self.bindings, identity)
            with self.feedback : print("keys created for {}".format(identity))
        else :
            with self.feedback : print("invalid identity {}".format(identity))

        self.key.value = ''

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class UploadKeyWidget(ipywidgets.VBox) :
    """Define a widget class for uploading a key

    This widget consists of several components: the name of the uploaded key,
    the type of uploaded key, the file that currently contains the key, an
    upload button, and a feedback area.
    """
    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        self.state = state
        self.bindings = bindings

        self.key_entry = ipywidgets.Text(description="Identity")
        self.key_type = ipywidgets.Dropdown(options=['public', 'private'], value='public', description='Key Type')
        self.key_file = ipywidgets.FileUpload(accept='.pem', description='Select Key File')

        self.upload_button = ipywidgets.Button(description="Upload")
        self.upload_button.on_click(self.upload_button_click)

        self.feedback = ipywidgets.Output()

        hbox = ipywidgets.HBox([self.key_entry, self.key_type, self.key_file, self.upload_button])
        super().__init__([hbox, self.feedback])

    def reset_widget(self) :
        """Reset the values of the components in the widget
        """
        self.key_entry.value = ''
        self.key_type.value = 'public'
        self.key_file.value = ()

    def upload_button_click(self, b) :
        """Handle the request to upload the file
        """
        self.feedback.clear_output()

        if not self.key_entry.value or not re.match(r'^\w+$', self.key_entry.value) :
            with self.feedback : print("Identity must be alphanumeric")
            return
        if not self.key_file.value :
            with self.feedback : print("No file specified")
            return

        keydir = self.bindings.expand("${keys}")
        keyfile = "{}_{}.pem".format(self.key_entry.value, self.key_type.value)
        filename = os.path.join(keydir, keyfile)
        with open(filename, "wb") as fp : fp.write(self.key_file.value[0].content)
        with self.feedback : print("keys uploaded to {}".format(filename))

        self.reset_widget()
