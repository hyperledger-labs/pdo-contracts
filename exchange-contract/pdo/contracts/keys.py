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

import ipywidgets

import pdo.client.builder as pbuilder
from pdo.common.keys import ServiceKeys

__all__ = [
    'build_public_key_map',
    'build_private_key_map',
    'build_public_key_list',
    'build_private_key_list',
    'generate_key_pair',
    'creat_public_key_selection_widget',
    'creat_private_key_selection_widget',
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
def create_public_key_list_widget(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
    public_key_map = build_public_key_map(state,bindings)
    public_keys = list(public_key_map.keys())
    public_keys.sort()

    result = "<h1>Public Keys</h1>\n"
    result += "<table border=3 padding=3>\n"
    result += "<tr><th style=text-align:left>Identity</th><th style=text-align:left>Key File</th></tr>\n"
    for k in public_keys :
        result += "<tr><td>{}</td><td>{}</td></tr>\n".format(k, public_key_map[k])
    result += "</table>\n"

    htmlbox = ipywidgets.HTML(value=result)
    return htmlbox

def create_public_key_selection_widget(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
    public_keys = build_public_key_list(state, bindings) or ['unknown']

    dropdown = ipywidgets.Dropdown(options=public_keys, value=public_keys[0], description='Public Keys')
    refresh_button = ipywidgets.Button(description="Refresh Keys")

    def on_button_click(b) :
        public_keys = build_public_key_list(state, bindings) or ['unknown']
        dropdown.options = public_keys
        dropdown.value = public_keys[0]

    refresh_button.on_click(on_button_click)

    return ipywidgets.HBox([dropdown, refresh_button])

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def create_private_key_list_widget(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
    private_key_map = build_private_key_map(state,bindings)
    private_keys = list(private_key_map.keys())
    private_keys.sort()

    result = "<h1>Private Keys</h1>\n"
    result += "<table border=3 padding=3>\n"
    result += "<tr><th style=text-align:left>Identity</th><th style=text-align:left>Key File</th></tr>\n"
    for k in private_keys :
        result += "<tr><td>{}</td><td>{}</td></tr>\n".format(k, private_key_map[k])
    result += "</table>\n"

    htmlbox = ipywidgets.HTML(value=result)
    return htmlbox

def create_private_key_selection_widget(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
    private_keys = build_private_key_list(state, bindings) or ['unknown']

    dropdown = ipywidgets.Dropdown(options=private_keys, value=private_keys[0], description='Private Keys')
    refresh_button = ipywidgets.Button(description="Refresh Keys")

    def on_button_click(b) :
        private_keys = build_private_key_list(state, bindings) or ['unknown']
        dropdown.options = private_keys
        dropdown.value = private_keys[0]

    refresh_button.on_click(on_button_click)

    return ipywidgets.HBox([dropdown, refresh_button])

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def create_generate_key_widget(state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
    feedback_box = ipywidgets.Output()
    key_entry_box = ipywidgets.Text(description="Identity")
    key_click_button = ipywidgets.Button(description="Generate Keys")

    def on_button_click(b) :
        identity = key_entry_box.value
        if identity and identity.isalnum() :
            generate_key_pair(state, bindings, identity)
            key_entry_box.value = ''
            feedback_box.clear_output()
            with feedback_box :
                print("keys created for {}".format(identity))

    key_click_button.on_click(on_button_click)

    return ipywidgets.HBox([key_entry_box, key_click_button, feedback_box])
