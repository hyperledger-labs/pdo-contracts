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

#include <algorithm>
#include <stddef.h>
#include <stdint.h>

#include "Dispatch.h"

#include "Cryptography.h"
#include "Environment.h"
#include "KeyValue.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "contract/attestation.h"
#include "exchange/data_guardian.h"

#include "digital_asset/guardian.h"

// -----------------------------------------------------------------
// NAME: initialize_contract
// -----------------------------------------------------------------
bool initialize_contract(const Environment& env, Response& rsp)
{
    ASSERT_SUCCESS(rsp, ww::digital_asset::guardian::initialize_contract(env),
                   "failed to initialize the contract");

    return rsp.success(true);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(initialize, ww::digital_asset::guardian::initialize),

    // from the attestation contract
    CONTRACT_METHOD2(get_ledger_key, ww::contract::attestation::get_ledger_key),
    CONTRACT_METHOD2(get_contract_metadata, ww::contract::attestation::get_contract_metadata),
    CONTRACT_METHOD2(get_contract_code_metadata, ww::contract::attestation::get_contract_code_metadata),
    CONTRACT_METHOD2(add_endpoint, ww::contract::attestation::add_endpoint),

    // use the asset
    CONTRACT_METHOD2(provision_token_issuer, ww::exchange::data_guardian::provision_token_issuer),
    CONTRACT_METHOD2(provision_token_object, ww::exchange::data_guardian::provision_token_object),
    CONTRACT_METHOD2(process_capability, ww::digital_asset::guardian::process_capability),

    { NULL, NULL }
};
