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

#include "Dispatch.h"

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"
#include "Types.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "exchange/issuer.h"

#include "contract/base.h"
#include "exchange/issuer_authority_base.h"

#include "exchange/common/AuthoritativeAsset.h"
#include "exchange/common/Common.h"
#include "exchange/common/Escrow.h"
#include "exchange/common/LedgerEntry.h"
#include "exchange/common/LedgerStore.h"

static ww::exchange::LedgerStore ledger_store("ledger");

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
bool ww::exchange::issuer::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    return true;
}

// -----------------------------------------------------------------
// METHOD: issue
//
// JSON PARAMETERS:
//   owner_identity
//   count
//
// RETURNS:
//   boolean
// -----------------------------------------------------------------
bool ww::exchange::issuer::issue(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(ISSUE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // in theory, owner is an escda key, in practice it could be anything
    // but only an ecdsa key can be used meaningfully
    const std::string owner(msg.get_string("owner_identity"));
    ASSERT_SUCCESS(rsp, ! owner.empty(),
                   "invalid request, invalid owner identity parameter");
    ASSERT_SUCCESS(rsp, ! ledger_store.exists(owner),
                   "invalid request, duplicate issuance");

    const int count = (int) msg.get_number("count");
    ASSERT_SUCCESS(rsp, count > 0,
                   "invalid request, invalid asset count");

    std::string asset_type_identifier;
    ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                   "internal error, contract state corrupted, no asset type identifier");

    ASSERT_SUCCESS(rsp, ledger_store.add_entry(owner, asset_type_identifier, (uint32_t)count),
                   "ledger operation failed, unable to save issuance");

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
bool ww::exchange::issuer::get_balance(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ww::exchange::LedgerEntry entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(env.originator_id_, entry),
                   "no entry for originator");

    ww::value::Number balance(entry.asset_.count_);
    return rsp.value(balance, false);
}

// -----------------------------------------------------------------
// METHOD: get_entry
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   current number of assets assigned to the requestor
// -----------------------------------------------------------------
bool ww::exchange::issuer::get_entry(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ww::exchange::LedgerEntry entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(env.originator_id_, entry),
                   "no entry for originator");

    ww::value::Object result;
    ASSERT_SUCCESS(rsp, entry.serialize(result),
                   "internal error, failed to seralize ledger entry");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: transfer
//
// JSON PARAMETERS:
//   new_owner_identity
//   count
//
// RETURNS:
//   boolean
// -----------------------------------------------------------------
bool ww::exchange::issuer::transfer(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(TRANSFER_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string old_owner(env.originator_id_);

    const std::string new_owner(msg.get_string("new_owner_identity"));
    ASSERT_SUCCESS(rsp, new_owner.size() > 0, "invalid transfer request, invalid owner identity parameter");

    // if the old and new accounts are the same, then there is nothing to be done
    if (old_owner == new_owner)
        return rsp.success(false);

    const int count = (int) msg.get_number("count");
    ASSERT_SUCCESS(rsp, count > 0, "invalid transfer request, invalid asset count");

    // if there is no issuance for this identity, we treat it as a 0 balance
    ww::exchange::LedgerEntry old_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(old_owner, old_entry),
                   "transfer failed, insufficient balance for transfer");
    ASSERT_SUCCESS(rsp, count <= old_entry.asset_.count_,
                   "transfer failed, insufficient balance for transfer");

    if (! ledger_store.exists(new_owner))
    {
        std::string asset_type_identifier;
        ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                       "internal error, no asset type identifier");

        ASSERT_SUCCESS(rsp, ledger_store.add_entry(new_owner, asset_type_identifier, 0),
                       "transfer failed, failed to add new owner");
    }

    ww::exchange::LedgerEntry new_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(new_owner, new_entry),
                   "transfer failed, failed to find new owner");

    // after all the set up, finally transfer the assets
    old_entry.asset_.count_ = old_entry.asset_.count_ - (uint32_t)count;
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(old_owner, old_entry), "unexpected error");

    new_entry.asset_.count_ = new_entry.asset_.count_ + (uint32_t)count;
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(new_owner, new_entry), "unexpected error");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: escrow
//
// JSON PARAMETERS:
//   escrow_agent_identity
//
// RETURNS:
//   boolean
// -----------------------------------------------------------------
bool ww::exchange::issuer::escrow(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(ESCROW_PARAM_SCHEMA),
                   "invalid escrow request, missing required parameters");

    const std::string escrow_agent(msg.get_string("escrow_agent_identity"));
    const int count = (int) msg.get_number("count");
    ASSERT_SUCCESS(rsp, 0 <= count, "invalid request, invalid asset count");

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
// METHOD: escrow_attestation
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   authoritative_asset_type
// -----------------------------------------------------------------
bool ww::exchange::issuer::escrow_attestation(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(ESCROW_ATTESTATION_PARAM_SCHEMA),
                   "invalid escrow attestation request, missing required parameters");

    const std::string owner(env.originator_id_);
    const std::string escrow_agent(msg.get_string("escrow_agent_identity"));

    // get the verifying key
    std::string verifying_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_verifying_key(verifying_key),
                   "unexpected error, failed to retrieve signing key");

    // get the signing key
    std::string signing_key;
    ASSERT_SUCCESS(rsp, ww::contract::base::get_signing_key(signing_key),
                   "unexpected error, failed to retrieve signing key");

    // if there is no issuance for this identity, we treat it as a 0 balance
    ww::exchange::LedgerEntry entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(owner, entry),
                   "invalid escrow attestation request, no entry for requestor");

    ww::exchange::AuthoritativeAsset authoritative_asset;
    ASSERT_SUCCESS(rsp, entry.get_escrowed_asset(escrow_agent, authoritative_asset.asset_),
                   "invalid escrow attestation request, asset is not escrowed");
    ASSERT_SUCCESS(rsp, authoritative_asset.issuer_state_reference_.set_from_environment(env),
                   "expected error, failed to set state reference");
    ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_authority(authoritative_asset.issuer_authority_chain_),
                   "unexpected error, failed to retrieve issuer authority");
    authoritative_asset.issuer_identity_ = verifying_key;

    ASSERT_SUCCESS(rsp, authoritative_asset.sign(signing_key),
                   "unexpected error, failed to sign authoritative asset");

    ww::value::Value result;
    ASSERT_SUCCESS(rsp, authoritative_asset.serialize(result),
                   "unexpected error, failed to serialize authoritative asset");

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// METHOD: release
//
// JSON PARAMETERS:
//   escrow_agent_state_reference
//   escrow_agent_signature
//
// RETURNS:
//   boolean
// -----------------------------------------------------------------
bool ww::exchange::issuer::release(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    // handle the parameters
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

    ASSERT_SUCCESS(rsp, entry.release_escrow(release_request.escrow_agent_identity_), "unexpected error");

    // update the entry
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(owner, entry), "escrow failed, unable to update entry");

    // add the dependency to the response
    ASSERT_SUCCESS(rsp, release_request.escrow_agent_state_reference_.add_to_response(rsp),
                   "release request failed, unable to save state reference");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: claim
