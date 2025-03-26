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
#include "identity/signature_authority.h"
#include "identity/common/Credential.h"
#include "identity/common/SigningContext.h"
#include "identity/common/SigningContextManager.h"

// -----------------------------------------------------------------
// METHOD: sign_credential
//   Sign a credential generating the appropriate proof data
//
// JSON PARAMETERS:
//   SIGNATURE_AUTHORITY_SIGN_CREDENTIAL_PARAM_SCHEMA
// RETURNS:
//   VERIFIABLE_CREDENTIAL_SCHEMA
// -----------------------------------------------------------------
bool ww::identity::signature_authority::sign_credential(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(SIGNATURE_AUTHORITY_SIGN_CREDENTIAL_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // Get and validate the context path parameter
    std::vector<std::string> context_path;
    ASSERT_SUCCESS(rsp, ww::identity::identity::get_context_path(msg, context_path),
                   "invalid request, ill-formed context path");

    // Get and validate the credential parameter
    ww::value::Object credential;
    ASSERT_SUCCESS(rsp, msg.get_value("credential", credential),
                   "missing required parameter; credential");

    // Pull together the information needed to build the vc
    const ww::identity::IdentityKey identity(env.contract_id_, context_path);
    const ww::identity::SigningContextManager manager = ww::identity::identity::get_context_manager();

    ww::identity::SigningContext context;
    std::vector<std::string> extended_path;

    ASSERT_SUCCESS(rsp, manager.find_context(context_path, extended_path, context),
                   "invalid request, unable to locate context");
    ASSERT_SUCCESS(rsp, context.is_extensible() || extended_path.size() == 0,
                   "invalid request, extensible paths not allowed");

    // The context that will be used to sign the message is found context
    // extended with the path from the message
    context.set_context_path(extended_path);

    // And build the veriable credential; just wanted to note that it would be
    // completely appropriate to make a constructor for VC's that took the
    // information for build; however, there are no exceptions with our current
    // WASM interpreter so failure in the constructor would be a catastrophic
    // failure for the contract
    ww::identity::VerifiableCredential vc;
    ASSERT_SUCCESS(rsp, vc.build(credential, identity, context),
                   "invalid request, ill-formed credential");

    // Finally pull the serialized verifiable credential and send it back
    ww::value::Object serialized_vc;
    ASSERT_SUCCESS(rsp, vc.serialize(serialized_vc),
                   "unexpected error, failed to serialized the credential");

    return rsp.value(serialized_vc, false);
}

// -----------------------------------------------------------------
// METHOD: verify_credential
//   Verify the signature on a credential
//
// JSON PARAMETERS:
//   SIGNATURE_AUTHORITY_VERIFY_CREDENTIAL_PARAM_SCHEMA
// RETURNS:
//   true signature is verified
// -----------------------------------------------------------------
bool ww::identity::signature_authority::verify_credential(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(SIGNATURE_AUTHORITY_VERIFY_CREDENTIAL_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // Get the credential parameter
    ww::value::Object credential;
    ASSERT_SUCCESS(rsp, msg.get_value("credential", credential),
                   "missing required parameter; credential");

    ww::identity::VerifiableCredential vc;
    ASSERT_SUCCESS(rsp, vc.deserialize(credential),
                   "invalid request, ill-formed credential");
    ASSERT_SUCCESS(rsp, vc.proof_.verificationMethod_.id_ == env.contract_id_,
                   "invalid request, wrong verifier");

    // Build the context needed to verify the credential
    const ww::identity::SigningContextManager manager = ww::identity::identity::get_context_manager();

    ww::identity::SigningContext context;
    std::vector<std::string> extended_path;

    ASSERT_SUCCESS(rsp, manager.find_context(vc.proof_.verificationMethod_.context_path_, extended_path, context),
                   "invalid request, unable to locate context");
    ASSERT_SUCCESS(rsp, context.is_extensible() || extended_path.size() == 0,
                   "invalid request, extensible paths not allowed");

    // The context that will be used to sign the message is found context
    // extended with the path from the message
    context.set_context_path(extended_path);

    bool verified = vc.check(context);

    // ---------- RETURN ----------
    ww::value::Boolean result(verified);
    return rsp.value(result, false);
}
