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

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "exchange/issuer_authority_base.h"
#include "exchange/vetting_organization.h"

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
    // ---------- initialize the base contract ----------
    ASSERT_SUCCESS(rsp, ww::exchange::vetting_organization::initialize_contract(env),
                   "failed to initialize the base contract");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(initialize, ww::exchange::issuer_authority_base::initialize_root_authority),
    CONTRACT_METHOD2(get_verifying_key, ww::contract::base::get_verifying_key),
    CONTRACT_METHOD2(get_asset_type_identifier, ww::exchange::issuer_authority_base::get_asset_type_identifier),
    CONTRACT_METHOD2(add_approved_issuer, ww::exchange::issuer_authority_base::add_approved_issuer),
    CONTRACT_METHOD2(get_issuer_authority, ww::exchange::issuer_authority_base::get_issuer_authority),
    { NULL, NULL }
};
