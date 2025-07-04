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

#include "exchange/common/AuthoritativeAsset.h"
#include "exchange/common/LedgerStore.h"

#include "contract/base.h"
#include "contract/attestation.h"
#include "exchange/issuer_authority_base.h"
#include "exchange/issuer.h"
#include "exchange/token_issuer.h"
#include "exchange/token_object.h"

static KeyValueStore token_object_store("token_object");
const std::string token_description_key("token_description");
const std::string token_metadata_key("token_metadata");
const std::string minted_identity_key("minted_identity");
const std::string capability_generation_key("capability_generation_key");

static ww::exchange::LedgerStore ledger_store("token_ledger");

// -----------------------------------------------------------------
// NAME: get_token_metadata
//
// Pulls the stored token metadata (which is a serialized JSON object),
// verifies the schema of the metadata, and returns it in the
// token_metadata parameter. The expectation is that this function
// will be called by token classes that specialize token behavior.
// -----------------------------------------------------------------
bool ww::exchange::token_object::get_token_metadata(
    const std::string& schema,
    ww::value::Object& token_metadata)
{
    std::string serialized_token_metadata;
    ERROR_IF_NOT(token_object_store.get(token_metadata_key, serialized_token_metadata),
                 "unexpected error: failed to get token metadata");

    ww::value::Object deserialized_token_metadata;
    ERROR_IF_NOT(deserialized_token_metadata.deserialize(serialized_token_metadata.c_str()),
                 "unexpected error: failed to deserialize token metadata");

    ERROR_IF_NOT(deserialized_token_metadata.validate_schema(schema.c_str()),
                 "unexpected error: token metadata does not match schema");

    token_metadata.set(deserialized_token_metadata);
    return true;
}

// -----------------------------------------------------------------
// get_token_identity
//
// Return the minted identity for this token object.
// -----------------------------------------------------------------
bool ww::exchange::token_object::get_token_identity(
    std::string& token_identity)
{
    ERROR_IF_NOT(token_object_store.get(minted_identity_key, token_identity),
                 "unexpected error: failed to get minted identity");
    return true;
}

// -----------------------------------------------------------------
// METHOD: initialize_contract
// -----------------------------------------------------------------
bool ww::exchange::token_object::initialize_contract(const Environment& env)
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
// -----------------------------------------------------------------
bool ww::exchange::token_object::initialize(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(TO_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // initialize the derived authority from the token issuer object, not
    // sure that this is necessary though I think it will make it easier
    // to expression escrow consistently with other exchange assets. This
    // object becomes an issuer of precisely one asset.
    if (! ww::exchange::issuer_authority_base::initialize_derived_authority(msg, env, rsp))
        return false;

    // save the ledger key, this is passed in as a parameter; later we need
    // to decide if there is an attack when the TIO has a different verification
    // key than the TO. I think its OK because the TIO checks the TO's attestation
    // against the ledger key (so they must be in the same ledger).
    const std::string ledger_verifying_key(msg.get_string("ledger_verifying_key"));
    ASSERT_SUCCESS(rsp, ww::contract::attestation::set_ledger_key(ledger_verifying_key),
                   "failed to save the ledger verifying key");

    // process the secret object that was generated by the guardian
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
    ASSERT_SUCCESS(rsp, secret.validate_schema(TO_INITIALIZATION_PACKAGE_SCHEMA),
                   "failed to process initialization package");

    ASSERT_SUCCESS(rsp, token_object_store.set(token_description_key, secret.get_string("token_description")),
                   "unexpected error: failed to save configuration");
    ww::value::Object token_metadata;
    ASSERT_SUCCESS(rsp, secret.get_value("token_metadata", token_metadata),
                   "unexpected error: failed to get token_metadata parameters");
    const std::string serialized_token_metadata(token_metadata.serialize());
    ASSERT_SUCCESS(rsp, token_object_store.set(token_metadata_key, serialized_token_metadata),
                   "unexpected error: failed to save configuration");
    ASSERT_SUCCESS(rsp, token_object_store.set(minted_identity_key, secret.get_string("minted_identity")),
                   "unexpected error: failed to save configuration");
    ASSERT_SUCCESS(rsp, token_object_store.set(capability_generation_key, secret.get_string("capability_generation_key")),
                   "unexpected error: failed to save configuration");

    // add the asset to the ledger store, this is really overkill but it makes it easier
    // to copy code from the issuer
    const std::string owner(env.creator_id_);
    std::string asset_type_identifier;
    ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                   "unexpected error: no asset type identifier");
    ASSERT_SUCCESS(rsp, ledger_store.add_entry(owner, asset_type_identifier, 1),
                   "unexpected error: failed ledger store");

    // we are fully initialized
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "unexpected error: failed to initialize");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: get_balance
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   current number of assets assigned to the requestor
// -----------------------------------------------------------------
bool ww::exchange::token_object::get_balance(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    int count = 0;
    std::string owner;

    ASSERT_SUCCESS(rsp, ww::contract::base::get_owner(owner), "failed to retrieve owner");
    if (env.originator_id_ == owner)
        count = 1;

    ww::value::Number balance(count);
    return rsp.value(balance, false);
}

