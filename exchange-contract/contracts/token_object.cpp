/* Copyright 2019 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <string>
#include <stddef.h>
#include <stdint.h>

#include "Dispatch.h"

#include "Cryptography.h"
#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "contract/attestation.h"
#include "exchange/issuer_authority_base.h"
#include "exchange/token_object.h"
#include "token_object.h"

// -----------------------------------------------------------------
// METHOD: initialize_contract
// -----------------------------------------------------------------
bool initialize_contract(const Environment& env, Response& rsp)
{
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::initialize_contract(env),
                   "failed to initialize the base contract");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// echo
//
// This generates a capability that can be fed to the sample guardian
// contract to echo the input parameter.
// -----------------------------------------------------------------
bool echo(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema("{\"message\":\"\"}"),
                   "invalid request, missing required parameters");

    const std::string message(msg.get_string("message"));
    ww::value::Structure params("{\"message\":\"\"}");
    ASSERT_SUCCESS(rsp, params.set_string("message", message.c_str()),
                   "unexpected error: failed to store message");

    ww::value::Object result;
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::create_operation_package("echo", params, result),
                   "unexpected error: failed to generate capability");

    // this assumes that generating the capability does not change state, depending on
    // how the nonce is created this may need to change.
    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(initialize,ww::exchange::token_object::initialize),
    CONTRACT_METHOD2(get_verifying_key, ww::contract::base::get_verifying_key),

    // issuer methods
    CONTRACT_METHOD2(get_asset_type_identifier, ww::exchange::issuer_authority_base::get_asset_type_identifier),
    CONTRACT_METHOD2(get_issuer_authority, ww::exchange::issuer_authority_base::get_issuer_authority),
    CONTRACT_METHOD2(get_authority, ww::exchange::issuer_authority_base::get_authority),

    // from the attestation contract
    CONTRACT_METHOD2(get_contract_metadata, ww::contract::attestation::get_contract_metadata),
    CONTRACT_METHOD2(get_contract_code_metadata, ww::contract::attestation::get_contract_code_metadata),

    // use the asset
    CONTRACT_METHOD(echo),

    // object transfer, escrow & claim methods
    CONTRACT_METHOD2(get_balance,ww::exchange::token_object::get_balance),
    CONTRACT_METHOD2(transfer,ww::exchange::token_object::transfer),
    CONTRACT_METHOD2(escrow,ww::exchange::token_object::escrow),
    CONTRACT_METHOD2(escrow_attestation,ww::exchange::token_object::escrow_attestation),
    CONTRACT_METHOD2(release,ww::exchange::token_object::release),
    CONTRACT_METHOD2(claim,ww::exchange::token_object::claim),

    { NULL, NULL }
};
