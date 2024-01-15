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
#include "Util.h"

#include "common/Credential.h"

#define POLICY_AGENT_INITIALIZE_PARAM_SCHEMA         \
    "{"                                                 \
        SCHEMA_KWS(claims_schema, CLAIMS_SCHEMA)        \
    "}"

#define POLICY_AGENT_VALIDATE_CREDENTIAL_PARAM_SCHEMA        \
    "{"                                                         \
        SCHEMA_KW(credential, CREDENTIAL_SCHEMA)                \
    "}"

namespace ww
{
namespace identity
{
namespace policy_agent
{
    bool initialize_contract(const Environment& env);
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool validate_credential(const Message& msg, const Environment& env, Response& rsp);
}; // policy_agent
}; // identity
}; // ww
