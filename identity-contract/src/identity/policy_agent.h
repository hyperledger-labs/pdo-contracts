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

#include "Environment.h"
#include "Message.h"
#include "Response.h"

#define POLICY_AGENT_REGISTER_ISSUER_PARAM_SCHEMA       \
    "{"                                                 \
        SCHEMA_KW(issuer_identity, "") ","              \
        SCHEMA_KW(public_key, "") ","                   \
        SCHEMA_KW(chain_code, "")                       \
    "}"


#define POLICY_AGENT_ISSUE_POLICY_CREDENTIAL_PARAM_SCHEMA       \
    "{"                                                         \
        SCHEMA_KWS(credential, VERIFIABLE_CREDENTIAL_SCHEMA)    \
    "}"

#define POLICY_AGENT_ISSUE_POLICY_CREDENTIAL_RESULT_SCHEMA      \
    VERIFIABLE_CREDENTIAL_SCHEMA

namespace ww
{
namespace identity
{
namespace policy_agent
{
    bool initialize_contract(const Environment& env);
    bool issue_policy_credential(const Message& msg, const Environment& env, Response& rsp);
    bool register_trusted_issuer(const Message& msg, const Environment& env, Response& rsp);

}; // policy_agent
}; // identity
}; // ww
