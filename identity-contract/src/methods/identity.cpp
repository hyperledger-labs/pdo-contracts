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
#include "identity/common/SigningContext.h"
#include "identity/common/SigningContextManager.h"

static KeyValueStore identity_metadata_store("key_store");
static KeyValueStore signing_context_store("signing_context");

static const std::string md_extended_key_seed("extend_key_seed");
static const std::string md_description("description");

// -----------------------------------------------------------------
// FUNCTION: get_context_path
//   create a context path from a message parameter
// RETURNS:
//   true if path successfully created
// -----------------------------------------------------------------
bool ww::identity::identity::get_context_path(const Message& msg, std::vector<std::string>& context_path)
{
    ww::value::Array context_path_array;
    if (! msg.get_value("context_path", context_path_array))
        return false;

    // context path must have at least one element
    if (context_path_array.get_count() < 1)
        return false;

    context_path.resize(0);
    for (size_t i = 0; i < context_path_array.get_count(); i++)
    {
        const std::string s(context_path_array.get_string(i));
        context_path.push_back(s);
    }

    return true;
}

// -----------------------------------------------------------------
// FUNCTION: validate_context_path
// -----------------------------------------------------------------
bool ww::identity::identity::validate_context_path(std::vector<std::string>& context_path)
{
    // Attempt to find the context, this will tell us whether
    // the path is valid... that is, it meets the extensibility
    // criteria for all registered contexts
    ww::identity::SigningContextManager manager(signing_context_store);
    ww::identity::SigningContext context;
    std::vector<std::string> extended_path;

    return manager.find_context(context_path, extended_path, context);
}

// -----------------------------------------------------------------
// FUNCTION: get_extended_key_seed
// -----------------------------------------------------------------
bool ww::identity::identity::get_extended_key_seed(ww::types::ByteArray& extended_key_seed)
{
    return identity_metadata_store.get(md_extended_key_seed, extended_key_seed);
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
bool ww::identity::identity::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    // ---------- create the extended key seed ----------
    ww::types::ByteArray extended_key_seed(EXTENDED_KEY_SIZE);
    if (! ww::crypto::random_identifier(extended_key_seed))
        return false;

    if (! identity_metadata_store.set(md_extended_key_seed, extended_key_seed))
        return false;

    // ---------- prime signing context store ----------
    ww::identity::SigningContextManager manager(signing_context_store);
    if (! manager.initialize())
        return false;

    // ---------- prime the credential store ----------

    // ---------- other metadata ----------
    if (! identity_metadata_store.set(md_description, "identity object"))
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
bool ww::identity::identity::initialize(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string description(msg.get_string("description"));
    ASSERT_SUCCESS(rsp, identity_metadata_store.set(md_description, description),
                   "unexpected error, failed to save description");

    // Mark as initialized
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "initialization failed");

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD:
//   register_signing_context
//
//   Register a signing context. If the context already exists, it will be overridden
//   with the new context.
// JSON PARAMETERS:
//   IDENTITY_REGISTER_SIGNING_CONTEXT_PARAM_SCHEMA
// RETURNS:
//   boolean
// -----------------------------------------------------------------
bool ww::identity::identity::register_signing_context(
    const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_REGISTER_SIGNING_CONTEXT_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    std::vector<std::string> context_path;
    ASSERT_SUCCESS(rsp, get_context_path(msg, context_path),
                   "invalid request, ill-formed context path");

    const std::string description(msg.get_string("description"));
    const bool extensible(msg.get_boolean("extensible"));

    ww::identity::SigningContextManager manager(signing_context_store);
    ww::identity::SigningContext context(extensible, description);
    ASSERT_SUCCESS(rsp, manager.add_context(context_path, context),
                   "failed to register the new context");

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD:
//   describe_signing_context
//
// JSON PARAMETERS:
//   IDENTITY_DESCRIBE_SIGNING_CONTEXT_PARAM_SCHEMA
// RETURNS:
//   IDENTITY_DESCRIBE_SIGNING_CONTEXT_RESULT_SCHEMA
// -----------------------------------------------------------------
bool ww::identity::identity::describe_signing_context(
    const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_DESCRIBE_SIGNING_CONTEXT_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    std::vector<std::string> context_path;
    ASSERT_SUCCESS(rsp, get_context_path(msg, context_path),
                   "invalid request, ill-formed context path");

    ww::identity::SigningContextManager manager(signing_context_store);
    ww::identity::SigningContext context;
    std::vector<std::string> extended_path;

    ASSERT_SUCCESS(rsp, manager.find_context(context_path, extended_path, context),
                   "invalid request, unable to locate context");
    ASSERT_SUCCESS(rsp, extended_path.size() == 0,
                   "invalid request, extensible paths not allowed");

    // ---------- RETURN ----------
    ww::value::Value v;
    ASSERT_SUCCESS(rsp, context.serialize(v),
                   "unexpected error, failed to serialize signing context");

    return rsp.value(v, false);
}

// -----------------------------------------------------------------
// METHOD:
//   sign
//
// JSON PARAMETERS:
//   IDENTITY_SIGN_PARAM_SCHEMA
// RETURNS:
//   IDENTITY_SIGN_RESULT_SCHEMA
// -----------------------------------------------------------------
bool ww::identity::identity::sign(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_SIGN_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    std::vector<std::string> context_path;
    ASSERT_SUCCESS(rsp, get_context_path(msg, context_path),
                   "invalid request, ill-formed context path");
    ASSERT_SUCCESS(rsp, validate_context_path(context_path),
                   "invalid request, ill-formed context path");

    ww::types::ByteArray extended_key_seed;
    ASSERT_SUCCESS(rsp, get_extended_key_seed(extended_key_seed),
                   "unexpected error, failed to retrieve extended key seed");

    const std::string b64_message(msg.get_string("message"));
    ww::types::ByteArray message;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(b64_message, message),
                   "invalid request, failed to decode message");

    ww::types::ByteArray signature;
    ASSERT_SUCCESS(rsp, ww::identity::SigningContext::sign_message(extended_key_seed, context_path, message, signature),
                   "unexpected error, signature failed");

    std::string b64_signature;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(signature, b64_signature),
                   "unexpected error: failed to encode signature");

        // ---------- RETURN ----------
    ww::value::String s(b64_signature.c_str());
    return rsp.value(s, false);
}

