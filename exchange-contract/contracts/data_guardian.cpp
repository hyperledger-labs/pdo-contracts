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

#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"

#include "contract/attestation.h"
#include "contract/base.h"
#include "exchange/data_guardian.h"
#include "token_object.h"

// -----------------------------------------------------------------
// METHOD: initialize_contract
// -----------------------------------------------------------------
bool initialize_contract(const Environment& env, Response& rsp)
{
    ASSERT_SUCCESS(rsp, ww::exchange::data_guardian::initialize_contract(env),
                   "failed to initialize the base contract");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// process_capability
//
// Perform an operation on the asset in the guardian.
// -----------------------------------------------------------------
bool process_capability(const Message& msg, const Environment& env, Response& rsp)
{
    // note that we specifically DO NOT verify the identity of the
    // invoker... possession of a valid capability is sufficient to
    // prove the right to invoke the operation

    ASSERT_INITIALIZED(rsp);
    ASSERT_SUCCESS(rsp, msg.validate_schema(DG_PROCESS_CAPABILITY_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string minted_identity(msg.get_string("minted_identity"));
    ww::value::Object operation_secret;
    ASSERT_SUCCESS(rsp, msg.get_value("operation", operation_secret),
                   "unexpected error: failed to get value");

    ww::value::Object operation;
    ASSERT_SUCCESS(rsp, ww::exchange::data_guardian::parse_capability(minted_identity, operation_secret, operation),
                   "invalid capability");

    const std::string method_name(operation.get_string("method_name"));
    ww::value::Object params;
    ASSERT_SUCCESS(rsp, operation.get_value("parameters", params),
                   "unexpected error: failed to get value");
    ASSERT_SUCCESS(rsp, params.validate_schema(ECHO_PARAM_SCHEMA),
                   "invalid operation, missing required parameters");

    ww::value::String result(params.get_string("message"));

    // for now we assume that state has not changed, this may not be
    // true in the future
    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(initialize, ww::exchange::data_guardian::initialize),

    // from the attestation contract
    CONTRACT_METHOD2(get_ledger_key, ww::contract::attestation::get_ledger_key),
    CONTRACT_METHOD2(get_contract_metadata, ww::contract::attestation::get_contract_metadata),
    CONTRACT_METHOD2(get_contract_code_metadata, ww::contract::attestation::get_contract_code_metadata),
    CONTRACT_METHOD2(add_endpoint, ww::contract::attestation::add_endpoint),

    // use the asset
    CONTRACT_METHOD2(provision_token_issuer, ww::exchange::data_guardian::provision_token_issuer),
    CONTRACT_METHOD2(provision_token_object, ww::exchange::data_guardian::provision_token_object),
    CONTRACT_METHOD(process_capability),

    { NULL, NULL }
};
