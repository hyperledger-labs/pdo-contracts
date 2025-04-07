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
#include "Value.h"

#include "common/Credential.h"
#include "common/VerifyingContext.h"

#define POLICY_AGENT_REGISTER_ISSUER_PARAM_SCHEMA       \
    "{"                                                 \
        SCHEMA_KW(issuer_identity, "") ","              \
        SCHEMA_KW(context_path, [ "" ]) ","             \
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
    // Policy Agent contract methods
    bool initialize_contract(const Environment& env);
    bool issue_policy_credential(const Message& msg, const Environment& env, Response& rsp);
    bool register_trusted_issuer(const Message& msg, const Environment& env, Response& rsp);

    // Functions to extend the functionality of the policy agent
    bool save_trusted_issuer(const std::string& issuer_id, const ww::identity::VerifyingContext& vc);
    bool fetch_trusted_issuer(const std::string& issuer_id, ww::identity::VerifyingContext& vc);
    bool verify_credential(const ww::value::Object& vc_object, ww::identity::VerifiableCredential vc);
    bool issue_credential(
        const std::string& originator,
        const std::string& contract_id,
        const ww::identity::Credential& credential,
        ww::identity::VerifiableCredential& vc);

    // This function must be defined by the contract, this is not a very clean way to do
    // this but WASM does not seem to support function pointers very well
    bool policy_agent_function(const ww::identity::Credential&, ww::identity::Credential);

}; // policy_agent
}; // identity
}; // ww
