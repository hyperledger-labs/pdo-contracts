# Copyright 2022 Intel Corporation
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

import json
import logging

from pdo.contract import invocation_request

import pdo.client.builder as pbuilder
import pdo.client.builder.command as pcommand
import pdo.client.builder.contract as pcontract
import pdo.client.builder.shell as pshell
import pdo.client.commands.contract as pcontract_cmd

import pdo.client.plugins.common as common
import pdo.exchange.plugins.issuer as pi_issuer

__all__ = [
    'op_get_verifying_key',
    'op_initialize',
    'op_cancel_exchange',
    'op_examine_offered_asset',
    'op_examine_requested_asset',
    'op_exchange',
    'op_claim_offered_asset',
    'op_claim_exchanged_asset',
    'cmd_create_order',
    'cmd_match_order',
    'cmd_cancel_order',
    'cmd_examine_order',
    'cmd_claim_offer',
    'cmd_claim_payment',
    'cmd_release',
    'do_exchange',
    'do_exchange_contract',
    'load_commands',
]

op_get_verifying_key = common.op_get_verifying_key

logger = logging.getLogger(__name__)

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_initialize(pcontract.contract_op_base) :

    name = "initialize"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--asset',
            help='offered authoriative asset, must be escrowed to the exchange contract',
            type=pbuilder.invocation_parameter,
            required=True)
        subparser.add_argument(
            '-i', '--issuer',
            help='verifying key for the requested issuer',
            type=pbuilder.invocation_parameter,
            required=True)
        subparser.add_argument(
            '-t', '--type_id',
            help='contract identifier for the requested asset type',
            type=pbuilder.invocation_parameter,
            required=True)
        subparser.add_argument(
            '-o', '--owner',
            help='identity of the asset owner; ECDSA key',
            type=str, default="")
        subparser.add_argument(
            '-c', '--count',
            help='amount requested',
            type=int,
            required=True)


    @classmethod
    def invoke(cls, state, session_params, asset, issuer, type_id, owner, count, **kwargs) :
        session_params['commit'] = True

        asset_request = {
            "issuer_verifying_key" : issuer,
            "asset_type_identifier" : type_id,
            "count" : count,
            "owner_identity" : owner
        }
        message = invocation_request('initialize', asset_request=asset_request, offered_authoritative_asset=asset)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_cancel_exchange(pcontract.contract_op_base) :

    name = "cancel_exchange"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = True
        message = invocation_request('cancel_exchange')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        session_params['commit'] = False
        message = invocation_request('cancel_exchange_attestation')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_examine_offered_asset(pcontract.contract_op_base) :

    name = "examine_offered_asset"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('examine_offered_asset')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_examine_requested_asset(pcontract.contract_op_base) :

    name = "examine_requested_asset"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('examine_requested_asset')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_exchange(pcontract.contract_op_base) :

    name = "exchange"
    help = ""

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '-a', '--asset',
            help='exchanged authoriative asset, must be escrowed to the exchange contract',
            type=pbuilder.invocation_parameter,
            required=True)

    @classmethod
    def invoke(cls, state, session_params, asset, **kwargs) :
        session_params['commit'] = True

        message = invocation_request('exchange_asset', exchanged_authoritative_asset=asset)
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_claim_offered_asset(pcontract.contract_op_base) :

    name = "claim_offered_asset"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('claim_offered_asset')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class op_claim_exchanged_asset(pcontract.contract_op_base) :

    name = "claim_exchanged_asset"
    help = ""

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        session_params['commit'] = False

        message = invocation_request('claim_exchanged_asset')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        cls.log_invocation(message, result)

        return result

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_create_order(pcommand.contract_command_base) :
    name = "create_order"
    help = "script to create an exchange order"

    @classmethod
    def add_arguments(cls, subparser) :
        # issuer specific parameters
        subparser.add_argument(
            '--offer-issuer',
            help='context identifier for the issuer of the offered assets',
            type=str)
        subparser.add_argument(
            '--offer-count',
            help='amount of assets being offered',
            type=int)
        subparser.add_argument(
            '--request-issuer',
            help='context identifier for the issuer of the requested assets',
            type=str)
        subparser.add_argument(
            '--request-user',
            help='identity of the asset owner',
            type=str)
        subparser.add_argument(
            '--request-count',
            help='amount requested',
            type=int)

        subparser.add_argument(
            '-c', '--contract-class',
            help='Name of the contract class',
            type=str)

        # contract creation general parameters
        subparser.add_argument(
            '-e', '--eservice-group',
            help='Name of the enclave service group to use',
            type=str)

        subparser.add_argument(
            '-f', '--save-file',
            help='File where contract data is stored',
            type=str)

        subparser.add_argument(
            '-p', '--pservice-group',
            help='Name of the provisioning service group to use',
            type=str)

        subparser.add_argument(
            '-r', '--sservice-group',
            help='Name of the storage service group to use',
            type=str)

        subparser.add_argument(
            '--source',
            help='File that contains contract source code',
            type=str)

        subparser.add_argument(
            '--extra',
            help='Extra data associated with the contract file',
            nargs=2, action='append')

    @classmethod
    def invoke(cls,
               state, context,
               offer_issuer=None, offer_count=None,
               request_issuer=None, request_user=None, request_count=None,
               **kwargs) :

        # we need to make sure all operation use the current identity, the current identity
        # will generally have been set from the context or the command line
        if kwargs.get('identity') is None :
            kwargs['identity'] = state.identity

        # --------------------------------------------------
        # process information about the request
        # --------------------------------------------------

        # first see if there is an issuer specified either as a parameter or in the context file
        request_issuer_verifying_key = ""
        request_issuer_context = None
        if request_issuer :
            request_issuer_context = Context(state, request_issuer)
        elif context.has_key('request.issuer_context') :
            request_issuer_context = context.get_context('request.issuer_context')
        if request_issuer_context is None :
            raise ValueError('missing required parameter request_issuer')

        request_issuer_save_file = pcontract_cmd.get_contract_from_context(state, request_issuer_context)
        if request_issuer_save_file is None :
            raise ValueError("request issuer contract has not been created or is unknown")

        request_issuer_session = pbuilder.SessionParameters(save_file=request_issuer_save_file)
        request_issuer_verifying_key = pcontract.invoke_contract_op(
            common.op_get_verifying_key,
            state, request_issuer_context, request_issuer_session,
            **kwargs)
        request_issuer_verifying_key = json.loads(request_issuer_verifying_key)

        asset_type_contract_id = pcontract.invoke_contract_op(
            pi_issuer.op_get_asset_type_identifier,
            state, request_issuer_context, request_issuer_session,
            **kwargs)
        asset_type_contract_id = json.loads(asset_type_contract_id)

        # now see if there is a specific user specified
        user_verifying_key = ""
        user_identity = request_user or context.get('request.user_identity')
        if user_identity is not None :
            keypath = state.get(['Key', 'SearchPath'])
            keyfile = putils.find_file_in_path("{0}_public.pem".format(user_identity), keypath)
            with open (keyfile, "r") as myfile:
                user_verifying_key = myfile.read()

        # lastly make sure the count is set
        request_count = int(request_count) if request_count is not None else int(context.get('request.count', 1))

        # --------------------------------------------------
        # process information about the offer
        # --------------------------------------------------
        if offer_issuer :
            offer_issuer_context = Context(state, offer_issuer)
        else :
            offer_issuer_context = context.get_context('offer.issuer_context')
            if offer_issuer_context is None :
                raise ValueError('missing required parameter offer_issuer')

        offer_issuer_save_file = pcontract_cmd.get_contract_from_context(state, offer_issuer_context)
        if offer_issuer_save_file is None :
            raise ValueError("issuer contract has not been created")

        offer_issuer_session = pbuilder.SessionParameters(save_file=offer_issuer_save_file)

        # make sure there is a count
        offer_count = int(offer_count) if offer_count is not None else int(context.get('offer.count', 1))

        # --------------------------------------------------
        # now create the exchange contract
        # --------------------------------------------------
        if  pcontract_cmd.get_contract_from_context(state,context) :
            raise ValueError("exchange contract already exists")

        save_file = pcontract_cmd.create_contract_from_context(state, context, 'exchange_contract', **kwargs)
        context['save_file'] = save_file

        # prepare the material to initialize the exchange contract
        session = pbuilder.SessionParameters(save_file=save_file)
        verifying_key = pcontract.invoke_contract_op(common.op_get_verifying_key, state, context, session)
        verifying_key = json.loads(verifying_key)

        # escrow the offered assets to the exchange contract
        escrow_attestation = pcontract.invoke_contract_op(
            pi_issuer.op_escrow,
            state, offer_issuer_context, offer_issuer_session,
            verifying_key,
            offer_count,
            **kwargs)
        escrow_attestation = json.loads(escrow_attestation)

        # initialize
        try :
            pcontract.invoke_contract_op(
                op_initialize,
                state, context, session,
                escrow_attestation,
                request_issuer_verifying_key,
                asset_type_contract_id,
                user_verifying_key,
                request_count,
                **kwargs)
        except Exception as e :
            # eventually we need to release the assets from escrow when
            # the contract fails to initialize correctly
            raise e

        return save_file

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_match_order(pcommand.contract_command_base) :
    name = "match_order"
    help = "script to match an order"

    @classmethod
    def add_arguments(cls, subparser) :
        subparser.add_argument(
            '--issuer',
            help='context identifier for the issuer of the offered assets',
            type=pbuilder.invocation_parameter)
        subparser.add_argument(
            '--count',
            help='amount of assets being offered',
            type=int)

    @classmethod
    def invoke(cls, state, context, issuer=None, count=None, **kwargs) :
        # get the exchange contract reference
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('order contract must be created and initialized')
        session = pbuilder.SessionParameters(save_file=save_file)

        # get the issuer that will provide the assets
        if issuer :
            issuer_context = Context(state, issuer)
        else :
            issuer_context = context.get_context('request.issuer_context')
        issuer_save_file = pcontract_cmd.get_contract_from_context(state, issuer_context)
        if issuer_save_file is None :
            raise ValueError("unable to locate issuer contract")

        issuer_session = pbuilder.SessionParameters(save_file=issuer_save_file)

        # make sure there is a count
        count = int(count) if count is not None else context['request.count']

        # prepare the material to initialize the exchange contract
        verifying_key = pcontract.invoke_contract_op(common.op_get_verifying_key, state, context, session)
        verifying_key = json.loads(verifying_key)

        # escrow the offered assets to the exchange contract
        escrow_attestation = pcontract.invoke_contract_op(
            pi_issuer.op_escrow,
            state, issuer_context, issuer_session,
            verifying_key,
            count,
            **kwargs)
        escrow_attestation = json.loads(escrow_attestation)

        try :
            pcontract.invoke_contract_op(
                op_exchange,
                state, context, session,
                escrow_attestation,
                **kwargs)
        except Exception as e :
            # eventually we need to release the assets from escrow when
            # the offer is rejected
            raise e

        cls.display('offer made and accepted')
        return save_file

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_cancel_order(pcommand.contract_command_base) :
    name = "cancel"
    help = "script to cancel the exchange and release offered assets from escrow"

    @classmethod
    def invoke(cls, state, context, **kwargs) :

        # get the issuer contract reference
        issuer_context = context.get_context('offer.issuer_context')
        issuer_save_file = pcontract_cmd.get_contract_from_context(state, issuer_context)
        if not issuer_save_file :
            raise ValueError('failed to find the issuer contract')
        issuer_session = pbuilder.SessionParameters(save_file=issuer_save_file)

        # get the exchange contract reference
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('order contract must be created and initialized')
        session = pbuilder.SessionParameters(save_file=save_file)

        # cancel the exchange
        escrow_release_attestation = pcontract.invoke_contract_op(
            op_cancel_exchange,
            state, context, session,
            **kwargs)
        escrow_release_attestation = json.loads(escrow_release_attestation)

        # release the assets from escro
        pcontract.invoke_contract_op(
            pi_issuer.op_release,
            state, context, issuer_session,
            escrow_release_attestation,
            **kwargs)

        cls.display('exchange cancelled')
        return save_file

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_examine_order(pcommand.contract_command_base) :
    name = "examine"
    help = "script to "

    @classmethod
    def add_arguments(cls, parser) :
        pass

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('order contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)

        offered_asset = pcontract.invoke_contract_op(
            op_examine_offered_asset,
            state, context, session,
            **kwargs)
        offered_asset = json.loads(offered_asset)

        cls.display_highlight('offered asset is:')
        cls.display(json.dumps(offered_asset, indent=4))

        requested_asset = pcontract.invoke_contract_op(
            op_examine_requested_asset,
            state, context, session,
            **kwargs)
        requested_asset = json.loads(requested_asset)

        cls.display('')
        cls.display_highlight('requested asset is:')
        cls.display(json.dumps(requested_asset, indent=4))


## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_claim_offer(pcommand.contract_command_base) :
    name = "claim_offer"
    help = "script to claim the offered asset"

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        # we need to make sure all operation use the current identity, the current identity
        # will generally have been set from the context or the command line
        if kwargs.get('identity') is None :
            kwargs['identity'] = state.identity

        # handles for the exchange contract
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('order contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)

        # handles for the issuer contract, note that we could extract the
        # contract information directly from the information about the offered
        # asset, for now we'll do the easy thing and just assume its in the
        # offer context
        offer_issuer_context = context.get_context('offer.issuer_context')
        offer_issuer_save_file = pcontract_cmd.get_contract_from_context(state, offer_issuer_context)
        if offer_issuer_save_file is None :
            raise ValueError("issuer contract has not been created")

        offer_issuer_session = pbuilder.SessionParameters(save_file=offer_issuer_save_file)

        # now get the claim attestation
        offered_asset_claim = pcontract.invoke_contract_op(
            op_claim_offered_asset,
            state, context, session,
            **kwargs)
        offered_asset_claim = json.loads(offered_asset_claim)

        # and send it to the offer issuer to transfer the assets & release the escrow
        pcontract.invoke_contract_op(
            pi_issuer.op_claim,
            state, offer_issuer_context, offer_issuer_session,
            offered_asset_claim,
            **kwargs)

        cls.display('offered assets claimed')
        return save_file

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_claim_payment(pcommand.contract_command_base) :
    name = "claim_payment"
    help = "script to claim the payment"

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        # we need to make sure all operation use the current identity, the current identity
        # will generally have been set from the context or the command line
        if kwargs.get('identity') is None :
            kwargs['identity'] = state.identity

        # handles for the exchange contract
        save_file = pcontract_cmd.get_contract_from_context(state, context)
        if not save_file :
            raise ValueError('order contract must be created and initialized')

        session = pbuilder.SessionParameters(save_file=save_file)

        # handles for the issuer contract, note that we could extract the
        # contract information directly from the information about the offered
        # asset, for now we'll do the easy thing and just assume its in the
        # offer context
        request_issuer_context = context.get_context('request.issuer_context')
        request_issuer_save_file = pcontract_cmd.get_contract_from_context(state, request_issuer_context)
        if request_issuer_save_file is None :
            raise ValueError("issuer contract has not been created")

        request_issuer_session = pbuilder.SessionParameters(save_file=request_issuer_save_file)

        # now get the claim attestation
        requested_asset_claim = pcontract.invoke_contract_op(
            op_claim_exchanged_asset,
            state, context, session,
            **kwargs)
        requested_asset_claim = json.loads(requested_asset_claim)

        # and send it to the offer issuer to transfer the assets & release the escrow
        pcontract.invoke_contract_op(
            pi_issuer.op_claim,
            state, request_issuer_context, request_issuer_session,
            requested_asset_claim,
            **kwargs)

        cls.display('requested assets claimed')
        return save_file

## -----------------------------------------------------------------
## -----------------------------------------------------------------
class cmd_release(pcommand.contract_command_base) :
    name = "release"
    help = "script to release escrow on unused exchange assets"

    @classmethod
    def add_arguments(cls, parser) :
        pass

    @classmethod
    def invoke(cls, state, context, **kwargs) :
        pass

## -----------------------------------------------------------------
## Create the generic, shell independent version of the aggregate command
## -----------------------------------------------------------------
__operations__ = [
    op_get_verifying_key,
    op_initialize,
    op_cancel_exchange,
    op_examine_offered_asset,
    op_examine_requested_asset,
    op_exchange,
    op_claim_offered_asset,
    op_claim_exchanged_asset,
]

do_exchange_contract = pcontract.create_shell_command('exchange_contract', __operations__)

__commands__ = [
    cmd_create_order,
    cmd_match_order,
    cmd_cancel_order,
    cmd_examine_order,
    cmd_claim_offer,
    cmd_claim_payment,
    cmd_release,
]

do_exchange = pcommand.create_shell_command('exchange', __commands__)

## -----------------------------------------------------------------
## Enable binding of the shell independent version to a pdo-shell command
## -----------------------------------------------------------------
def load_commands(cmdclass) :
    pshell.bind_shell_command(cmdclass, 'exchange', do_exchange)
    pshell.bind_shell_command(cmdclass, 'exchange_contract', do_exchange_contract)
