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

import codecs
import datetime
import toml
import typing

import ipywidgets

import pdo.client.builder as pbuilder
from pdo.service_client.service_data.service_data import ServiceDatabaseManager as service_data

__all__ = [
    'get_by_name',
    'get_by_url',
    'update_service',
    'store_service',
    'remove_service',
    'build_services_map',
    'build_services_list',
    'ServiceListWidget',
    'ServiceSelectionWidget',
    'ServiceUploadWidget',
    'service_labels',
]

service_labels = {
    'eservice' : 'Enclave Service',
    'pservice' : 'Provisioning Service',
    'sservice' : 'Storage Service',
}

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# shortcuts for common service functions
def get_by_name(*args, **kwargs) :
    return service_data.local_service_manager.get_by_name(*args, **kwargs)

def get_by_url(*args, **kwargs) :
    return service_data.local_service_manager.get_by_url(*args, **kwargs)

def update_service(*args, **kwargs) :
    return service_data.local_service_manager.update(*args, **kwargs)

def store_service(*args, **kwargs) :
    return service_data.local_service_manager.store(*args, **kwargs)

def remove_service(*args, **kwargs) :
    return service_data.local_service_manager.remove(*args, **kwargs)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def build_services_map(service_type : str) :
    """Build a dictionary that maps a service URL to information about the service
    """
    assert service_type in service_data.service_types, "Unknown service type {}".format(service_type)

    services = service_data.local_service_manager.list_services(service_type)

    services_info = {}
    for (service_url, service_info) in services :
        services_info[service_url] = service_info.serialize()

    return services_info


def build_services_list(service_type : str) :
    """Return a list of URLs for services of the given type
    """
    services_info_map = build_services_map(service_type)
    return list(services_info_map.keys())


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ServiceListWidget(ipywidgets.VBox) :
    """Define a widget class that can be used to display a list
    of service instances from a specific class of services.
    """

    table_header = """
<table border=3 cellpadding=5>\n
<tr>
<th style=text-align:left>URL</th>
<th style=text-align:left>Service Names</th>
<th style=test-align:left>Last Verified Time</th>
</tr>
"""
    table_row = """
<tr>
<td>{service_url}</td>
<td>{names}</td>
<td>{last_verified}</td>
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

        self.service_list = ipywidgets.HTML(value=self.create_service_list())

        self.refresh = ipywidgets.Button(description="Refresh")
        self.refresh.on_click(self.refresh_button_click)

        super().__init__([self.service_list, self.refresh])

    def create_service_list(self) :
        """Create HTML version of the service list
        """

        services_info_map = build_services_map(self.service_type)
        services_list = list(services_info_map.keys())
        services_list.sort()

        # this just makes a display friendly version of the names
        for u in services_list :
            services_info_map[u]['names'] = '<br>'.join(services_info_map[u]['service_names'])

            timestamp = services_info_map[u]['last_verified_time']
            if timestamp > 0 :
                services_info_map[u]['last_verified'] = datetime.date.fromtimestamp(timestamp).ctime()
            else :
                services_info_map[u]['last_verified'] = 'not verified'

        # and now create the service_list table
        result = self.table_header
        for u in services_list :
            result += self.table_row.format(**services_info_map[u])
        result += self.table_footer

        return result

    def refresh_button_click(self, b) :
        """Recompute the service list and update the service_list widget
        """
        self.service_list.value = self.create_service_list()


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ServiceSelectionWidget(ipywidgets.VBox) :
    """Define a widget class that can be used to select a service from
    a list of currently known services

    This widget consists of several components: a multi-select box for services,
    a refresh button, and optionally a callback button that can be used for
    submitting the selected services. The callback button can be left out if
    this widget is part of a more complex form.
    """

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 service_type : str,
                 button_label : str = None,
                 button_callback : typing.Callable = None) :

        assert service_type in service_data.service_types, "Unknown service type {}".format(service_type)
        self.service_type = service_type

        self.service_list = ipywidgets.SelectMultiple(
            options=self.create_service_list(),
            description=service_labels[self.service_type])

        self.refresh_button = ipywidgets.Button(description="Refresh")
        self.refresh_button.on_click(self.refresh_button_click)
        button_bar = [self.refresh_button]

        if button_callback :
            self.button_label = button_label
            self.button_callback = button_callback

            self.submit_button = ipywidgets.Button(description=self.button_label)
            self.submit_button.on_click(self.submit_button_click)

            button_bar.append(self.submit_button)

        self.feedback = ipywidgets.Output()

        super().__init__([self.service_list, ipywidgets.HBox(button_bar), self.feedback])

    @property
    def selection(self) :
        return self.service_list.value

    def reset_widget(self) :
        self.service_list.options = self.create_service_list()
        self.service_list.value = []

    def create_service_list(self) :
        """Create a list of the services
        """

        services_info_map = build_services_map(self.service_type)
        if services_info_map is None :
            return ['unknown']

        services_list = list(map(lambda s : s.decode(), services_info_map.keys()))
        services_list.sort()
        return services_list

    def refresh_button_click(self, b) :
        """Recompute the service list and update the service_list widget
        """
        self.service_list.options = self.create_service_list()

    def submit_button_click(self, b) :
        """Invoke the function for handling the selection
        """
        self.feedback.clear_output()
        self.button_callback(self.service_type, self.service_list.value, self.feedback)


# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ServiceUploadWidget(ipywidgets.VBox) :
    """Define a widget class that can be used to upload a sit
    configuration file.

    This widget consists of several components: a file selection button to pick the
    service description file, a submit button that handles the uploaded file, and a
    feedback panel.
    """

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings) :

        self.site_file = ipywidgets.FileUpload(accept='.toml', description='Select Site Services File')
        self.submit = ipywidgets.Button(description="Upload")
        self.submit.on_click(self.on_button_click)
        self.feedback = ipywidgets.Output()

        super().__init__([ipywidgets.HBox([self.site_file, self.submit]), self.feedback])

    def check_input(self) :
        if not self.site_file.value :
            with self.feedback :
                print("No file specified")
            return False
        return True

    def reset_widget(self) :
        self.site_file.value = ()

    def on_button_click(self, b) :
        self.feedback.clear_output()
        if self.check_input() :
            try :
                service_file = codecs.decode(self.site_file.value[0].content, encoding='utf-8')
                service_info = toml.loads(service_file)
                service_data.local_service_manager.import_service_information(service_info)
                with self.feedback :
                    print("Service data imported")
            except Exception as e :
                with self.feedback :
                    print("Unable to import service data; {}".format(e))

        self.reset_widget()
