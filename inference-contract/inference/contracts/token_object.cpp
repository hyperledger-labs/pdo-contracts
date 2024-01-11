/* Copyright 2023 Intel Corporation
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
#include "exchange/token_object.h"
#include "inference/token_object.h"

// -----------------------------------------------------------------
// do_inference
//
// This generates a capability that can be fed to the sample guardian
// contract to do inference with an openvino model
// -----------------------------------------------------------------
bool ww::inference::token_object::do_inference(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(INFERENCE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string encoded_encryption_key(msg.get_string("encryption_key"));
    const std::string encoded_state_hash(msg.get_string("state_hash"));
    const std::string image_key(msg.get_string("image_key"));

    ww::value::Structure params(INFERENCE_PARAM_SCHEMA);
    ASSERT_SUCCESS(rsp, params.set_string("encryption_key", encoded_encryption_key.c_str()),
                   "unexpected error: failed to store parameter");
    ASSERT_SUCCESS(rsp, params.set_string("state_hash", encoded_state_hash.c_str()),
                   "unexpected error: failed to store parameter");
    ASSERT_SUCCESS(rsp, params.set_string("image_key", image_key.c_str()),
                   "unexpected error: failed to store parameter");

    ww::value::Object result;
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::create_operation_package("do_inference", params, result),
                   "unexpected error: failed to generate capability");

    // this assumes that generating the capability does not change state, depending on
    // how the nonce is created this may need to change.
    return rsp.value(result, false);
}