// -----------------------------------------------------------------
// transfer
// -----------------------------------------------------------------
bool ww::exchange::token_object::transfer(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(TRANSFER_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string old_owner(env.originator_id_);
    const std::string new_owner(msg.get_string("new_owner_identity"));
    const int count = (int) msg.get_number("count");
    ASSERT_SUCCESS(rsp, count == 1, "invalid transfer request, invalid asset count");

    // For now this is the simple transfer of ownership, the previous
    // owner will not be able to create new capabilities but may be
    // able to evaluate existing capabilities, this will be fixed when
    // we complete the transfer protocol

    ASSERT_SUCCESS(rsp, ww::contract::base::set_owner(new_owner),
                   "unexpected error: failed to reassign ownership");

    // if there is no issuance for this identity, we treat it as a 0 balance
    ww::exchange::LedgerEntry old_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(old_owner, old_entry),
                   "unexpected error: failed to process ledgerstore");

    if (! ledger_store.exists(new_owner))
    {
        std::string asset_type_identifier;
        ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                       "unexpected error: no asset type identifier");
        ASSERT_SUCCESS(rsp, ledger_store.add_entry(new_owner, asset_type_identifier, 0),
                       "unexpected error: failed to add new owner");
    }

    ww::exchange::LedgerEntry new_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(new_owner, new_entry),
                   "unexpected error: failed to find new owner");

    // after all the set up, finally transfer the assets
    old_entry.asset_.count_ = 0;
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(old_owner, old_entry),
                   "unexpected error: failed to save ledger entry");

    new_entry.asset_.count_ = 1;
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(new_owner, new_entry),
                   "unexpected error: failed to save ledger entry");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// escrow
// -----------------------------------------------------------------
bool ww::exchange::token_object::escrow(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(ESCROW_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string escrow_agent(msg.get_string("escrow_agent_identity"));
    const int count = (int) msg.get_number("count");
    ASSERT_SUCCESS(rsp, count == 1, "invalid escrow request, invalid asset count");

    const std::string owner(env.originator_id_);

    // if there is no issuance for this identity, we treat it as a 0 balance
    ww::exchange::LedgerEntry entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(owner, entry), "escrow failed, insufficient assets");
    ASSERT_SUCCESS(rsp, ! entry.asset_is_escrowed(escrow_agent), "escrow failed, asset already escrowed");
    ASSERT_SUCCESS(rsp, entry.escrow(escrow_agent, count), "unexpected error, failed to escrow");

    // and save the modified ledger entry
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(owner, entry), "unexpected error, unable to update entry");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// escrow_attestation
// -----------------------------------------------------------------
bool ww::exchange::token_object::escrow_attestation(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(ESCROW_ATTESTATION_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string owner(env.originator_id_);
    const std::string escrow_agent(msg.get_string("escrow_agent_identity"));

    // get the verifying key
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error: failed to retrieve signing key");

    // get the signing key
    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "unexpected error: failed to retrieve signing key");

    // if there is no issuance for this identity, we treat it as a 0 balance
    ww::exchange::LedgerEntry entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(owner, entry),
                   "unpexpected error: failed to get ledger entry");

    ww::exchange::AuthoritativeAsset authoritative_asset;
    ASSERT_SUCCESS(rsp, entry.get_escrowed_asset(escrow_agent, authoritative_asset.asset_),
                   "invalid escrow attestation request, asset is not escrowed");
    ASSERT_SUCCESS(rsp, authoritative_asset.issuer_state_reference_.set_from_environment(env),
                   "unexpected error: failed to set state reference");
    ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_authority(authoritative_asset.issuer_authority_chain_),
                   "unexpected error: failed to retrieve issuer authority");
    authoritative_asset.issuer_identity_ = verifying_key;

    ASSERT_SUCCESS(rsp, authoritative_asset.sign(signing_key),
                   "unexpected error: failed to sign authoritative asset");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, authoritative_asset.serialize(result),
                   "unexpected error: failed to serialize authoritative asset");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// release
// -----------------------------------------------------------------
bool ww::exchange::token_object::release(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(RELEASE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string owner(env.originator_id_);

    ww::exchange::EscrowRelease release_request;
    ASSERT_SUCCESS(rsp, release_request.get_from_message(msg, "release_request"),
                   "invalid request, malformed parameter, release_request");

    // get the ledger entry and make sure it has actually been escrowed
    ww::exchange::LedgerEntry entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(owner, entry),
                   "invalid request, assets are not escrowed");

    ww::exchange::Asset escrowed_asset;
    ASSERT_SUCCESS(rsp, entry.get_escrowed_asset(release_request.escrow_agent_identity_, escrowed_asset),
                   "invalid request, asset is not escrowed");

    // verify the escrow agent signature
    ASSERT_SUCCESS(rsp, release_request.verify_signature(escrowed_asset),
                   "escrow signature verification failed");

    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    // for the moment, we only allow release of the fully escrowed asset, we need to add a
    // means to prevent replay of release requests before we allow partial releases
    // XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ASSERT_SUCCESS(rsp, release_request.count_ == escrowed_asset.count_,
                   "invalid request, count mismatch");

    ASSERT_SUCCESS(rsp, entry.release_escrow(release_request.escrow_agent_identity_),
                   "unexpected error: failed to update status");

    // update the entry
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(owner, entry),
                   "unexpected error: unable to update ledger entry");

    // add the dependency to the response
    ASSERT_SUCCESS(rsp, release_request.escrow_agent_state_reference_.add_to_response(rsp),
                   "unexpected error: unable to save state reference");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// claim
