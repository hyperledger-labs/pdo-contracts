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

#include <stddef.h>
#include <stdint.h>
#include <string>

#include "Dispatch.h"

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "exchange/exchange.h"

#include "contract/base.h"
#include "exchange/issuer_authority_base.h"

#include "exchange/common/AssetRequest.h"
#include "exchange/common/AuthoritativeAsset.h"
#include "exchange/common/Escrow.h"

static KeyValueStore exchange_state("exchange_state");

static const std::string md_current_state("current_state");
static const std::string md_asset_request("asset_request");
static const std::string md_offered_asset("offered_asset");
static const std::string md_exchanged_asset("exchanged_asset");
static const std::string md_exchanged_asset_owner("exchanged_asset_owner");

#define EXCHANGE_STATE_START     0b0001
#define EXCHANGE_STATE_OFFERED   0b0010
#define EXCHANGE_STATE_COMPLETED 0b0100
#define EXCHANGE_STATE_CANCELLED 0b1000

#define SET_STATE(rsp, _STATE_)                                         \
do {                                                                    \
    const uint32_t current_state = _STATE_;                             \
    if (! exchange_state.set(md_current_state, current_state))          \
        return rsp.error("failed to initialize contract state");        \
} while (0)

#define CHECK_STATE(rsp, _EXPECTED_STATE_)                              \
do {                                                                    \
    uint32_t current_state;                                             \
    if (! exchange_state.get(md_current_state, current_state))          \
        return rsp.error("unexpected error, failed to retrieve current state"); \
    if ((current_state & ( _EXPECTED_STATE_ )) == 0)                    \
        return rsp.error("operation failed, incorrect state");          \
} while (0)

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
bool ww::exchange::exchange::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    const uint32_t current_state = EXCHANGE_STATE_START;
    if (! exchange_state.set(md_current_state, current_state))
        return false;

    const std::string empty_value("");
    if (! exchange_state.set(md_asset_request, empty_value))
        return false;
    if (! exchange_state.set(md_offered_asset, empty_value))
        return false;
    if (! exchange_state.set(md_exchanged_asset, empty_value))
        return false;
    if (! exchange_state.set(md_exchanged_asset_owner, empty_value))
        return false;

    return true;
}

