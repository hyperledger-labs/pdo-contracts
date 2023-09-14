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

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "StateReference.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "exchange/issuer_authority_base.h"

#include "exchange/common/IssuerAuthority.h"
#include "exchange/common/IssuerAuthorityChain.h"

static KeyValueStore issuer_authority_common_store("issuer_authority_common_store");
static KeyValueStore issuer_authority_approved_keys("issuer_authority_approved_keys");

static const std::string md_asset_type_id_key("asset_type_identifier");
static const std::string md_authority_chain_key("authority_chain");

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// CONTRACT METHODS
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
// METHOD: initialize_root_authority
//   initialize key value store for a vetting organization that is
//   the root of trust; that is, there is no associated authority
//   object that needs to be added to the store.
//
// JSON PARAMETERS:
//   asset-type-id -- ecdsa public key for the asset type
//
// RETURNS:
//   true if asset type id successfully saved
// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::initialize_root_authority(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    if (! msg.validate_schema(INITIALIZE_ROOT_AUTHORITY_PARAM_SCHEMA))
        return rsp.error("invalid request, missing required parameters");

    // Build the root authority chain and save it in the metadata
    std::string verifying_key;
    if (! ww::contract::base::get_verifying_key(verifying_key))
        return rsp.error("corrupted state; verifying key not found");

    ww::value::String verifying_key_string(verifying_key.c_str());

    // Set the asset type
    const std::string asset_type_identifier(msg.get_string("asset_type_identifier"));
    if (asset_type_identifier.empty())
        return rsp.error("missing required parameter; asset_type_identifier");

    if (! issuer_authority_common_store.set(md_asset_type_id_key, asset_type_identifier))
        return rsp.error("failed to store the asset type id");

    // CONTINUE

    // Save the serialized authority object
    ww::exchange::IssuerAuthorityChain authority_chain(asset_type_identifier, verifying_key);

    std::string serialized_authority_chain;
    if (! authority_chain.serialize_string(serialized_authority_chain))
        return rsp.error("failed to save authority chain; serialization failed");

    if (! issuer_authority_common_store.set(md_authority_chain_key, serialized_authority_chain))
        return rsp.error("failed to save authority chain; failed to store data");

    // Mark as initialized
    ww::contract::base::mark_initialized();

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: initialize_derived_authority
//   initialize the key value store for an issuer that derives authority
//   from another object such as a vetting organization or another issuer
//
// JSON PARAMETERS:
//  asset_authority_chain -- the object that grants issuance
//    authority to this contract
//
// RETURNS:
//   true
// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::initialize_derived_authority(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    if (! msg.validate_schema(INITIALIZE_DERIVED_AUTHORITY_PARAM_SCHEMA))
        return rsp.error("invalid request, missing required parameters");

    ww::value::Object value;

    // Validate the authority given to the contract object
    ww::exchange::IssuerAuthorityChain authority_chain;
    ASSERT_SUCCESS(rsp, msg.get_value("asset_authority_chain", value),
                   "missing required parameter; asset_authority_chain");
    ASSERT_SUCCESS(rsp, authority_chain.deserialize(value),
                   "invalid parameter; asset_authority_chain");

    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "corrupted state; verifying key not found");
    ASSERT_SUCCESS(rsp, authority_chain.validate_issuer_key(verifying_key),
                   "invalid parameter; authority chain validation failed");

    // Save the serialized authority chain object
    std::string serialized_authority_chain;
    ASSERT_SUCCESS(rsp, authority_chain.serialize_string(serialized_authority_chain),
                   "failed to save authority chain; serialization failed");
    ASSERT_SUCCESS(rsp, issuer_authority_common_store.set(md_authority_chain_key, serialized_authority_chain),
                   "failed to save authority chain; failed to store data");

    // Save the asset type identifier
    ASSERT_SUCCESS(rsp, issuer_authority_common_store.set(md_asset_type_id_key, authority_chain.asset_type_identifier_),
                   "failed to store the asset type id");

    // Mark as initialized
    ww::contract::base::mark_initialized();

    // ---------- RETURN ----------

    // the authority given to the issuer is only valid if all of the
    // dependencies have been committed to the ledger
    ASSERT_SUCCESS(rsp, authority_chain.add_dependencies_to_response(rsp),
                   "failed to add dependencies to the response");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: get_asset_type_identifier
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   asset type id as a string
// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::get_asset_type_identifier(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    std::string asset_type_identifier;
    ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                   "contract state corrupted, no asset type identifier");

    ww::value::String v(asset_type_identifier.c_str());
    return rsp.value(v, false);
}

