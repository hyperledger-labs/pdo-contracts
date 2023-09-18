/* Copyright 2022 Intel Corporation
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

#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"

namespace ww
{
namespace digital_asset
{
namespace token_object
{
    bool initialize_contract(const Environment& env);
    bool get_image_metadata(const Message& msg, const Environment& env, Response& rsp);
    bool get_public_image(const Message& msg, const Environment& env, Response& rsp);
    bool get_original_image(const Message& msg, const Environment& env, Response& rsp);
    bool decode_original_image(const Message& msg, const Environment& env, Response& rsp);
}; /* token_object */
}; /* digital_asset */
}; /* ww */
