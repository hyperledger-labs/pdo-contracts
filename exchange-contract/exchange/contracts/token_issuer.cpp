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

#include "contract/attestation.h"
#include "contract/base.h"
#include "exchange/issuer_authority_base.h"
#include "exchange/token_issuer.h"

static KeyValueStore token_issuer_store("token_issuer");
const std::string token_description_key("token_description");
const std::string token_metadata_key("token_metadata");
const std::string maximum_token_count_key("maximum_token_count");
const std::string current_token_count_key("current_token_count");
const std::string token_object_code_hash_key("token_object_code_hash");
const std::string capability_management_key("capability_management_key");

// maps contract_id --> token identifier
static KeyValueStore minted_identity_store("minted_identities");

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
bool ww::exchange::token_issuer::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    // ---------- initialize the attestation contract ----------
    if (! ww::contract::attestation::initialize_contract(env))
        return false;

    return true;
}

// -----------------------------------------------------------------
// initialize
//
// Initializing the token issuer object requires several pieces of
// information:
// * a description of the token and corresponding token object
// * limits on minting token objects
// * the identity of the ledger that provides the root of trust
// * the guardian initialization package
// * the issuer authority chain provided by the common vetting org
//
// The process for initialization is:
// 1) create the TIO
// 2) invoke the TIO operations to fetch contract metadata (get_contract_metadata, get_contract_code_metadata)
// 3) request the TIO contract information from the ledger
// 4) submit the metadata and ledger information to the guardian for verification
// 5) retrieve the
// -----------------------------------------------------------------
bool ww::exchange::token_issuer::initialize(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(TIO_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // initialize the derived authority from the vetting organization
    if (! ww::exchange::issuer_authority_base::initialize_derived_authority(msg, env, rsp))
        return false;

    // save the ledger key
    const std::string ledger_verifying_key(msg.get_string("ledger_verifying_key"));
    ASSERT_SUCCESS(rsp, ww::contract::attestation::set_ledger_key(ledger_verifying_key),
                   "failed to save the ledger verifying key");

    // save the code hash (decode it first)
    const std::string encoded_code_hash(msg.get_string("token_object_code_hash"));
    ww::types::ByteArray code_hash;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(encoded_code_hash, code_hash),
                   "failed to decode the parameter");
    ASSERT_SUCCESS(rsp, ww::contract::attestation::set_code_hash(code_hash),
                   "failed to save the code hash");

    // save the configuration
    ASSERT_SUCCESS(rsp, token_issuer_store.set(token_description_key, msg.get_string("token_description")),
                   "unexpected error: failed to save configuration");
    ww::value::Object token_metadata;
    ASSERT_SUCCESS(rsp, msg.get_value("token_metadata", token_metadata),
                   "unexpected error: failed to get token_metadata parameters");
    const std::string serialized_token_metadata(token_metadata.serialize());
    ASSERT_SUCCESS(rsp, token_issuer_store.set(token_metadata_key, serialized_token_metadata),
                   "unexpected error: failed to save configuration");
    ASSERT_SUCCESS(rsp, token_issuer_store.set(maximum_token_count_key, msg.get_number("maximum_token_count")),
                   "unexpected error: failed to save configuration");
    ASSERT_SUCCESS(rsp, token_issuer_store.set(current_token_count_key, msg.get_number("maximum_token_count")),
                   "unexpected error: failed to save configuration");

    // process the guardian initialization package
    ww::value::Object initialization_package;
    ASSERT_SUCCESS(rsp, msg.get_value("initialization_package",initialization_package),
                   "unexpected error: failed to get parameter");

    std::string decryption_key;
    ASSERT_SUCCESS(rsp, KeyValueStore::privileged_get("ContractKeys.Decryption", decryption_key),
                   "failed to retreive privileged value for ContractKeys.Deccryption");

    std::string decrypted_secret;
    ASSERT_SUCCESS(rsp, ww::secret::recv_secret(decryption_key, initialization_package, decrypted_secret),
                   "failed to process initialization package");

    ww::value::Object secret;
    ASSERT_SUCCESS(rsp, secret.deserialize(decrypted_secret.c_str()),
                   "failed to process initialization package");
    ASSERT_SUCCESS(rsp, secret.validate_schema(TIO_INITIALIZATION_PACKAGE_SCHEMA),
                   "failed to process initialization package");

    const std::string management_key(secret.get_string("capability_management_key"));
    ASSERT_SUCCESS(rsp, token_issuer_store.set(capability_management_key, management_key),
                   "unexpected error: failed to save capability management key");

    // we are fully initialized
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "unexpected error: failed to initialize");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// mint_token_object
//
// Take a token object that has been verified through the add_endpoint
// method and mint a token for it if there are tokens left to mint. We
// can only provision up to the number of token objects specified in
// the initialization parameter. Minting involves creating a random
// token identifier that will be (later) registered with the guardian.
// -----------------------------------------------------------------
bool ww::exchange::token_issuer::mint_token_object(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(TIO_MINT_TOKEN_OBJECT_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // check to see if the contract has been registered
    const std::string contract_id(msg.get_string("contract_id"));
    std::string verifying_key;
    std::string encryption_key;
    ASSERT_SUCCESS(rsp, ww::contract::attestation::get_endpoint(contract_id, verifying_key, encryption_key),
                   "failed to fetch information about the contract");

    // check to see if we have previously minted a token for the contract
    std::string minted_identity;
    ASSERT_SUCCESS(rsp, ! minted_identity_store.get(contract_id, minted_identity),
                   "a token was already minted for the contract");

    // mark this as an approved issuer
    ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::add_approved_issuer(verifying_key),
                   "unexpected error: failed to set issuer");

    // mint the token
    ww::types::ByteArray minted_identity_raw;
    ASSERT_SUCCESS(rsp, ww::crypto::random_identifier(minted_identity_raw),
                   "unexpected error: failed to create identifier");
    ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(minted_identity_raw, minted_identity),
                   "unexpected error: failed to encode identifier");
    ASSERT_SUCCESS(rsp, minted_identity_store.set(contract_id, minted_identity),
                   "unexpected error: failed to store identifier");

    // update the token count
    uint32_t token_count;
    ASSERT_SUCCESS(rsp, token_issuer_store.get(current_token_count_key, token_count),
                   "unexpected error: failed to fetch current token count");
    ASSERT_SUCCESS(rsp, token_count > 0, "no more tokens to issue");
    token_count = token_count - 1;
    ASSERT_SUCCESS(rsp, token_issuer_store.set(current_token_count_key, token_count),
                   "unexpected error: failed to save token count");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// provision_minted_token_object