// -----------------------------------------------------------------
// METHOD: initialize
//
// JSON PARAMETERS:
//  asset_request
//  authority_verifying_key
//
// RETURNS:
//   true if asset_request is valid
// -----------------------------------------------------------------
bool ww::exchange::exchange::initialize(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_UNINITIALIZED(rsp);
    ASSERT_SENDER_IS_OWNER(env, rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(EXCH_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    CHECK_STATE(rsp, EXCHANGE_STATE_START);

    // validate and save the asset request
    ww::exchange::AssetRequest asset_request;
    ASSERT_SUCCESS(rsp, asset_request.get_from_message(msg, "asset_request"),
                   "invalid request, malformed parameter, asset_request");
    ASSERT_SUCCESS(rsp, asset_request.count_ > 0,
                   "invalid request, count must be a positive number");

    ASSERT_SUCCESS(rsp, asset_request.save_to_datastore(exchange_state, md_asset_request),
                   "unexpected error, failed to serialize asset request");

    // validate the offered asset
    ww::exchange::AuthoritativeAsset offered_authoritative_asset;
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.get_from_message(msg, "offered_authoritative_asset"),
                   "invalid request, malformed parameter, offered_authoritative_asset");
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.asset_.owner_identity_ == env.originator_id_,
                   "invalid request, only the owner of the asset may offer it in exchange");
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.validate(),
                   "invalid request, malformed parameter, offered_authoritative_asset");

    // verify that the asset was escrowed to us
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve verifying key");
    ASSERT_SUCCESS(rsp, verifying_key == offered_authoritative_asset.asset_.escrow_agent_identity_,
                   "invalid request, malformed parameter, invalid escrow");

    // serialize and save the offered asset
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.save_to_datastore(exchange_state, md_offered_asset),
                   "unexpected error, failed to save offered asset");

    // update the state, now ready to accept exchanges
    SET_STATE(rsp, EXCHANGE_STATE_OFFERED);

    // mark the state as initialized and ready
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "initialization failed");

    // add the asset dependencies to the response
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.issuer_authority_chain_.add_dependencies_to_response(rsp),
                   "unexpected error, failed to add dependencies to response");

    // and return
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: cancel_exchange
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   boolean for success/failure
//
// MODIFIES STATE:
//   true
// -----------------------------------------------------------------
bool ww::exchange::exchange::cancel_exchange(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    ASSERT_SENDER_IS_OWNER(env, rsp);

    CHECK_STATE(rsp, EXCHANGE_STATE_OFFERED);
    SET_STATE(rsp,EXCHANGE_STATE_CANCELLED);

    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: cancel_exchange_attestation
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   #/pdo/wawaka/exchange/basetypes/escrow_release_type
//
// MODIFIES STATE:
//   false
// -----------------------------------------------------------------
bool ww::exchange::exchange::cancel_exchange_attestation(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    ASSERT_SENDER_IS_OWNER(env, rsp);

    CHECK_STATE(rsp, EXCHANGE_STATE_CANCELLED);

    // get the asset for signing
    ww::exchange::AuthoritativeAsset offered_authoritative_asset;
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.get_from_datastore(exchange_state, md_offered_asset),
                   "unexpected error, failed to retrieve offered asset");

    // get the verifying key
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve signing key");

    // get the signing key
    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "unexpected error, failed to retrieve signing key");

    // set up the release request
    ww::exchange::EscrowRelease release_request(env, verifying_key, offered_authoritative_asset.asset_.count_);

    // and finally sign the asset and save the signature in the attestation
    ASSERT_SUCCESS(rsp, release_request.sign(offered_authoritative_asset.asset_, signing_key),
                   "unexpected error, failed to sign release attestation");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, release_request.serialize(result),
                   "unexpected error, failed to serialize release attestation");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: examine_offered_asset
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   #/pdo/wawaka/exchange/basetypes/authoritative_asset_type
//
// MODIFIES STATE:
//   false
// -----------------------------------------------------------------
bool ww::exchange::exchange::examine_offered_asset(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    CHECK_STATE(rsp, EXCHANGE_STATE_OFFERED);

    ww::exchange::AuthoritativeAsset offered_authoritative_asset;
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.get_from_datastore(exchange_state, md_offered_asset),
                   "unexpected error, failed to deserialized offered asset");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.serialize(result),
                   "unexpected error, failed to serialize offered asset");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: examine_requested_asset
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   #/pdo/wawaka/exchange/basetypes/asset_request_type
//
// MODIFIES STATE:
//   false
// -----------------------------------------------------------------
bool ww::exchange::exchange::examine_requested_asset(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    CHECK_STATE(rsp, EXCHANGE_STATE_OFFERED);

    ww::exchange::AssetRequest asset_request;
    ASSERT_SUCCESS(rsp, asset_request.get_from_datastore(exchange_state, md_asset_request),
                   "unexpected error, failed to deserialized asset request");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, asset_request.serialize(result),
                   "unexpected error, failed to serialize asset request");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: exchange_asset
