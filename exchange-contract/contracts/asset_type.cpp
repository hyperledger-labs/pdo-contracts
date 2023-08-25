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

#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"

#include "exchange/asset_type.h"

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
    ASSERT_SUCCESS(rsp, ww::exchange::asset_type::initialize_contract(env),
                   "unexpected error: failed to initialize the contract");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(initialize, ww::exchange::asset_type::initialize),
    CONTRACT_METHOD2(get_asset_type_identifier, ww::exchange::asset_type::get_asset_type_identifier),
    CONTRACT_METHOD2(get_description, ww::exchange::asset_type::get_description),
    CONTRACT_METHOD2(get_link, ww::exchange::asset_type::get_link),
    CONTRACT_METHOD2(get_name, ww::exchange::asset_type::get_name),

    { NULL, NULL }
};