//
// JSON PARAMETERS:
//   escrow_claim
//
// RETURNS:
//   boolean
// -----------------------------------------------------------------
bool ww::exchange::issuer::claim(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    // handle the parameters
    ASSERT_SUCCESS(rsp, msg.validate_schema(CLAIM_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string new_owner_identity(env.originator_id_);

    ww::exchange::EscrowClaim claim_request;
    ASSERT_SUCCESS(rsp, claim_request.get_from_message(msg, "claim_request"),
                   "invalid request, malformed parameter, claim_request");

    // get the old owner's entry from the ledger
    ww::exchange::LedgerEntry old_owner_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(claim_request.old_owner_identity_, old_owner_entry),
                   "invalid claim request, no such asset");

    // get the escrowed asset information
    ww::exchange::Asset old_escrowed_asset;
    ASSERT_SUCCESS(rsp, old_owner_entry.get_escrowed_asset(claim_request.escrow_agent_identity_, old_escrowed_asset),
                   "invalid claim request, not escrowed");

    // check the signature from the escrow agent
    ASSERT_SUCCESS(rsp, claim_request.verify_signature(old_escrowed_asset, new_owner_identity),
                   "invalid claim request, signature verification failed");

    // update the old entry and save it back to the ledger
    ASSERT_SUCCESS(rsp, old_owner_entry.transfer_escrow(claim_request.escrow_agent_identity_, claim_request.count_),
                   "unexpected error, failed to update ledger entry");

    ASSERT_SUCCESS(rsp, ledger_store.set_entry(claim_request.old_owner_identity_, old_owner_entry),
                   "unexpected error, failed to update ledger entry");

    // get the new owner's entry from the ledger, create an empty
    // entry if one does not already exist
    if (! ledger_store.exists(new_owner_identity))
    {
        const int count = 0;
        std::string asset_type_identifier;
        ASSERT_SUCCESS(rsp, ww::exchange::issuer_authority_base::get_asset_type_identifier(asset_type_identifier),
                       "contract state corrupted, no asset type identifier");
        ASSERT_SUCCESS(rsp, ledger_store.add_entry(new_owner_identity, asset_type_identifier, (uint32_t)count),
                       "ledger operation failed, unable to save issuance");
    }

    ww::exchange::LedgerEntry new_owner_entry;
    ASSERT_SUCCESS(rsp, ledger_store.get_entry(new_owner_identity, new_owner_entry),
                   "contract state corrupted, no issuance located");

    new_owner_entry.asset_.count_ = new_owner_entry.asset_.count_ + claim_request.count_;
    ASSERT_SUCCESS(rsp, ledger_store.set_entry(new_owner_identity, new_owner_entry),
                   "unexpected error, failed to update ledger entry");

    // add the dependency to the response
    ASSERT_SUCCESS(rsp, claim_request.escrow_agent_state_reference_.add_to_response(rsp),
                   "release request failed, unable to save state reference");

    return rsp.success(true);
}