//   submit an asset in response to the asset request
//   the submitted asset must be escrowed to the exchange object
//   the submitted asset must match the request
//
// JSON PARAMETERS:
//   exchanged_authoritative_asset --> #/pdo/wawaka/exchange/basetypes/authoritative_asset_type
//
// RETURNS:
//   boolean
//
// MODIFIES STATE:
//   true
// -----------------------------------------------------------------
bool ww::exchange::exchange::exchange_asset(const Message& msg, const Environment& env, Response& rsp)
{
    // if this fails, we should find a way for the exchange to cancel
    // any additional assets that are escrowed to this contract

    ASSERT_INITIALIZED(rsp);
    CHECK_STATE(rsp, EXCHANGE_STATE_OFFERED);

    ASSERT_SUCCESS(rsp, env.creator_id_ != env.originator_id_,
                   "invalid request, contract owner may not offer exchange asset");

    ASSERT_SUCCESS(rsp, msg.validate_schema(EXCHANGE_ASSET_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // validate the exchange asset
    ww::exchange::AuthoritativeAsset exchanged_authoritative_asset;
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.get_from_message(msg, "exchanged_authoritative_asset"),
                   "invalid request, malformed parameter, exchanged_authoritative_asset");
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.asset_.owner_identity_ == env.originator_id_,
                   "invalid request, only the owner of the asset may offer it in exchange");
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.validate(),
                   "invalid request, malformed parameter, exchanged_authoritative_asset");

    // verify that the asset was escrowed to us
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve verifying key");
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.asset_.escrow_agent_identity_ == verifying_key,
                   "invalid request, malformed parameter, invalid escrow");

    // get the request so we can test the exchanged asset
    ww::exchange::AssetRequest asset_request;
    ASSERT_SUCCESS(rsp, asset_request.get_from_datastore(exchange_state, md_asset_request),
                   "unexpected error, failed to deserialized asset request");
    ASSERT_SUCCESS(rsp, asset_request.check_for_match(exchanged_authoritative_asset),
                   "exchange asset unacceptable");

    // save the exchanged asset and update the state
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.save_to_datastore(exchange_state, md_exchanged_asset),
                   "unexpected error, failed to save exchanged asset");
    ASSERT_SUCCESS(rsp, exchange_state.set(md_exchanged_asset_owner, env.originator_id_),
                   "unexpected error, failed to save exchanged asset owner");

    // update the state, now ready to accept exchanges
    SET_STATE(rsp, EXCHANGE_STATE_COMPLETED);

    // add the asset dependencies to the response
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.issuer_authority_chain_.add_dependencies_to_response(rsp),
                   "unexpected error, failed to add dependencies to response");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: claim_exchange
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   #/pdo/wawaka/exchange/basetypes/escrow_claim_type
//
// MODIFIES STATE:
//   false
// -----------------------------------------------------------------
bool ww::exchange::exchange::claim_exchanged_asset(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    ASSERT_SENDER_IS_OWNER(env, rsp);

    CHECK_STATE(rsp, EXCHANGE_STATE_COMPLETED);

    // get the signing and verifying keys for later use
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve verifying key");

    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "unexpected error, failed to retrieve signing key");

    // set up the claim request
    ww::exchange::EscrowClaim claim_request(env, verifying_key);

    ASSERT_SUCCESS(rsp, exchange_state.get(md_exchanged_asset_owner, claim_request.old_owner_identity_),
                   "unexpected error, failed to get exchanged asset owner");

    ww::exchange::AuthoritativeAsset exchanged_authoritative_asset;
    ASSERT_SUCCESS(rsp, exchanged_authoritative_asset.get_from_datastore(exchange_state, md_exchanged_asset),
                   "unexpected error, failed to deserialized exchanged asset");
    claim_request.count_ = exchanged_authoritative_asset.asset_.count_;

    // and finally sign the asset and save the signature in the attestation
    ASSERT_SUCCESS(rsp, claim_request.sign(exchanged_authoritative_asset.asset_, env.originator_id_, signing_key),
                   "unexpected error, failed to sign claim attestation");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, claim_request.serialize(result),
                   "unexpected error, failed to serialize claim attestation");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: claim_offer