// -----------------------------------------------------------------
bool ww::exchange::token_object::claim(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(CLAIM_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string new_owner(env.originator_id_);

    ww::exchange::EscrowClaim claim_request;
    ASSERT_SUCCESS(rsp, claim_request.get_from_message(msg, "claim_request"),
                   "invalid request, malformed parameter, claim_request");

    // get the old owner's entry from the ledger
    ww::exchange::LedgerEntry old_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(claim_request.old_owner_identity_, old_entry),
                   "invalid claim request, no such asset");

    // get the escrowed asset information
    ww::exchange::Asset old_escrowed_asset;
    ASSERT_SUCCESS(rsp, old_entry.get_escrowed_asset(claim_request.escrow_agent_identity_, old_escrowed_asset),
                   "invalid claim request, not escrowed");

    // check the signature from the escrow agent
    ASSERT_SUCCESS(rsp, claim_request.verify_signature(old_escrowed_asset, new_owner),
                   "invalid claim request, signature verification failed");

    // update the old entry and save it back to the ledger
    ASSERT_SUCCESS(rsp, old_entry.transfer_escrow(claim_request.escrow_agent_identity_, claim_request.count_),
                   "unexpected error, failed to update ledger entry");

    ASSERT_SUCCESS(rsp, ledger_store.set_entry(claim_request.old_owner_identity_, old_entry),
                   "unexpected error, failed to update ledger entry");

    // get the new owner's entry from the ledger, create an empty
    // entry if one does not already exist
    if (! ledger_store.exists(new_owner))
    {
        const int count = 0;
        std::string asset_type_identifier;
        ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                       "unexpected error: no asset type identifier");
        ASSERT_SUCCESS(rsp, ledger_store.add_entry(new_owner, asset_type_identifier, (uint32_t)count),
                       "unexpected error: failed to add new owner");
    }

    ww::exchange::LedgerEntry new_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(new_owner, new_entry),
                   "unexpected error: failed to find new owner");

    new_entry.asset_.count_ = 1;
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(new_owner, new_entry),
                   "unexpected error: failed to save ledger entry");

    ASSERT_SUCCESS(rsp, ww::contract::base::set_owner(new_owner),
                   "unexpected error: failed to reassign ownership");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// UTILITY FUNCTIONS
// -----------------------------------------------------------------

// -----------------------------------------------------------------
// create_operation_package
// -----------------------------------------------------------------
bool ww::exchange::token_object::create_operation_package(
    const std::string& method_name,
    const ww::value::Object& parameters,
    ww::value::Object& capability_result)
{
    // No request identifier is specified so we'll generate a new one
    ww::types::ByteArray identifier_raw;
    if (! ww::crypto::random_identifier(identifier_raw))
        return false;

    std::string identifier;
    if (! ww::crypto::b64_encode(identifier_raw, identifier))
        return false;

    return create_operation_package(identifier, method_name, parameters, capability_result);
}

bool ww::exchange::token_object::create_operation_package(
    const std::string& request_identifier,
    const std::string& method_name,
    const ww::value::Object& parameters,
    ww::value::Object& capability_result)
{
    // Create the operation package, this will be the message in the
    // secret that we are going to create for the capability
    ww::value::Structure operation(TO_OPERATION_SCHEMA);

    ww::types::ByteArray nonce_raw;
    if (! ww::crypto::random_identifier(nonce_raw))
        return false;

    std::string nonce;
    if (! ww::crypto::b64_encode(nonce_raw, nonce))
        return false;

    if (! operation.set_string("nonce", nonce.c_str()))
        return false;

    if (! operation.set_string("request_identifier", request_identifier.c_str()))
            return false;

    if (! operation.set_string("method_name", method_name.c_str()))
        return false;

    if (! operation.set_value("parameters", parameters))
        return false;

    // From the operation create the secret that will be
    // used in the capability
    ww::value::Structure encrypted_secret(CONTRACT_SECRET_SCHEMA);

    std::string serialized_operation;
    if (! operation.serialize(serialized_operation))
        return false;

    std::string generation_key;
    if (! token_object_store.get(capability_generation_key, generation_key))
        return false;

    if (! ww::secret::send_secret(generation_key, serialized_operation, encrypted_secret))
        return false;

    // Create the capability
    ww::value::Structure capability(TO_CAPABILITY_SCHEMA);

    std::string minted_identity;
    if (! token_object_store.get(minted_identity_key, minted_identity))
        return false;
    if (! capability.set_string("minted_identity", minted_identity.c_str()))
        return false;

    if (! capability.set_value("operation", encrypted_secret))
        return false;

    // And save what we just created into the result parameter
    if (! capability_result.set(capability))
        return false;

    return true;
}
