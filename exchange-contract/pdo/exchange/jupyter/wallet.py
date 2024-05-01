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
import time

import pdo.contracts.jupyter.keys as jp_keys
import pdo.contracts.jupyter.utility as jp_util

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.commands.contract as pcontract_cmd

import pdo.exchange.plugins.issuer as ex_issuer

_logger = logging.getLogger(__name__)

__all__ = [
    'get_asset_type',
    'get_asset_owner',
    'get_asset_balance',
    'transfer_assets',
    'AssetBalanceWidget',
    'AssetTransferWidget',
    'ImportIssuerWidget',
]

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def get_asset_type(state, wallet_path, asset_handle) :
    """Get information about the asset type

    Returns a dictionary of properties of the asset type.
    """
    wallet_context = pbuilder.Context(state, f'{wallet_path}.{asset_handle}')
    asset_type_context = wallet_context.get_context('asset_type')
    return asset_type_context.context

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def get_asset_owner(state, wallet_path, asset_handle) :
    """Get the owner of assets held by an issuer
    """
    wallet_context = pbuilder.Context(state, f'{wallet_path}.{asset_handle}')
    issuer_context = wallet_context.get_context('issuer')
    return issuer_context.get('identity')

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def get_asset_balance(state, wallet_path, asset_handle, owner=None) :
    """Get the balance of assets held by an issuer on behalf of an owner
    """
    wallet_context = pbuilder.Context(state, f'{wallet_path}.{asset_handle}')
    issuer_context = wallet_context.get_context('issuer')
    owner = owner or issuer_context.get('identity')

    # check the balance, if the account has no balance a value error exception will be thrown; in
    # this case, that is not a problem, the value is simply assumed to be 0 (and assets may be
    # transferred to this account in the future
    try :
        return pcommand.invoke_contract_cmd(
            ex_issuer.cmd_get_balance, state, issuer_context, identity=owner)
    except ValueError as ve :
        return 0

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def transfer_assets(state, wallet_path, asset_handle, count, new_owner, old_owner=None) :
    """Transfer assets from current owner to a new owner

    Assets are transfered within a specific asset type; transfers across
    types must be done through an exchange.
    """
    wallet_context = pbuilder.Context(state, f'{wallet_path}.{asset_handle}')
    issuer_context = wallet_context.get_context('issuer')
    old_owner = old_owner or issuer_context.get('identity')

    return pcommand.invoke_contract_cmd(
        ex_issuer.cmd_transfer_assets, state, issuer_context, new_owner=new_owner, count=count, identity=old_owner)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class AssetBalanceWidget(ipywidgets.VBox) :
    """Define a widget class for building a table of asset balances

    The widget consists of two parts: a table of asset balances computed
    from the asset handles known to the wallet and a refresh button.
    """

    table_header = """
<table border=3 cellpadding=5>
<tr>
<th style=text-align:left>Asset Handle</th>
<th style=text-align:left>Identity</th>
<th style=text-align:left>Asset Type Name</th>
<th style=text-align:left>Balance</th>
</tr>
"""

    table_row = """
<tr>
<td style=text-align:left>{}</td>
<td style=text-align:left>{}</td>
<td style=text-align:left>{}</td>
<td style=text-align:left>{}</td>
</tr>
"""

    table_footer = """
</table>
"""

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 wallet_path : str) :

        self.state = state
        self.bindings = bindings
        self.wallet_path = wallet_path

        self.balance_table = ipywidgets.HTML()
        self.balance_table.value = self.create_balance_list()

        self.refresh = ipywidgets.Button(description="Refresh", button_style='info')
        self.refresh.on_click(self.refresh_button_click)

        super().__init__([self.balance_table, self.refresh])

    def create_balance_list(self) :
        """Create an HTML table with the current balances
        """
        wallet_context = pbuilder.Context(self.state, self.wallet_path)
        asset_list = wallet_context.get('asset_list', [])

        result = self.table_header
        for asset_handle in asset_list :
            balance = get_asset_balance(self.state, self.wallet_path, asset_handle)
            owner = get_asset_owner(self.state, self.wallet_path, asset_handle)
            asset_type_info = get_asset_type(self.state, self.wallet_path, asset_handle)

            result += self.table_row.format(asset_handle, owner, asset_type_info['name'], balance)

        result += self.table_footer
        return result

    def refresh_button_click(self, b) :
        """Recompute the balance list and update the widget

        In order to get most recent version of the contract, this will flush the
        contract cache.
        """
        pcontract_cmd.flush_contract_cache()
        self.balance_table.value = self.create_balance_list()

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class AssetTransferWidget(ipywidgets.VBox) :
    """Define a widget to handle a transfer of assets

    The widget consists of serveral parts: the source asset handle, two
    fields that capture the identity and asset type associated with the
    handle, an amount to transfer, and a new owner (from the current
    list of public keys). In addition there is a transfer and refresh
    button.
    """

    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 wallet_path : str) :

        self.state = state
        self.bindings = bindings
        self.wallet_path = wallet_path

        self.source = ipywidgets.Dropdown(options=['unknown'], value=None, description="Source Handle")
        self.source.options = self.create_asset_list()
        self.source.observe(self.handle_source_change)

        self.old_owner = ipywidgets.Text(description="Old Owner", disabled=True)
        self.asset_type = ipywidgets.Text(description="Asset Type", disabled=True)
        self.balance = ipywidgets.IntSlider(description="Amount", min=0)

        self.new_owner = ipywidgets.Dropdown(options=[], description='New Owner')

        self.submit = ipywidgets.Button(description="Transfer", button_style='primary')
        self.submit.on_click(self.submit_button_click)

        self.refresh = ipywidgets.Button(description="Refresh", button_style='info')
        self.refresh.on_click(self.refresh_button_click)

        self.feedback = ipywidgets.Output()

        self.reset_widget()

        super().__init__(
            [
                self.source,
                self.old_owner,
                self.asset_type,
                self.balance,
                self.new_owner,
                ipywidgets.HBox([self.submit, self.refresh]),
                self.feedback
            ])

    def reset_widget(self) :
        """Reset all fields in the widget
        """
        self.source.options = self.create_asset_list()
        self.source.value = self.source.options[0]
        self.update_source_information()

        keys = self.create_key_list()
        self.new_owner.options = keys
        self.new_owner.value = keys[0]

    def create_asset_list(self) :
        """Create a list of assets in the wallet that could be transferred
        """
        context = pbuilder.Context(self.state, self.wallet_path)
        return context.get('asset_list', ['unknown'])

    def create_key_list(self) :
        """Create a list of public key names that could be used for the transfer
        """
        return jp_keys.build_public_key_list(self.state, self.bindings) or ['unknown']

    def update_source_information(self) :
        """Update the dependent fields from the currently selected source handle

        This presumes that the source field has been initialized with the currently
        available asset handles.
        """

        # take care of the case where no issuers have been imported into the wallet
        if self.source.value == 'unknown' :
            self.old_owner.disabled = False
            self.old_owner.value = 'unknown'
            self.old_owner.disabled = True

            self.asset_type.disabled = False
            self.asset_type.value = 'unknown'
            self.asset_type.disabled = True

            self.balance.value = 0
            self.balance.max = 0

            return

        asset_handle = self.source.value

        asset_type_information = get_asset_type(self.state, self.wallet_path, asset_handle)
        self.asset_type.disabled = False
        self.asset_type.value = asset_type_information['name']
        self.asset_type.disabled = True

        owner = get_asset_owner(self.state, self.wallet_path, asset_handle)
        self.old_owner.disabled = False
        self.old_owner.value = owner
        self.old_owner.disabled = True

        self.balance.value = 0
        self.balance.max = get_asset_balance(self.state, self.wallet_path, asset_handle)

    def handle_source_change(self, change) :
        """Handle a change to the source asset drop down
        """
        if change['type'] == 'change' and change['name'] == 'value' :
            self.update_source_information()

    def refresh_button_click(self, b) :
        """Handle the refresh button click

        In order to get most recent version of the contract, this will flush the
        contract cache.
        """
        self.feedback.clear_output()

        pcontract_cmd.flush_contract_cache()
        self.reset_widget()

    def submit_button_click(self, b) :
        """Invoke the function for handling the selection
        """
        self.feedback.clear_output()

        # validate the input state
        if self.source.value == 'unknown' :
            with self.feedback :
                print('select a valid source account')
            return

        if self.balance.value == 0 :
            with self.feedback :
                print('no assets specified for transfer')
            return

        if self.new_owner.value == 'unknown' :
            with self.feedback :
                print('no destination provided for transfer')
            return

        # and process the transfer
        asset_handle = self.source.value
        asset_type_name = self.asset_type.value
        count = self.balance.value
        max_count = self.balance.max
        new_owner = self.new_owner.value
        old_owner = self.old_owner.value

        try :
            transfer_assets(self.state, self.wallet_path, asset_handle, count, new_owner, old_owner)
        except Exception as e :
            with self.feedback :
                print(f'transfer failed with an error; {e}')
            return

        with self.feedback :
            print(f'transferred {count} {asset_type_name} assets from {old_owner} to {new_owner}')

        self.reset_widget()
        return

