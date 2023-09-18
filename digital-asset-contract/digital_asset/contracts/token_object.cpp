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
#include "exchange/issuer_authority_base.h"
#include "exchange/token_object.h"
#include "digital_asset/token_object.h"

// -----------------------------------------------------------------
// METHOD: initialize_contract
// -----------------------------------------------------------------
bool ww::digital_asset::token_object::initialize_contract(const Environment& env)
{
    return ww::exchange::token_object::initialize_contract(env);
}

// -----------------------------------------------------------------
// METHOD: get_image_metadata
// -----------------------------------------------------------------
bool ww::digital_asset::token_object::get_image_metadata(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ww::value::Object params;
    ww::value::Object result;
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::create_operation_package("get_image_metadata", params, result),
                   "unexpected error: failed to generate capability");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: get_public_image
// -----------------------------------------------------------------
bool ww::digital_asset::token_object::get_public_image(const Message& msg, const Environment& env, Response& rsp)
{
    // Anyone is allowed to get the public image
    ASSERT_INITIALIZED(rsp);

    ww::value::Object params;
    ww::value::Object result;
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::create_operation_package("get_public_image", params, result),
                   "unexpected error: failed to generate capability");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: get_original_image
// -----------------------------------------------------------------
bool ww::digital_asset::token_object::get_original_image(const Message& msg, const Environment& env, Response& rsp)
{
    // Only the owner may get the original image
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ww::value::Object params;
    ww::value::Object result;
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::create_operation_package("get_original_image", params, result),
                   "unexpected error: failed to generate capability");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: decode_original_image
// -----------------------------------------------------------------
bool ww::digital_asset::token_object::decode_original_image(const Message& msg, const Environment& env, Response& rsp)
{
    return rsp.error("not implemented");
}
