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

#pragma once

#include <string>

#include "Util.h"

#define ECHO_PARAM_SCHEMA                       \
    "{"                                         \
        SCHEMA_KW(message,"")                   \
    "}"

#define INFERENCE_PARAM_SCHEMA                   \
    "{"                                         \
        SCHEMA_KW(encryption_key, "") ","       \
        SCHEMA_KW(state_hash, "") ","           \
        SCHEMA_KW(image_key, "")                \
    "}"

namespace ww
{
namespace inference
{
namespace token_object
{
    // methods
    bool do_inference(const Message& msg, const Environment& env, Response& rsp);
}; // token_object
}; // inference
}; // ww
