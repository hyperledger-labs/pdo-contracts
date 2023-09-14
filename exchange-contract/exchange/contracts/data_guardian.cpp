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
#include "contract/attestation.h"
#include "exchange/issuer_authority_base.h"
#include "exchange/data_guardian.h"
#include "exchange/token_issuer.h"
#include "exchange/token_object.h"

static KeyValueStore guardian_store("guardian_store");
const std::string cap_encrypt_key("capability_encrypt_key");
const std::string cap_decrypt_key("capability_decrypt_key");

static KeyValueStore identity_store("identity_store");

// -----------------------------------------------------------------
// METHOD: initialize_contract
// -----------------------------------------------------------------
bool ww::exchange::data_guardian::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    // ---------- initialize the attestation contract ----------
    if (! ww::contract::attestation::initialize_contract(env))
        return false;

    // Generate the capability management key pair
    std::string decrypt_key;
    std::string encrypt_key;

    if (! ww::crypto::rsa::generate_keys(decrypt_key, encrypt_key))
        return false;
    if (! guardian_store.set(cap_encrypt_key, encrypt_key))
        return false;
    if (!guardian_store.set(cap_decrypt_key, decrypt_key))
        return false;

    return true;
}

// -----------------------------------------------------------------
// initialize
// -----------------------------------------------------------------
bool ww::exchange::data_guardian::initialize(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(DG_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // save the ledger key
    const std::string ledger_verifying_key(msg.get_string("ledger_verifying_key"));
    ASSERT_SUCCESS(rsp, ww::contract::attestation::set_ledger_key(ledger_verifying_key),
                   "failed to save the ledger verifying key");

    // save the code hash (decode it first)
    const std::string encoded_code_hash(msg.get_string("token_issuer_code_hash"));
    ww::types::ByteArray code_hash;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(encoded_code_hash, code_hash),
                   "failed to decode the parameter");
    ASSERT_SUCCESS(rsp, ww::contract::attestation::set_code_hash(code_hash),
                   "failed to save the code hash");

    // we are fully initialized
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "unexpected error: failed to initialize");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// provision_token_issuer
// -----------------------------------------------------------------
bool ww::exchange::data_guardian::provision_token_issuer(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(DG_PROVISION_TOKEN_ISSUER_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // check to see if the contract has been registered as a valid endpoint
    const std::string contract_id(msg.get_string("contract_id"));

    std::string verifying_key;
    std::string encryption_key;
    ASSERT_SUCCESS(rsp, ww::contract::attestation::get_endpoint(contract_id, verifying_key, encryption_key),
                   "failed to fetch information about the contract");

    // construct the initialization package
    std::string management_encryption_key;
    ASSERT_SUCCESS(rsp, guardian_store.get(cap_encrypt_key, management_encryption_key),
                   "unexpected error: failed to fetch management key");

    ww::value::Structure provisioning_secret(TIO_INITIALIZATION_PACKAGE_SCHEMA);
    ASSERT_SUCCESS(rsp, provisioning_secret.set_string("capability_management_key", management_encryption_key.c_str()),
                   "unexpected error: failed to set field");

    std::string serialized_provisioning_secret;
    ASSERT_SUCCESS(rsp, provisioning_secret.serialize(serialized_provisioning_secret),
                   "unexpected error: failed to serialize secret");

    ww::value::Structure provisioning_package(CONTRACT_SECRET_SCHEMA);
    ASSERT_SUCCESS(rsp, ww::secret::send_secret(encryption_key, serialized_provisioning_secret, provisioning_package),
                   "unexpected error: failed to encrypt secret");

    return rsp.value(provisioning_package, false);
}

// -----------------------------------------------------------------
// provision_token_object
// -----------------------------------------------------------------
bool ww::exchange::data_guardian::provision_token_object(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(DG_PROVISION_TOKEN_OBJECT_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // Unpack the provisioning package
    std::string management_decryption_key;
    ASSERT_SUCCESS(rsp, guardian_store.get(cap_decrypt_key, management_decryption_key),
                   "unexpected error: failed to fetch management key");

    std::string serialized_secret;
    ASSERT_SUCCESS(rsp, ww::secret::recv_secret(management_decryption_key, msg, serialized_secret),
                   "failed to decrypt secret");

    ww::value::Object provisioning_package;
    ASSERT_SUCCESS(rsp, provisioning_package.deserialize(serialized_secret.c_str()),
                   "unexpected error: failed to process initialization package");
    ASSERT_SUCCESS(rsp, provisioning_package.validate_schema(TIO_PROVISION_MINTED_TOKEN_SECRET_SCHEMA),
                   "failed to process initialization package");

    // pull the information out of the provisioning package
    const std::string minted_identity(provisioning_package.get_string("minted_identity"));
    const std::string token_description(provisioning_package.get_string("token_description"));
    const std::string to_encryption_key(provisioning_package.get_string("token_object_encryption_key"));
    const std::string to_verifying_key(provisioning_package.get_string("token_object_verifying_key"));

    ww::value::Object token_metadata;
    ASSERT_SUCCESS(rsp, provisioning_package.get_value("token_metadata", token_metadata),
                   "unexpected error: failed to fetch token_metadata");

    ww::value::Object capability_key_pair;
    std::string decrypt_key;
    std::string encrypt_key;
    std::string serialized_keys;

    if (! identity_store.get(minted_identity, serialized_keys))
    {
        // we need to create a new capability generation key pair
        ASSERT_SUCCESS(rsp, ww::crypto::rsa::generate_keys(decrypt_key, encrypt_key),
                       "unexpected error: failed to generate keys");
        ASSERT_SUCCESS(rsp, capability_key_pair.set_string("encryption_key", encrypt_key.c_str()),
                       "unexpected error: failed to store keys");
        ASSERT_SUCCESS(rsp, capability_key_pair.set_string("decryption_key", decrypt_key.c_str()),
                       "unexpected error: failed to store keys");
        ASSERT_SUCCESS(rsp, capability_key_pair.serialize(serialized_keys),
                       "unexpected error: failed to serialize keys");
        ASSERT_SUCCESS(rsp, identity_store.set(minted_identity, serialized_keys),
                       "unexpected error: failed to save key");
    }
    else
    {
        ASSERT_SUCCESS(rsp, capability_key_pair.deserialize(serialized_keys.c_str()),
                       "unexpected error: failed to deserialize keys");
        encrypt_key = capability_key_pair.get_string("encryption_key");
        decrypt_key = capability_key_pair.get_string("decryption_key");
    }

    // create the token object initialization package
    ww::value::Structure to_initialization_package(TO_INITIALIZATION_PACKAGE_SCHEMA);
    ASSERT_SUCCESS(rsp, to_initialization_package.set_string("token_description", token_description.c_str()),
                   "unexpected error: failed to create secret");
    ASSERT_SUCCESS(rsp, to_initialization_package.set_value("token_metadata", token_metadata),
                   "unexpected error: failed to get token metadata");
    ASSERT_SUCCESS(rsp, to_initialization_package.set_string("minted_identity", minted_identity.c_str()),
                   "unexpected error: failed to create secret");
    ASSERT_SUCCESS(rsp, to_initialization_package.set_string("capability_generation_key", encrypt_key.c_str()),
                   "unexpected error: failed to create secret");

    std::string serialized_initialization_package;
    ASSERT_SUCCESS(rsp, to_initialization_package.serialize(serialized_initialization_package),
                   "unexpected error: failed to serialize secret");

    ww::value::Structure result(CONTRACT_SECRET_SCHEMA);
    ASSERT_SUCCESS(rsp, ww::secret::send_secret(to_encryption_key, serialized_initialization_package, result),
                   "unexpected error: failed to encrypt secret");

    return rsp.value(result, true);
}

// -----------------------------------------------------------------
// UTILITY FUNCTIONS
// -----------------------------------------------------------------

// -----------------------------------------------------------------
// get_capability_keys
//
// get the encryption and decryption keys for processing capabilities
// associated with the minted identity
// -----------------------------------------------------------------
bool ww::exchange::data_guardian::get_capability_keys(
    const std::string& minted_identity,
    std::string& encrypt_key,
    std::string& decrypt_key)
{
    std::string serialized_keys;
    if (! identity_store.get(minted_identity, serialized_keys))
    {
        CONTRACT_SAFE_LOG(3, "not a valid capability: unknown identity");
        return false;
    }

    ww::value::Object capability_key_pair;
    if (! capability_key_pair.deserialize(serialized_keys.c_str()))
    {
        CONTRACT_SAFE_LOG(3, "unexpected error: failed to deserialize keys");
        return false;
    }

    decrypt_key.assign(capability_key_pair.get_string("decryption_key"));
    encrypt_key.assign(capability_key_pair.get_string("encryption_key"));
    return true;
}

// -----------------------------------------------------------------
// parse_capability
//
// find the
// -----------------------------------------------------------------
bool ww::exchange::data_guardian::parse_capability(
    const std::string& minted_identity,
    const ww::value::Object& operation_secret,
    ww::value::Object& operation)
{
    // get the keys for processing the capability
    std::string encrypt_key;
    std::string decrypt_key;
    if (! ww::exchange::data_guardian::get_capability_keys(minted_identity, encrypt_key, decrypt_key))
        return false;

    // decrypt the operation secret
    std::string decrypted_operation;
    if (! ww::secret::recv_secret(decrypt_key, operation_secret, decrypted_operation))
    {
        CONTRACT_SAFE_LOG(3, "not a valid capability: decryption failed");
        return false;
    }

    if (! operation.deserialize(decrypted_operation.c_str()))
    {
        CONTRACT_SAFE_LOG(3, "not a valid capability: invalid operation format");
        return false;
    }

    if (! operation.validate_schema(TO_OPERATION_SCHEMA))
    {
        CONTRACT_SAFE_LOG(3, "not a valid capability: invalid operation format");
        return false;
    }

    return true;
}