# -----------------------------------------------------------------
# -----------------------------------------------------------------
class ImportIssuerWidget(ipywidgets.VBox) :
    """Define a widget class for importing an issuer

    The widget consists of several parts: the identity (public key) of
    the account to use for interacting with the asset, a name for the
    asset (this name is local to the wallet and need not match the
    issuer's name for the asset), and the contract collections file for
    the issuer contracts that define the asset type. A button for
    performing the actual import and a feedback panel are included as
    well.
    """
    def __init__(self,
                 state : pbuilder.state.State,
                 bindings : pbuilder.bindings.Bindings,
                 context_file : str,
                 wallet_path : str) :

        self.state = state
        self.bindings = bindings

        self.context_file = context_file
        self.wallet_path = wallet_path

        self.identity = ipywidgets.Dropdown(description='Identity')
        self.identity.options = jp_keys.build_private_key_list(self.state, self.bindings) or ['unspecified']
        self.identity.value = self.identity.options[0]

        self.import_file = ipywidgets.FileUpload(accept='.zip', description='Contract File')

        self.asset_handle = ipywidgets.Text(description='Asset Handle')

        self.import_button = ipywidgets.Button(description='Import Contract', button_style='primary')
        self.import_button.on_click(self.import_button_click)

        self.refresh = ipywidgets.Button(description="Refresh", button_style='info')
        self.refresh.on_click(self.refresh_button_click)

        self.feedback = ipywidgets.Output()

        super().__init__(
            [
                ipywidgets.HBox([self.identity, self.import_file]),
                self.asset_handle,
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
        self.asset_handle.value = ''
        self.import_file.value = ()

    def import_button_click(self, b) :
        self.feedback.clear_output()

        # validate the inputs
        if not self.asset_handle.value or not re.match(r'^\w+$', self.asset_handle.value) :
            with self.feedback :
                print('Asset name must be a alphanumeric')
            return
        if not self.import_file.value :
            with self.feedback :
                print('No file specified')
            return

        try :
            import_name = self.import_file.value[0].name
            with tempfile.NamedTemporaryFile() as import_fp :
                asset_import_file = import_fp.name
                import_fp.write(self.import_file.value[0].content)

                with tempfile.NamedTemporaryFile() as context_fp :
                    asset_context_file = context_fp.name
                    asset_context = jp_util.import_contract_collection(
                        self.state, self.bindings, asset_context_file, asset_import_file)

            # merge the new context into the wallet context
            asset_path = self.asset_handle.value

            context = pbuilder.Context(self.state, self.wallet_path)
            context.set(asset_path, asset_context)
            context.set(asset_path + '.identity', self.identity.value)
            context.set('asset_list', context.get('asset_list', []) + [ asset_path ])
        except Exception as e :
            with self.feedback :
                print("failed to import the file; {}".format(e))
            return

        # save the updated context to the context file
        pbuilder.Context.SaveContextFile(self.state, self.context_file, prefix=self.wallet_path)

        self.clear_widget()
        with self.feedback :
            print("imported issuer contract information from {}".format(import_name))