// -----------------------------------------------------------------
// METHOD:
//   verify
//
// JSON PARAMETERS:
//   IDENTITY_VERIFY_PARAM_SCHEMA
// RETURNS:
//
// -----------------------------------------------------------------
bool ww::identity::identity::verify(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_VERIFY_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    std::vector<std::string> context_path;
    ASSERT_SUCCESS(rsp, get_context_path(msg, context_path),
                   "invalid request, ill-formed context path");
    ASSERT_SUCCESS(rsp, validate_context_path(context_path),
                   "invalid request, ill-formed context path");

    ww::types::ByteArray extended_key_seed;
    ASSERT_SUCCESS(rsp, get_extended_key_seed(extended_key_seed),
                   "unexpected error, failed to retrieve extended key seed");

    const std::string b64_message(msg.get_string("message"));
    ww::types::ByteArray message;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(b64_message, message),
                   "invalid request, failed to decode message");

    const std::string b64_signature(msg.get_string("signature"));
    ww::types::ByteArray signature;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(b64_signature, signature),
                   "invalid request, failed to decode signature");

    bool success = ww::identity::SigningContext::verify_signature(
        extended_key_seed, context_path, message, signature);

    // ---------- RETURN ----------
    ww::value::Boolean b(success);
    return rsp.value(b, false);
}

// -----------------------------------------------------------------
// METHOD:
//   get_verifying_key
//
//   Note that this method will override the get_verifying_key method
//   from the common library. That method returned the verifying key
//   for the contract. This is a more semantically rich variant. The
//   contract verifying key should still be available from the ledger.
//
// JSON PARAMETERS:
//   IDENTITY_GET_VERIFYING_KEY_PARAM_SCHEMA
// RETURNS:
//   PEM encoded public key
// -----------------------------------------------------------------
bool ww::identity::identity::get_verifying_key(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(IDENTITY_GET_VERIFYING_KEY_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // Get the context path parameter
    std::vector<std::string> context_path;
    ASSERT_SUCCESS(rsp, get_context_path(msg, context_path),
                   "invalid request, ill-formed context path");
    ASSERT_SUCCESS(rsp, validate_context_path(context_path),
                   "invalid request, ill-formed context path");

    // Get the keys associated with the context path
    ww::types::ByteArray root_key;
    ASSERT_SUCCESS(rsp, get_extended_key_seed(root_key),
                   "unexpected error, failed to retrieve extended key seed");

    std::string private_key, public_key;
    ASSERT_SUCCESS(rsp, ww::identity::SigningContext::generate_keys(root_key, context_path, private_key, public_key),
                   "unexpected error, failed to generate public key");

    // ---------- RETURN ----------
    ww::value::String result(public_key.c_str());
    return rsp.value(result, false);
}
