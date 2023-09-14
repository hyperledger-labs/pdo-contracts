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

#include "Value.h"

#include "Asset.h"
#include "Cryptography.h"
#include "StateReference.h"
#include "Types.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::Asset
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
ww::exchange::Asset::Asset(
    const std::string& owner_identity,
    const std::string& asset_type_identifier,
    uint32_t count) :
    owner_identity_(owner_identity),
    escrow_agent_identity_(owner_identity),
    asset_type_identifier_(asset_type_identifier),
    count_(count),
    escrow_identifier_("")
{
}

// -----------------------------------------------------------------
bool ww::exchange::Asset::serialize_for_escrow_signing(
    const ww::value::StateReference& escrow_agent_state_reference,
    std::string& serialized) const
{
    ww::value::Value serialized_reference;
    if (! escrow_agent_state_reference.serialize(serialized_reference))
        return false;

    ww::value::Array serializer;
    serializer.append_number(count_);
    serializer.append_string(asset_type_identifier_.c_str());
    serializer.append_string(owner_identity_.c_str());
    serializer.append_string(escrow_agent_identity_.c_str());
    serializer.append_string(escrow_identifier_.c_str());
    serializer.append_value(serialized_reference);

    if (! serializer.serialize(serialized))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::Asset::deserialize(
    const ww::value::Object& asset)
{
    if (! ww::exchange::Asset::verify_schema(asset))
        return false;

    asset_type_identifier_ = asset.get_string("asset_type_identifier");
    count_ = (unsigned int)asset.get_number("count");
    owner_identity_ = asset.get_string("owner_identity");
    escrow_agent_identity_ = asset.get_string("escrow_agent_identity");
    escrow_identifier_ = asset.get_string("escrow_identifier");

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::Asset::serialize(
    ww::value::Value& serialized_asset) const
{
    ww::value::Structure asset(ASSET_SCHEMA);

    if (! asset.set_string("asset_type_identifier", asset_type_identifier_.c_str()))
        return false;
    if (! asset.set_number("count", count_))
        return false;
    if (! asset.set_string("owner_identity", owner_identity_.c_str()))
        return false;
    if (! asset.set_string("escrow_agent_identity", escrow_agent_identity_.c_str()))
        return false;
    if (! asset.set_string("escrow_identifier", escrow_identifier_.c_str()))
        return false;

    serialized_asset.set(asset);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::Asset::escrow(
    const std::string& escrow_agent_identity)
{
    escrow_agent_identity_ = escrow_agent_identity;

    // create a random identifier
    ww::types::ByteArray id_array(32);
    if (! ww::crypto::random_identifier(id_array))
        return false;

    // base64 encode the random identifier
    if (! ww::crypto::b64_encode(id_array, escrow_identifier_))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::Asset::sign_for_escrow(
    const ww::value::StateReference& escrow_agent_state_reference,
    const std::string& escrow_agent_signing_key,
    std::string& encoded_signature) const
{
    // serialize the asset
    std::string serialized_string;
    if (! serialize_for_escrow_signing(escrow_agent_state_reference, serialized_string))
        return false;

    const ww::types::ByteArray serialized(serialized_string.begin(), serialized_string.end());

    // sign the serialized authority
    ww::types::ByteArray signature;
    if (! ww::crypto::ecdsa::sign_message(serialized, escrow_agent_signing_key, signature))
        return false;

    // base64 encode the signature so we can use it in the JSON
    if (! ww::crypto::b64_encode(signature, encoded_signature))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::Asset::verify_escrow_signature(
    const ww::value::StateReference& escrow_agent_state_reference,
    const std::string& encoded_signature) const
{
    // serialize the asset
    std::string serialized_string;
    if (! serialize_for_escrow_signing(escrow_agent_state_reference, serialized_string))
        return false;

    const ww::types::ByteArray serialized(serialized_string.begin(), serialized_string.end());

    // sign the signature from the object
    ww::types::ByteArray signature;
    if (! ww::crypto::b64_decode(encoded_signature, signature))
        return false;

    // and verify the signature
    if (! ww::crypto::ecdsa::verify_signature(serialized, escrow_agent_identity_, signature))
        return false;

    return true;
}
