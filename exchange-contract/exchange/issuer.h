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

#include "common/Escrow.h"

#define ISSUE_PARAM_SCHEMA                      \
    "{"                                         \
        SCHEMA_KW(owner_identity,"") ","        \
        SCHEMA_KW(count, 0)                     \
    "}"

#define TRANSFER_PARAM_SCHEMA                   \
    "{"                                         \
        SCHEMA_KW(new_owner_identity,"") ","    \
        SCHEMA_KW(count, 0)                     \
    "}"

#define ESCROW_PARAM_SCHEMA                     \
    "{"                                         \
        SCHEMA_KW(escrow_agent_identity,"") "," \
        SCHEMA_KW(count, 0)                     \
    "}"

#define ESCROW_ATTESTATION_PARAM_SCHEMA     \
    "{"                                     \
        SCHEMA_KW(escrow_agent_identity,"") \
    "}"

#define RELEASE_PARAM_SCHEMA                                    \
    "{"                                                         \
        SCHEMA_KWS(release_request, ESCROW_RELEASE_SCHEMA)      \
    "}"

#define CLAIM_PARAM_SCHEMA                              \
    "{"                                                 \
        SCHEMA_KWS(claim_request, ESCROW_CLAIM_SCHEMA)  \
    "}"


namespace ww
{
namespace exchange
{
namespace issuer
{
    bool initialize_contract(const Environment& env);
    bool issue(const Message& msg, const Environment& env, Response& rsp);
    bool get_balance(const Message& msg, const Environment& env, Response& rsp);
    bool get_entry(const Message& msg, const Environment& env, Response& rsp);
    bool transfer(const Message& msg, const Environment& env, Response& rsp);
    bool escrow(const Message& msg, const Environment& env, Response& rsp);
    bool escrow_attestation(const Message& msg, const Environment& env, Response& rsp);
    bool release(const Message& msg, const Environment& env, Response& rsp);
    bool claim(const Message& msg, const Environment& env, Response& rsp);
}; // issuer
}; // exchange
}; // ww
