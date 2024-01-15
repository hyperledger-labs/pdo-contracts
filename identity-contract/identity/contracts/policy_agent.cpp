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

#include <string>
#include <stddef.h>
#include <stdint.h>

#include "Dispatch.h"

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "identity/policy_agent.h"
#include "identity/common/Credential.h"

static KeyValueStore policy_agent_store("policy_agent_store");

const std::string md_description_key("description");
const std::string md_schema_key("schema");

// -----------------------------------------------------------------
// METHOD: initialize_contract
//   contract initialization method
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   true if successfully initialized
// -----------------------------------------------------------------
bool ww::identity::policy_agent::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    return true;
}

// -----------------------------------------------------------------
// METHOD: initialize
//   set the basic information for the asset type
//
// JSON PARAMETERS:
//
// RETURNS:
//   true if successfully initialized
// -----------------------------------------------------------------
bool ww::identity::policy_agent::initialize(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(POLICY_AGENT_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // get the claims schema, combine it with the high level credential
    // schema and save that to the data store as the expected schema for
    // incoming credentials
    ww::value::Object claims_schema;
    ASSERT_SUCCESS(rsp, msg.get_value("claims_schema", claims_schema),
                   "unexpected error: failed to get claims_schema parameter");

    ww::value::Object credential_schema;
    ASSERT_SUCCESS(rsp, credential_schema.deserialize(CREDENTIAL_SCHEMA),
                   "unexpected error: failed to deserialize credential schema");
    ASSERT_SUCCESS(rsp, credential_schema.set_value("credentialSubject", claims_schema),
                   "unexpected error: failed to save credentialSubject");

    const std::string schema(credential_schema.serialize());
    ASSERT_SUCCESS(rsp, policy_agent_store.set(md_schema_key, schema),
                   "failed to store the link");

    // Mark as initialized
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "initialization failed");

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: validate_credential
//   set the basic information for the asset type
//
// JSON PARAMETERS:
//
// RETURNS:
//   true if successfully initialized
// -----------------------------------------------------------------
bool ww::identity::policy_agent::validate_credential(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(POLICY_AGENT_VALIDATE_CREDENTIAL_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    ww::value::Object credential;
    ASSERT_SUCCESS(rsp, msg.get_value("credential", credential),
                   "unexpected error: failed to get credential parameter");

    std::string schema;
    ASSERT_SUCCESS(rsp, policy_agent_store.get(md_schema_key, schema),
                   "unexpected error: failed to read the schema");

    if (! credential.validate_schema(schema.c_str()))
        return rsp.error("failed to validate the credential schema");

    // check the proof field?
    // generate a signature?

    return rsp.success(true);
}
