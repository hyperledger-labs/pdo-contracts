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

#pragma once

#include <string>

#include "Secret.h"
#include "Util.h"

#include "exchange/data_guardian.h"
#include "exchange/token_object.h"

#define DAG_INITIALIZE_PARAM_SCHEMA                             \
    "{"                                                         \
        SCHEMA_KW(public_border_width, 0) ","                   \
        SCHEMA_KW(encoded_image, "") ","                        \
        SCHEMA_KWS(guardian, DG_INITIALIZE_PARAM_SCHEMA)        \
    "}"

#define DAG_IMAGE_METADATA_SCHEMA               \
    "{"                                         \
        SCHEMA_KW(width, 0) ","                 \
        SCHEMA_KW(height, 0) ","                \
        SCHEMA_KW(byte-per-pixel, 0) ","        \
        SCHEMA_KW(public-border-width, 0) ","   \
        SCHEMA_KW(image_hash, "")               \
    "}"

namespace ww
{
namespace digital_asset
{
namespace guardian
{
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool process_capability(const Message& msg, const Environment& env, Response& rsp);

    // capability handlers, these must be executed through the process
    // capability interface
    bool get_public_image(const Message& msg, const Environment& env, Response& rsp);
    bool get_original_image(const Message& msg, const Environment& env, Response& rsp);
    bool get_image_metadata(const Message& msg, const Environment& env, Response& rsp);
} /* guardian */
} /* digital asset */
} /* ww
 */
