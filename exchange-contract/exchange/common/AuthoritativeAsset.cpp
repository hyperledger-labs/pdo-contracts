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

#include "Types.h"
#include "Value.h"

#include "Asset.h"
#include "AuthoritativeAsset.h"
#include "Common.h"
#include "Cryptography.h"
#include "IssuerAuthorityChain.h"
#include "StateReference.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::AuthoritativeAsset
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
ww::exchange::AuthoritativeAsset::AuthoritativeAsset(void) :
    issuer_identity_(""), encoded_signature_("")
{
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::serialize_for_signing(std::string& serialized) const
{
    // we do not serialize the authority chain because it is
    // bound to the asset through the verifying key that it
    // establishes. that is, the authority chain establishes
    // the authority of the key that signs the asset and state
    // reference so we do not need to include it in the
    // serialized buffer

    ww::value::Value serialized_asset;
    if (! asset_.serialize(serialized_asset))
        return false;

    ww::value::Value serialized_reference;
    if (! issuer_state_reference_.serialize(serialized_reference))
        return false;

    // we serialize in an array to ensure that there is a consistent ordering
    ww::value::Array serializer;
    serializer.append_value(serialized_asset);
    serializer.append_value(serialized_reference);

    // serialize the rest of the structure
    if (! serializer.serialize(serialized))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::exchange::AuthoritativeAsset::verify_schema(serialized_object))
        return false;

    ww::value::Structure asset_object(ASSET_SCHEMA);
    if (! serialized_object.get_value("asset", asset_object))
    {
        CONTRACT_SAFE_LOG(3, "deserialize asset in authoritative asset");
        return false;
    }

    if (! asset_.deserialize(asset_object))
        return false;

    ww::value::Structure reference_object(STATE_REFERENCE_SCHEMA);
    if (! serialized_object.get_value("issuer_state_reference", reference_object))
        return false;

    if (! issuer_state_reference_.deserialize(reference_object))
        return false;

    ww::value::Structure authority_chain_object(ISSUER_AUTHORITY_CHAIN_SCHEMA);
    if (! serialized_object.get_value("issuer_authority_chain", authority_chain_object))
        return false;

    if (! issuer_authority_chain_.deserialize(authority_chain_object))
        return false;

    issuer_identity_ = serialized_object.get_string("issuer_identity");
    encoded_signature_ = serialized_object.get_string("issuer_signature");

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::serialize(ww::value::Value& serialized_value) const
{
    ww::value::Structure asset_object(AUTHORITATIVE_ASSET_SCHEMA);

    ww::value::Value value;

    // asset
    if (! asset_.serialize(value))
        return false;
    if (! asset_object.set_value("asset", value))
    {
        CONTRACT_SAFE_LOG(3, "serialize asset in authoritative asset");
        return false;
    }

    // reference
    if (! issuer_state_reference_.serialize(value))
        return false;
    if (! asset_object.set_value("issuer_state_reference", value))
        return false;

    // authority chain
    if (! issuer_authority_chain_.serialize(value))
        return false;
    if (! asset_object.set_value("issuer_authority_chain", value))
        return false;

    // strings
    if (! asset_object.set_string("issuer_identity", issuer_identity_.c_str()))
        return false;
    if (! asset_object.set_string("issuer_signature", encoded_signature_.c_str()))
        return false;

    serialized_value.set(asset_object);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::sign(
    const std::string& authorizing_signing_key)
{
    std::string serialized_string;
    if (! serialize_for_signing(serialized_string))
        return false;
    ww::types::ByteArray serialized(serialized_string.begin(), serialized_string.end());

    // sign the serialized authority
    ww::types::ByteArray signature;
    if (! ww::crypto::ecdsa::sign_message(serialized, authorizing_signing_key, signature))
        return false;

    // base64 encode the signature so we can use it in the JSON
    if (! ww::crypto::b64_encode(signature, encoded_signature_))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::verify_signature(
    const std::string& authorizing_verifying_key) const
{
    std::string serialized_string;
    if (! serialize_for_signing(serialized_string))
        return false;

    // sign the signature from the object
    ww::types::ByteArray signature;
    if (! ww::crypto::b64_decode(encoded_signature_, signature))
        return false;

    ww::types::ByteArray serialized(serialized_string.begin(), serialized_string.end());
    if (! ww::crypto::ecdsa::verify_signature(serialized, authorizing_verifying_key, signature))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::validate(void) const
{
    // verify the authority of the issuer
    std::string issuer_verifying_key;
    if (! issuer_authority_chain_.get_issuer_identity(issuer_verifying_key))
        return false;

    if (! issuer_authority_chain_.validate_issuer_key(issuer_verifying_key))
        return false;

    // verify the issuer's signature on the asset
    return verify_signature(issuer_verifying_key);
}

// -----------------------------------------------------------------
bool ww::exchange::AuthoritativeAsset::get_issuer_identity(
    std::string& issuer_verifying_key) const
{
    return issuer_authority_chain_.get_issuer_identity(issuer_verifying_key);
}
