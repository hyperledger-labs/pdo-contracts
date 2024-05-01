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

import typing

import ipywidgets

import pdo.client.builder as pbuilder
import pdo.contracts.jupyter.services as pservices

from pdo.service_client.service_data.service_data import ServiceDatabaseManager as service_data
from pdo.service_client.service_data.service_groups import GroupsDatabaseManager as group_data

import pdo.client.commands.service_groups as psgroups


# -----------------------------------------------------------------
# -----------------------------------------------------------------
def build_groups_map(service_type : str) :
    assert service_type in group_data.service_types, "Unknown service type {}".format(service_type)

    groups = group_data.local_groups_manager.list_groups(service_type)

    groups_info = {}
    for (group_name, group_info) in groups :
        groups_info[group_name] = group_info.serialize()

    return groups_info

def build_groups_list(service_type : str) :
    groups_info_map = build_groups_map(service_type)
    return list(groups_info_map.keys())


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ServiceGroupListWidget(ipywidgets.VBox) :
    """Define a widget class that can be used to display a list
    of service groups from a specific class of services.
    """

    table_header = """
<table border=3 cellpadding=5>\n
<tr>
<th style=text-align:left>Service Group Name</th>
<th style=text-align:left>Service URLs</th>
</tr>
"""
    table_row = """
<tr>
<td>{group_name}</td>
<td>{service_urls}</td>
</tr>
"""

    table_footer = """
</table>
"""

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 service_type : str) :

        assert service_type in service_data.service_types, "Unknown service type {}".format(service_type)
        self.service_type = service_type

        self.group_list = ipywidgets.HTML(value=self.create_groups_list())

        self.refresh = ipywidgets.Button(description="Refresh")
        self.refresh.on_click(self.refresh_button_click)

        super().__init__([self.group_list, self.refresh])

    def create_groups_list(self) :
        """Create HTML version of the service groups list
        """

        groups_map = build_groups_map(self.service_type)
        groups_list = list(groups_map.keys())
        groups_list.sort()

        # this just makes a display friendly version of the names
        for g in groups_list :
            groups_map[g]['group_name'] = g
            groups_map[g]['service_urls'] = '<br>'.join(groups_map[g]['urls'])

        # and now create the service_list table
        result = self.table_header
        for g in groups_list :
            result += self.table_row.format(**groups_map[g])
        result += self.table_footer

        return result

    def refresh_button_click(self, b) :
        """Recompute the group list and update the groups_list widget
        """
        self.group_list.value = self.create_groups_list()


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ServiceGroupSelectionWidget(ipywidgets.VBox) :
    """Define a widget class that can be used to select a service group from
    a list of currently known groups
    """

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 service_type : str,
                 button_label : str = None,
                 button_callback : typing.Callable = None) :

        assert service_type in service_data.service_types, "Unknown service type {}".format(service_type)
        self.service_type = service_type

        self.button_label = button_label
        self.button_callback = button_callback

        groups = self.create_groups_list()
        self.groups_list = ipywidgets.Dropdown(options=groups, value=groups[0], description='Groups')

        self.refresh_button = ipywidgets.Button(description="Refresh")
        self.refresh_button.on_click(self.refresh_button_click)
        buttonbar = [self.refresh_button]
        if button_callback :
            self.button_label = button_label
            self.button_callback = button_callback

            self.submit_button = ipywidgets.Button(description=self.button_label)
            self.submit_button.on_click(self.submit_button_click)

            buttonbar.append(self.submit_button)

        self.feedback = ipywidgets.Output()

        super().__init__([self.groups_list, ipywidgets.HBox(buttonbar), self.feedback])

    @property
    def selection(self) :
        return self.groups_list.value

    def create_groups_list(self) :
        """Create a list of the services
        """

        groups_list = build_groups_list(self.service_type) or ['unknown']
        groups_list.sort()

        return groups_list

    def refresh_button_click(self, b) :
        """Recompute the service list and update the groups_list widget
        """
        self.groups_list.options = self.create_groups_list()

    def submit_button_click(self, b) :
        """Invoke the function for handling the selection
        """
        self.feedback.clear_output()
        self.button_callback(self.service_type, self.groups_list.value, self.feedback)


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ProvisioningServiceGroupCreateWidget(ipywidgets.VBox) :
    """Define a widget for creating an provisioning service group
    """

    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        self.group_name = ipywidgets.Text(description="Group Name")
        self.services = pservices.ServiceSelectionWidget(state, bindings, 'pservice')

        self.submit_button = ipywidgets.Button(description='Create Group')
        self.submit_button.on_click(self.submit_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__([self.group_name, self.services, self.submit_button, self.feedback])

    def reset_widget(self) :
        self.services.reset_widget()
        self.group_name.value = ''

    def submit_button_click(self, b) :
        """Create the provisioning services group
        """
        self.feedback.clear_output()
        psgroups.add_group('pservice', self.group_name.value, self.services.selection)
        with self.feedback :
            print("Provisioning service group {} created".format(self.group_name.value))

        self.reset_widget()


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class EnclaveServiceGroupCreateWidget(ipywidgets.VBox) :
    """Define a widget for creating an enclave service group
    """

    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        self.group_name = ipywidgets.Text(description="Group Name")
        self.services = pservices.ServiceSelectionWidget(state, bindings, 'eservice')
        self.services.service_list.observe(self.update_preferred_list)

        self.preferred_service = ipywidgets.Dropdown(options=['unknown'], value='unknown', description="Preferred Service")

        self.submit_button = ipywidgets.Button(description='Create Group')
        self.submit_button.on_click(self.submit_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__([self.group_name, self.services, self.preferred_service, self.submit_button, self.feedback])

    def update_preferred_list(self, change) :
        if change['type'] == 'change' and change['name'] == 'value' :
            value = self.preferred_service.value
            selection = self.services.selection
            if value not in selection :
                value = selection[0]

            self.preferred_service.options = selection
            self.preferred_service.value = value

    def reset_widget(self) :
        self.services.reset_widget()
        self.group_name.value = ''
        self.preferred_service.value = ''

    def submit_button_click(self, b) :
        """Create the enclave services group
        """
        self.feedback.clear_output()

        preferred = self.preferred_service.value or None
        if preferred and preferred not in self.services.selection :
            with self.feedback :
                print("Preferred service must be part of the group")
            return

        params = {}
        if preferred :
            params['preferred'] = preferred

        psgroups.add_group('eservice', self.group_name.value, self.services.selection, **params)
        with self.feedback :
            print("Enclave service group {} created".format(self.group_name.value))

        self.reset_widget()


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class StorageServiceGroupCreateWidget(ipywidgets.VBox) :
    """Define a widget for creating an storage service group
    """

    def __init__(self, state : pbuilder.state.State, bindings : pbuilder.bindings.Bindings) :
        self.group_name = ipywidgets.Text(description="Group Name")
        self.services = pservices.ServiceSelectionWidget(state, bindings, 'sservice')
        self.services.service_list.observe(self.update_persistent_list)

        self.persistent_service = ipywidgets.Dropdown(options=['unknown'], value='unknown', description="Presistent Service")

        self.replicas = ipywidgets.IntSlider(value=2, min=1, max=10, step=1, description='Required Replicas')
        self.duration = ipywidgets.IntSlider(value=120, min=60, max=3600, step=10, description='Required Duration')
        self.submit_button = ipywidgets.Button(description='Create Group')
        self.submit_button.on_click(self.submit_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__([self.group_name,
                          self.services,
                          self.persistent_service,
                          self.replicas,
                          self.duration,
                          self.submit_button,
                          self.feedback])

    def update_persistent_list(self, change) :
        if change['type'] == 'change' and change['name'] == 'value' :
            value = self.persistent_service.value
            selection = self.services.selection
            if value not in selection :
                value = selection[0]

            self.persistent_service.options = selection
            self.persistent_service.value = value

    def reset_widget(self) :
        self.services.reset_widget()
        self.group_name.value = ''
        self.persistent_service.value = ''
        self.replicas.value = 2
        self.duration.value = 120

    def submit_button_click(self, b) :
        """Create the storage services group
        """
        self.feedback.clear_output()

        persistent = self.persistent_service.value or None
        if persistent and persistent not in self.services.selection :
            with self.feedback :
                print("Persistent service must be part of the group")
            return

        if self.replicas.value >= len(self.services.selection) :
            with self.feedback :
                print("Number of replicas must be less than the number of services")
            return

        params = {}
        params['replicas'] = self.replicas.value
        params['duration'] = self.duration.value
        if persistent :
            params['persistent'] = persistent

        psgroups.add_group('sservice', self.group_name.value, self.services.selection, **params)
        with self.feedback :
            print("Storage service group {} created".format(self.group_name.value))

        self.reset_widget()
