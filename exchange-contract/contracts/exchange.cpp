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

#include <stddef.h>
#include <stdint.h>
#include <string>

#include "Dispatch.h"

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "exchange/exchange.h"

// -----------------------------------------------------------------
// METHOD: initialize_contract
//   contract initialization method
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   true if successfully initialized
// -----------------------------------------------------------------
bool initialize_contract(const Environment& env, Response& rsp)
{
    ASSERT_SUCCESS(rsp, ww::exchange::exchange::initialize_contract(env),
                   "failed to initialize the base contract");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(initialize, ww::exchange::exchange::initialize),
    CONTRACT_METHOD2(get_verifying_key, ww::contract::base::get_verifying_key),
    CONTRACT_METHOD2(cancel_exchange, ww::exchange::exchange::cancel_exchange),
    CONTRACT_METHOD2(cancel_exchange_attestation, ww::exchange::exchange::cancel_exchange_attestation),
    CONTRACT_METHOD2(examine_offered_asset, ww::exchange::exchange::examine_offered_asset),
    CONTRACT_METHOD2(examine_requested_asset, ww::exchange::exchange::examine_requested_asset),

    CONTRACT_METHOD2(exchange_asset, ww::exchange::exchange::exchange_asset),
    CONTRACT_METHOD2(claim_exchanged_asset, ww::exchange::exchange::claim_exchanged_asset),
    CONTRACT_METHOD2(claim_offered_asset, ww::exchange::exchange::claim_offered_asset),
    CONTRACT_METHOD2(release_asset, ww::exchange::exchange::release_asset),

    { NULL, NULL }
};
