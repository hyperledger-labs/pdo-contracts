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

#define AT_INITIALIZE_PARAM_SCHEMA              \
    "{"                                         \
        SCHEMA_KW(description,"") ","           \
        SCHEMA_KW(link,"") ","                  \
        SCHEMA_KW(name,"")                      \
    "}"

namespace ww
{
namespace exchange
{
namespace asset_type
{
    bool initialize_contract(const Environment& env);
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool get_asset_type_identifier(const Message& msg, const Environment& env, Response& rsp);
    bool get_description(const Message& msg, const Environment& env, Response& rsp);
    bool get_link(const Message& msg, const Environment& env, Response& rsp);
    bool get_name(const Message& msg, const Environment& env, Response& rsp);



}; // asset_type
}; // exchange
}; // ww