//
// JSON PARAMETERS:
//   None
//
// RETURNS:
//   #/pdo/wawaka/exchange/basetypes/escrow_claim_type
//
// MODIFIES STATE:
//   false
// -----------------------------------------------------------------
bool ww::exchange::exchange::claim_offered_asset(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    CHECK_STATE(rsp, EXCHANGE_STATE_COMPLETED);

    std::string exchanged_asset_owner;
    ASSERT_SUCCESS(rsp, exchange_state.get(md_exchanged_asset_owner, exchanged_asset_owner),
                   "unexpected error, failed to get exchanged asset owner");
    ASSERT_SUCCESS(rsp, exchanged_asset_owner == env.originator_id_,
                   "invalid request, incorrect identity");

    // get the signing and verifying keys for later use
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve verifying key");

    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "unexpected error, failed to retrieve signing key");

    // set up the claim request
    ww::exchange::EscrowClaim claim_request(env, verifying_key);

    // get the asset for signing
    ww::exchange::AuthoritativeAsset offered_authoritative_asset;
    ASSERT_SUCCESS(rsp, offered_authoritative_asset.get_from_datastore(exchange_state, md_offered_asset),
                   "unexpected error, failed to deserialized offered asset");

    claim_request.old_owner_identity_ = offered_authoritative_asset.asset_.owner_identity_;
    claim_request.count_ = offered_authoritative_asset.asset_.count_;

    // and finally sign the asset and save the signature in the attestation
    ASSERT_SUCCESS(rsp, claim_request.sign(offered_authoritative_asset.asset_, env.originator_id_, signing_key),
                   "unexpected error, failed to sign claim attestation");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, claim_request.serialize(result),
                   "unexpected error, failed to serialize claim attestation");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: release_asset
//
// JSON PARAMETERS:
//   None
//
// RETURNS:
//   #/pdo/wawaka/exchange/basetypes/escrow_release_type
//
// MODIFIES STATE:
//   false
// -----------------------------------------------------------------
bool ww::exchange::exchange::release_asset(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    CHECK_STATE(rsp, EXCHANGE_STATE_COMPLETED | EXCHANGE_STATE_CANCELLED);

    ASSERT_SUCCESS(rsp, msg.validate_schema(RELEASE_ASSET_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // we cannot release from escrow either the offered or exchanged assets
    ASSERT_SUCCESS(rsp, env.creator_id_ != env.originator_id_,
                   "invalid request, offered asset owner may not release asset");

    std::string exchanged_asset_owner;
    ASSERT_SUCCESS(rsp, exchange_state.get(md_exchanged_asset_owner, exchanged_asset_owner),
                   "unexpected error, failed to get exchanged asset owner");
    ASSERT_SUCCESS(rsp, exchanged_asset_owner != env.originator_id_,
                   "invalid request, exchange asset owner may not release asset");

    // validate the escrowed asset parameter
    ww::exchange::AuthoritativeAsset escrowed_authoritative_asset;
    ASSERT_SUCCESS(rsp, escrowed_authoritative_asset.get_from_message(msg, "escrowed_authoritative_asset"),
                   "invalid request, malformed parameter, escrowed_authoritative_asset");
    ASSERT_SUCCESS(rsp, escrowed_authoritative_asset.validate(),
                   "invalid request, malformed parameter, escrowed_authoritative_asset");

    // get the keys for this contract
    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "unexpected error, failed to retrieve signing key");

    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve verifying key");

    // verify that the asset was escrowed to this contract
    ASSERT_SUCCESS(rsp, escrowed_authoritative_asset.asset_.escrow_agent_identity_ == verifying_key,
                   "invalid request, malformed parameter, invalid escrow");

    // verify the that the message originator is the owner of the asset being released
    ASSERT_SUCCESS(rsp, escrowed_authoritative_asset.asset_.owner_identity_ == env.originator_id_,
                   "invalid request, only the owner of the asset may offer it in exchange");

    // create the escrow release response
    ww::exchange::EscrowRelease release_request(env, verifying_key, escrowed_authoritative_asset.asset_.count_);

    // and finally sign the asset and save the signature in the attestation
    ASSERT_SUCCESS(rsp, release_request.sign(escrowed_authoritative_asset.asset_, signing_key),
                   "unexpected error, failed to sign release attestation");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, release_request.serialize(result),
                   "unexpected error, failed to serialize release attestation");

    return rsp.value(result, false);
}
