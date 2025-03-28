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

#include "Cryptography.h"
#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "identity/identity.h"
#include "identity/policy_agent.h"
#include "identity/common/Credential.h"
#include "identity/common/VerifyingContext.h"

static KeyValueStore trusted_issuer_store("issuer_store");

// -----------------------------------------------------------------
// FUNCTION: save_trusted_issuer
// -----------------------------------------------------------------
bool save_trusted_issuer(
    const std::string& issuer_id,
    const ww::identity::VerifyingContext& vc)
{
    // ---------- save the trusted issuer ----------
    ww::value::Value trusted_issuer;
    ERROR_IF_NOT(vc.serialize(trusted_issuer),
                 "unexpected error, failed to serialize trusted issuer");

    std::string trusted_issuer_str;
    ERROR_IF_NOT(trusted_issuer.serialize(trusted_issuer_str),
                 "unexpected error, failed to serialize trusted issuer");

    return trusted_issuer_store.set(issuer_id, trusted_issuer_str);
}

// -----------------------------------------------------------------
// FUNCTION: fetch_trusted_issuer
// -----------------------------------------------------------------
bool fetch_trusted_issuer(
    const std::string& issuer_id,
    ww::identity::VerifyingContext& vc)
{
    // ---------- fetch the trusted issuer ----------
    std::string trusted_issuer_str;
    ERROR_IF_NOT(trusted_issuer_store.get(issuer_id, trusted_issuer_str),
                 "unexpected error, failed to fetch trusted issuer");

    ww::value::Object trusted_issuer;
    ERROR_IF_NOT(trusted_issuer.deserialize(trusted_issuer_str.c_str()),
                 "unexpected error, failed to deserialize trusted issuer");
    ERROR_IF_NOT(vc.deserialize(trusted_issuer),
                 "unexpected error, failed to deserialize verifying context");

    return true;
}
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
    if (! ww::identity::identity::initialize_contract(env))
        return false;

    return true;
}

// -----------------------------------------------------------------
// METHOD: register_trusted_issuer
//   Register the public key and chain code of a trusted issuer, note
//   that for the moment this is implemented with the assumption that
//   the invoker (the owner of the contract) is the only one who can
//   register trusted issuers.  This could be expanded to allow for
//   formal registration of endpoints including proof that a specific
//   contract object exists.
//
//   Any duplicate registration for a given ID will, for the moment,
//   fail. This is a simple policy that may be changed by others using
//   this approach.
//
// JSON PARAMETERS:
//   POLICY_AGENT_REGISTER_ISSUER_PARAM_SCHEMA
//
// RETURNS:
//   true if the registration succeeds
// -----------------------------------------------------------------
bool ww::identity::policy_agent::register_trusted_issuer(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string issuer_identity(msg.get_string("issuer_identity"));
    const std::string public_key_str(msg.get_string("public_key"));
    const std::string chain_code_str(msg.get_string("chain_code"));

    // Get and validate the path parameter. This is the path TO the
    // key relative to the contract object, any verification key from
    // this issuer must be prefixed by this key path; note that this
    // is not the same as the context_path field in Context objects
    // which describes the path to the key FROM the context.
    std::vector<std::string> prefix_path;
    ASSERT_SUCCESS(rsp, ww::identity::identity::get_context_path(msg, prefix_path),
                   "invalid request, ill-formed context path");

    // ---------- create the verifying context ----------
    ww::identity::VerifyingContext verifier;
    ASSERT_SUCCESS(rsp, verifier.initialize(prefix_path, public_key_str, chain_code_str),
                   "invalid request, invalid issuer public key/chain code");
    ASSERT_SUCCESS(rsp, save_trusted_issuer(issuer_identity, verifier),
                   "unexpected error, failed to save issuer information");

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: issue_policy_credential
//   Verify the incoming credential, process the policy decision and emit a new credential
//
// JSON PARAMETERS:
//   POLICY_AGENT_ISSUE_POLICY_CREDENTIAL_PARAM_SCHEMA
// RETURNS:
//   true signature is verified
// -----------------------------------------------------------------
bool ww::identity::policy_agent::issue_policy_credential(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(POLICY_AGENT_ISSUE_POLICY_CREDENTIAL_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // Get the credential parameter
    ww::value::Object credential;
    ASSERT_SUCCESS(rsp, msg.get_value("credential", credential),
                   "missing required parameter; credential");

    ww::identity::VerifiableCredential vc;
    ASSERT_SUCCESS(rsp, vc.deserialize(credential),
                   "invalid request, ill-formed credential");

    // Verify the credential signature

    // The signature was computed over the base64 encoded credential so we
    // do not need to decode the credential before checking the signature
    const std::string serialized_credential(vc.get_serialized_credential());
    ww::types::ByteArray message(serialized_credential.begin(), serialized_credential.end());

    ww::types::ByteArray signature;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(vc.proof_.proofValue_, signature),
                   "invalid request, ill-formed signature");

    ww::identity::VerifyingContext verifier;
    ASSERT_SUCCESS(rsp, fetch_trusted_issuer(vc.proof_.verificationMethod_.id_, verifier),
                         "invalid request, unknown issuer");
    ASSERT_SUCCESS(rsp, verifier.extend_context_path(vc.proof_.verificationMethod_.context_path_),
                                "invalid request, ill-formed context path");

    ASSERT_SUCCESS(rsp, verifier.verify_signature(message, signature),
                         "invalid request, signature verification failed");

    // And build the veriable credential; just wanted to note that it would be
    // completely appropriate to make a constructor for VC's that took the
    // information for build; however, there are no exceptions with our current
    // WASM interpreter so failure in the constructor would be a catastrophic
    // failure for the contract
    // ww::identity::VerifiableCredential vc;
    // ASSERT_SUCCESS(rsp, vc.build(credential, identity, extended_key_seed),
    //                "invalid request, ill-formed credential");

    // ---------- RETURN ----------
    // Finally pull the serialized verifiable credential and send it back
    ww::value::Object serialized_vc;
    ASSERT_SUCCESS(rsp, vc.serialize(serialized_vc),
                   "unexpected error, failed to serialized the credential");

    return rsp.value(serialized_vc, false);
}