//
// Create the provisioning package for a token object that has been
// registered and minted. The current state of the TIO must be
// committed in the ledger before we will allow the operation to
// be performed.
// -----------------------------------------------------------------
bool ww::exchange::token_issuer::provision_minted_token_object(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(TIO_PROVISION_MINTED_TOKEN_OBJECT_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // current state of the token issuer object must be committed in the ledger
    std::string ledger_key;
    if (! ww::contract::attestation::get_ledger_key(ledger_key) && ledger_key.length() > 0)
        return rsp.error("contract has not been initialized");

    const std::string ledger_signature(msg.get_string("ledger_signature"));

    ww::types::ByteArray buffer;
    std::copy(env.contract_id_.begin(), env.contract_id_.end(), std::back_inserter(buffer));
    std::copy(env.state_hash_.begin(), env.state_hash_.end(), std::back_inserter(buffer));

    ww::types::ByteArray signature;
    if (! ww::crypto::b64_decode(ledger_signature, signature))
        return rsp.error("failed to decode ledger signature");
    if (! ww::crypto::ecdsa::verify_signature(buffer, ledger_key, signature))
        return rsp.error("failed to verify ledger signature");

    // the current state has been committed so now make sure the contract object is valid
    const std::string contract_id(msg.get_string("contract_id"));
    std::string verifying_key;
    std::string encryption_key;
    ASSERT_SUCCESS(rsp, ww::contract::attestation::get_endpoint(contract_id, verifying_key, encryption_key),
                   "failed to fetch information about the contract");

    // and make sure that there is a token minted for the contract
    std::string minted_identity;
    ASSERT_SUCCESS(rsp, minted_identity_store.get(contract_id, minted_identity),
                   "token not yet minted");

    // create the secret & encrypt it with the guardian's management key
    ww::value::Structure secret(TIO_PROVISION_MINTED_TOKEN_SECRET_SCHEMA);
    ASSERT_SUCCESS(rsp, secret.set_string("minted_identity", minted_identity.c_str()),
                   "unexpected error: failed to update object");
    ASSERT_SUCCESS(rsp, secret.set_string("token_object_encryption_key", encryption_key.c_str()),
                   "unexpected error: failed to update object");
    ASSERT_SUCCESS(rsp, secret.set_string("token_object_verifying_key", verifying_key.c_str()),
                   "unexpected error: failed to update object");

    std::string token_description;
    ASSERT_SUCCESS(rsp, token_issuer_store.get(token_description_key, token_description),
                   "unexpected error: failed to get token description");
    ASSERT_SUCCESS(rsp, secret.set_string("token_description", token_description.c_str()),
                   "unexpected error: failed to update object");

    std::string token_metadata;
    ASSERT_SUCCESS(rsp, token_issuer_store.get(token_metadata_key, token_metadata),
                   "unexpected error: failed to get token metadata");
    ww::value::Object deserialized_token_metadata;
    ASSERT_SUCCESS(rsp, deserialized_token_metadata.deserialize(token_metadata.c_str()),
                   "unexpected error: failed to deserialized token metadata");
    ASSERT_SUCCESS(rsp, secret.set_value("token_metadata", deserialized_token_metadata),
                   "unexpected error: failed to update object");

    std::string serialized_secret;
    ASSERT_SUCCESS(rsp, secret.serialize(serialized_secret),
                   "unexpected error: failed to serialize object");

    std::string management_key;
    ASSERT_SUCCESS(rsp, token_issuer_store.get(capability_management_key, management_key),
                   "unexpected error: failed to get capability management key");

    ww::value::Structure result(CONTRACT_SECRET_SCHEMA);
    ASSERT_SUCCESS(rsp, ww::secret::send_secret(management_key, serialized_secret, result),
                   "unexpected error: failed to encrypt secret");

    return rsp.value(result, false);
}
