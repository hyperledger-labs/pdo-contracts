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

#define TIO_INITIALIZATION_PACKAGE_SCHEMA               \
    "{"                                                 \
            SCHEMA_KW(capability_management_key,"")     \
    "}"

#define TIO_INITIALIZE_PARAM_SCHEMA                                     \
    "{"                                                                 \
        SCHEMA_KW(token_description,"") ","                             \
        SCHEMA_KW(token_metadata,{}) ","                                \
        SCHEMA_KW(maximum_token_count,0) ","                            \
        SCHEMA_KW(token_object_code_hash,"") ","                        \
        SCHEMA_KW(ledger_verifying_key,"") ","                          \
        SCHEMA_KWS(initialization_package, CONTRACT_SECRET_SCHEMA) ","  \
        SCHEMA_KWS(asset_authority_chain, ISSUER_AUTHORITY_CHAIN_SCHEMA) \
    "}"

#define TIO_MINT_TOKEN_OBJECT_PARAM_SCHEMA      \
    "{"                                         \
        SCHEMA_KW(contract_id,"")               \
    "}"

#define TIO_PROVISION_MINTED_TOKEN_OBJECT_PARAM_SCHEMA  \
    "{"                                                 \
        SCHEMA_KW(ledger_signature,"") ","              \
        SCHEMA_KW(contract_id,"")                       \
    "}"

#define TIO_PROVISION_MINTED_TOKEN_SECRET_SCHEMA        \
    "{"                                                 \
        SCHEMA_KW(minted_identity,"") ","               \
        SCHEMA_KW(token_description,"") ","             \
        SCHEMA_KW(token_metadata,{}) ","                \
        SCHEMA_KW(token_object_encryption_key,"") ","   \
        SCHEMA_KW(token_object_verifying_key,"")        \
    "}"

namespace ww
{
namespace exchange
{
namespace token_issuer
{
    bool initialize_contract(const Environment& env);
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool mint_token_object(const Message& msg, const Environment& env, Response& rsp);
    bool provision_minted_token_object(const Message& msg, const Environment& env, Response& rsp);

    const std::string token_metadata_schema_key("token_metadata_schema");
}; // token_issuer
}; // exchange
}; // ww
