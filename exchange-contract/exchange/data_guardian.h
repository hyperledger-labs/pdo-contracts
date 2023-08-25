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

#include "token_object.h"

#define DG_INITIALIZE_PARAM_SCHEMA                      \
    "{"                                                 \
        SCHEMA_KW(token_issuer_code_hash,"") ","        \
        SCHEMA_KW(ledger_verifying_key,"")              \
    "}"

#define DG_PROVISION_TOKEN_ISSUER_PARAM_SCHEMA  \
    "{"                                         \
        SCHEMA_KW(contract_id,"")               \
    "}"

#define DG_PROVISION_TOKEN_OBJECT_PARAM_SCHEMA CONTRACT_SECRET_SCHEMA

#define DG_PROCESS_CAPABILITY_PARAM_SCHEMA TO_CAPABILITY_SCHEMA

namespace ww
{
namespace exchange
{
namespace data_guardian
{
    // Methods
    bool initialize_contract(const Environment& env);

    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool provision_token_issuer(const Message& msg, const Environment& env, Response& rsp);
    bool provision_token_object(const Message& msg, const Environment& env, Response& rsp);

    // Utility functions
    bool get_capability_keys(
        const std::string& minted_identity,
        std::string& encrypt_key,
        std::string& decrypt_key);
    bool parse_capability(
        const std::string& minted_identity,
        const ww::value::Object& operation_secret,
        ww::value::Object& operation);

}; // data_guardian
}; // exchange
}; // ww
