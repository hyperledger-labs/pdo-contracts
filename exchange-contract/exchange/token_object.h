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

// This is the schema for the secret that is returned by the
// guardian for token object initialization
#define TO_INITIALIZATION_PACKAGE_SCHEMA                \
    "{"                                                 \
            SCHEMA_KW(token_description,"") ","         \
            SCHEMA_KW(token_metadata,{}) ","            \
            SCHEMA_KW(minted_identity,"") ","           \
            SCHEMA_KW(capability_generation_key,"")     \
    "}"

#define TO_INITIALIZE_PARAM_SCHEMA                                      \
    "{"                                                                 \
        SCHEMA_KW(ledger_verifying_key,"") ","                          \
        SCHEMA_KWS(initialization_package, CONTRACT_SECRET_SCHEMA) ","  \
        SCHEMA_KWS(asset_authority_chain, ISSUER_AUTHORITY_CHAIN_SCHEMA) \
    "}"

// This is the schema for the capability that will be interpreted
// by the guardian when performing an operation
#define TO_CAPABILITY_SCHEMA                            \
    "{"                                                 \
        SCHEMA_KW(minted_identity,"") ","               \
        SCHEMA_KWS(operation, CONTRACT_SECRET_SCHEMA)   \
    "}"

#define TO_OPERATION_SCHEMA                     \
    "{"                                         \
        SCHEMA_KW(nonce,"") ","                 \
        SCHEMA_KW(method_name, "") ","          \
        SCHEMA_KWS(parameters, "{}")            \
    "}"

namespace ww
{
namespace exchange
{
namespace token_object
{
    // methods
    bool initialize(const Message& msg, const Environment& env, Response& rsp);

    // the interface for these methods is copied from issuer contract
    bool transfer(const Message& msg, const Environment& env, Response& rsp);
    bool escrow(const Message& msg, const Environment& env, Response& rsp);
    bool escrow_attestation(const Message& msg, const Environment& env, Response& rsp);
    bool release(const Message& msg, const Environment& env, Response& rsp);
    bool claim(const Message& msg, const Environment& env, Response& rsp);

    // utility functions
    bool initialize_contract(const Environment& env);
    bool create_operation_package(
        const std::string& method_name,
        const ww::value::Object& parameters,
        ww::value::Object& capability_result);

}; // token_object
}; // exchange
}; // ww