// -----------------------------------------------------------------
// METHOD: add_approved_issuer
//
// JSON PARAMETERS:
//   issuer-verifying-key -- verifying key of the asset issuer
//
// RETURNS:
//   true if key is successfully stored
// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::add_approved_issuer(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    // Save the issuer's key, would be good to make sure that this is a valid ECDSA key
    const std::string issuer_verifying_key(msg.get_string("issuer_verifying_key"));
    ASSERT_SUCCESS(rsp, add_approved_issuer(issuer_verifying_key),
                   "failed to save the issuer verifying key");

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: get_authority
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   serialized authority object for this contract
// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::get_authority(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ww::exchange::IssuerAuthorityChain authority_chain;
    ASSERT_SUCCESS(rsp, get_authority(authority_chain),
                   "failed to retrieve authority chain");

    ww::value::Value serialized;
    ASSERT_SUCCESS(rsp, authority_chain.serialize(serialized),
                   "failed to serialize authority chain");

    return rsp.value(serialized, false);
}

// -----------------------------------------------------------------
// METHOD: get_issuer_authority
//
// JSON PARAMETERS:
//   issuer-verifying-key -- verifying key of the asset issuer
//
// RETURNS:
//   serialized authority object
// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::get_issuer_authority(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    // Retrieve the issuer's key from the parameter list
    const std::string issuer_verifying_key(msg.get_string("issuer_verifying_key"));

    uint32_t flag;
    ASSERT_SUCCESS(rsp, issuer_authority_approved_keys.get(issuer_verifying_key, flag),
                   "invalid parameter; not an approved authority");

    // Retrieve information from the current state of the contract
    std::string asset_type_identifier;
    ASSERT_SUCCESS(rsp, issuer_authority_common_store.get(md_asset_type_id_key, asset_type_identifier),
                   "corrupted state; asset type identifier not found");

    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "corrupted state; verifying key not found");

    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "corrupted state; signing key not found");

    // --------------- Build the authority chain ---------------
    std::string serialized_authority_chain;
    ASSERT_SUCCESS(rsp, issuer_authority_common_store.get(md_authority_chain_key, serialized_authority_chain),
                   "corrupted state; serialized authority chain not found");

    ww::exchange::IssuerAuthorityChain authority_chain;
    ASSERT_SUCCESS(rsp, authority_chain.deserialize_string(serialized_authority_chain),
                   "failed to save authority chain; serialization failed");

    const ww::value::StateReference state_reference(env);
    ww::exchange::IssuerAuthority authority(issuer_verifying_key, state_reference);
    ASSERT_SUCCESS(rsp, authority.sign(signing_key, asset_type_identifier),
                   "failed to compute signature");
    ASSERT_SUCCESS(rsp, authority_chain.add_issuer_authority(authority),
                   "failed to create issuer authority chain");

    ww::value::Value serialized_chain;
    ASSERT_SUCCESS(rsp, authority_chain.serialize(serialized_chain),
                   "internal error; failed to serialize chain");

    return rsp.value(serialized_chain, false);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// UTILITY FUNCTIONS
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::add_approved_issuer(
    const std::string& issuer_verifying_key)
{
    return issuer_authority_approved_keys.set(issuer_verifying_key, 1);
}

// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::get_asset_type_identifier(
    std::string& asset_type_identifier)
{
    if (! issuer_authority_common_store.get(md_asset_type_id_key, asset_type_identifier))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::issuer_authority_base::get_authority(
    ww::exchange::IssuerAuthorityChain& authority_chain)
{
    // Retrieve the authority chain from state
    std::string serialized_authority_chain;
    if (! issuer_authority_common_store.get(md_authority_chain_key, serialized_authority_chain))
        return false;

    if (! authority_chain.deserialize_string(serialized_authority_chain))
        return false;

    return true;
}
