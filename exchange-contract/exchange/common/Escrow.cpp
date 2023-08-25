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

#include "Cryptography.h"
#include "Types.h"
#include "Value.h"

#include "Asset.h"
#include "Escrow.h"


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::EscrowBase
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// -----------------------------------------------------------------
ww::exchange::EscrowBase::EscrowBase(void) :
    encoded_escrow_agent_signature_(""),
    escrow_agent_identity_(""),
    count_(0)
{
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowBase::sign(
    const std::string& serialized_string,
    const std::string& escrow_agent_signing_key)
{
    ww::types::ByteArray serialized(serialized_string.begin(), serialized_string.end());

    // sign the serialized claim
    ww::types::ByteArray signature;
    if (! ww::crypto::ecdsa::sign_message(serialized, escrow_agent_signing_key, signature))
        return false;

    // base64 encode the signature so we can use it in the JSON
    if (! ww::crypto::b64_encode(signature, encoded_escrow_agent_signature_))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowBase::verify_signature(
    const std::string& serialized_string) const
{
    ww::types::ByteArray serialized(serialized_string.begin(), serialized_string.end());

    ww::types::ByteArray signature;
    if (! ww::crypto::b64_decode(encoded_escrow_agent_signature_, signature))
        return false;

    if (! ww::crypto::ecdsa::verify_signature(serialized, escrow_agent_identity_, signature))
        return false;

    return true;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::EscrowRelease
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// -----------------------------------------------------------------
ww::exchange::EscrowRelease::EscrowRelease(void) :
    ww::exchange::EscrowBase()
{
    return;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowRelease::serialize_for_signing(
    const ww::exchange::Asset& asset,
    std::string& serialized) const
{
    const ww::value::String operation("release");

    ww::value::Value serialized_asset;
    if (! asset.serialize(serialized_asset))
        return false;

    ww::value::Value serialized_reference;
    if (! escrow_agent_state_reference_.serialize(serialized_reference))
        return false;

    // we use the array to ensure that the ordering of fields
    // is consistent
    ww::value::Array serializer;
    serializer.append_value(operation);
    serializer.append_value(serialized_asset);
    serializer.append_value(serialized_reference);

    if (! serializer.serialize(serialized))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowRelease::deserialize(
    const ww::value::Object& release)
{
    if (! ww::exchange::EscrowRelease::verify_schema(release))
        return false;

    ww::value::Object reference_value;
    if (! release.get_value("escrow_agent_state_reference", reference_value))
        return false;

    if (! escrow_agent_state_reference_.deserialize(reference_value))
        return false;

    encoded_escrow_agent_signature_ = release.get_string("escrow_agent_signature");
    escrow_agent_identity_ = release.get_string("escrow_agent_identity");
    count_ = release.get_number("count");
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowRelease::serialize(
    ww::value::Value& serialized_release) const
{
    ww::value::Value serialized_reference;
    if (! escrow_agent_state_reference_.serialize(serialized_reference))
        return false;

    ww::value::Structure release(ESCROW_RELEASE_SCHEMA);
    if (! release.set_string("escrow_agent_signature", encoded_escrow_agent_signature_.c_str()))
        return false;
    if (! release.set_string("escrow_agent_identity", escrow_agent_identity_.c_str()))
        return false;
    if (! release.set_number("count", count_))
        return false;
    if (! release.set_value("escrow_agent_state_reference", serialized_reference))
        return false;

    serialized_release.set(release);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowRelease::sign(
    const ww::exchange::Asset& asset,
    const std::string& escrow_agent_signing_key)
{
    std::string serialized;
    if (! serialize_for_signing(asset, serialized))
        return false;

    return ww::exchange::EscrowBase::sign(serialized, escrow_agent_signing_key);
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowRelease::verify_signature(
    const ww::exchange::Asset& asset) const
{
    std::string serialized;
    if (! serialize_for_signing(asset, serialized))
        return false;

    return ww::exchange::EscrowBase::verify_signature(serialized);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::EscrowClaim
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
ww::exchange::EscrowClaim::EscrowClaim(void) :
    ww::exchange::EscrowBase()
{
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowClaim::serialize_for_signing(
    const ww::exchange::Asset& asset,
    const std::string& new_owner_identity,
    std::string& serialized) const
{
    const ww::value::String operation("claim");

    ww::value::Value serialized_asset;
    if (! asset.serialize(serialized_asset))
        return false;

    ww::value::Value serialized_reference;
    if (! escrow_agent_state_reference_.serialize(serialized_reference))
        return false;

    // we use the array to ensure that the ordering of fields
    // is consistent
    ww::value::Array serializer;
    serializer.append_value(operation);
    serializer.append_value(serialized_asset);
    serializer.append_string(new_owner_identity.c_str());
    serializer.append_value(serialized_reference);

    if (! serializer.serialize(serialized))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowClaim::deserialize(
    const ww::value::Object& claim)
{
    if (! ww::exchange::EscrowRelease::verify_schema(claim))
        return false;

    old_owner_identity_ = claim.get_string("old_owner_identity");

    ww::value::Object reference_value;
    if (! claim.get_value("escrow_agent_state_reference", reference_value))
        return false;

    if (! escrow_agent_state_reference_.deserialize(reference_value))
        return false;

    encoded_escrow_agent_signature_ = claim.get_string("escrow_agent_signature");
    escrow_agent_identity_ = claim.get_string("escrow_agent_identity");
    count_ = claim.get_number("count");
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowClaim::serialize(
    ww::value::Value& serialized_claim) const
{
    ww::value::Value serialized_reference;
    if (! escrow_agent_state_reference_.serialize(serialized_reference))
        return false;

    ww::value::Structure claim(ESCROW_CLAIM_SCHEMA);
    if (! claim.set_string("old_owner_identity", old_owner_identity_.c_str()))
        return false;
    if (! claim.set_string("escrow_agent_signature", encoded_escrow_agent_signature_.c_str()))
        return false;
    if (! claim.set_string("escrow_agent_identity", escrow_agent_identity_.c_str()))
        return false;
    if (! claim.set_number("count", count_))
        return false;
    if (! claim.set_value("escrow_agent_state_reference", serialized_reference))
        return false;

    serialized_claim.set(claim);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowClaim::sign(
    const ww::exchange::Asset& asset,
    const std::string& new_owner_identity,
    const std::string& escrow_agent_signing_key)
{
    std::string serialized;
    if (! serialize_for_signing(asset, new_owner_identity, serialized))
        return false;

    return ww::exchange::EscrowBase::sign(serialized, escrow_agent_signing_key);
}

// -----------------------------------------------------------------
bool ww::exchange::EscrowClaim::verify_signature(
    const ww::exchange::Asset& asset,
    const std::string& new_owner_identity) const
{
    std::string serialized;
    if (! serialize_for_signing(asset, new_owner_identity, serialized))
        return false;

    return ww::exchange::EscrowBase::verify_signature(serialized);
}
