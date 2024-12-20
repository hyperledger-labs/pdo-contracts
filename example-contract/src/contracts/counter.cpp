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

#include "Dispatch.h"

#include "Environment.h"
#include "Response.h"

#include "example/counter.h"

// -----------------------------------------------------------------
// NAME: initialize_contract
// -----------------------------------------------------------------
bool initialize_contract(const Environment& env, Response& rsp)
{
    return ww::example_contract::counter::initialize_contract(env, rsp);
}

contract_method_reference_t contract_method_dispatch_table[] = {
    CONTRACT_METHOD2(inc_value, ww::example_contract::counter::inc_value),
    CONTRACT_METHOD2(get_value, ww::example_contract::counter::get_value),
    { NULL, NULL }
};
