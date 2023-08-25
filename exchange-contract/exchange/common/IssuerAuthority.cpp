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
#include "WasmExtensions.h"

#include "Common.h"
#include "Cryptography.h"
#include "IssuerAuthority.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::IssuerAuthority
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
static const ww::exchange::IssuerAuthority issuer_authority_schema;

// -----------------------------------------------------------------
ww::exchange::IssuerAuthority::IssuerAuthority(void) :
    authorized_issuer_verifying_key_(""),
    authorizing_signature_ ("")
{
}

// -----------------------------------------------------------------
ww::exchange::IssuerAuthority::IssuerAuthority(
    const std::string& issuer_verifying_key,
    const ww::value::StateReference& reference) :
    authorized_issuer_verifying_key_(issuer_verifying_key),
    authorizing_signature_(""),
    state_reference_(reference)
{
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthority::serialize_for_signing(
    const std::string& asset_type_identifier,
    std::string& serialized
    ) const
{

    ww::value::Value serialized_reference_object;
    if (! state_reference_.serialize(serialized_reference_object))
        return false;

    std::string serialized_reference;
    if (! serialized_reference_object.serialize(serialized_reference))
        return false;

    // we serialize in an array to ensure that there is a consistent ordering
    ww::value::Array serializer;
    serializer.append_string(asset_type_identifier.c_str());
    serializer.append_string(authorized_issuer_verifying_key_.c_str());
    serializer.append_string(serialized_reference.c_str());

    // serialize the rest of the structure
    if (! serializer.serialize(serialized))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthority::deserialize(const ww::value::Object& authority)
{
    if (! ww::exchange::IssuerAuthority::verify_schema(authority))
        return false;

    authorized_issuer_verifying_key_ = authority.get_string("authorized_issuer_verifying_key");
    authorizing_signature_ = authority.get_string("authorizing_signature");

    ww::value::Object reference_value;
    if (! authority.get_value("issuer_state_reference", reference_value))
        return false;

    if (! state_reference_.deserialize(reference_value))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthority::serialize(ww::value::Value& serialized_authority) const
{
    ww::value::Value serialized_reference;
    if (! state_reference_.serialize(serialized_reference))
        return false;

    ww::value::Structure authority(ISSUER_AUTHORITY_SCHEMA);
    if (! authority.set_string("authorized_issuer_verifying_key", authorized_issuer_verifying_key_.c_str()))
        return false;
    if (! authority.set_string("authorizing_signature", authorizing_signature_.c_str()))
        return false;
    if (! authority.set_value("issuer_state_reference", serialized_reference))
        return false;

    serialized_authority.set(authority);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthority::sign(
    const std::string& authorizing_signing_key,
    const std::string& asset_type_identifier
    )
{
    // serialize the authority for signing
    std::string serialized_string;
    if (! serialize_for_signing(asset_type_identifier, serialized_string))
    {
        CONTRACT_SAFE_LOG(3, "failed to serialize issuer authority");
        return false;
    }

    // sign the serialized authority
    const ww::types::ByteArray serialized_array(serialized_string.begin(), serialized_string.end());
    ww::types::ByteArray signature_array;
    if (! ww::crypto::ecdsa::sign_message(serialized_array, authorizing_signing_key, signature_array))
    {
        CONTRACT_SAFE_LOG(3, "failed to sign serialized issuer authority");
        return false;
    }

    // base64 encode the signature so we can use it in the JSON
    if (! ww::crypto::b64_encode(signature_array, authorizing_signature_))
    {
        CONTRACT_SAFE_LOG(3, "failed to encode issuer authority signature");
        return false;
    }

    // save the encoded array in the signature field
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthority::verify_signature(
    const std::string& authorizing_verifying_key,
    const std::string& asset_type_identifier
    ) const
{
    // serialize the authority for signing
    std::string serialized_string;
    if (! serialize_for_signing(asset_type_identifier, serialized_string))
    {
        CONTRACT_SAFE_LOG(3, "failed to serialize issuer authority");
        return false;
    }

    const ww::types::ByteArray serialized_array(serialized_string.begin(), serialized_string.end());

    // sign the signature from the object
    ww::types::ByteArray signature_array;
    if (! ww::crypto::b64_decode(authorizing_signature_, signature_array))
    {
        CONTRACT_SAFE_LOG(3, "failed to decode issuer authority signature");
        return false;
    }

    if (! ww::crypto::ecdsa::verify_signature(serialized_array, authorizing_verifying_key, signature_array))
    {
        CONTRACT_SAFE_LOG(2, "failed to verify issuer authority");
        return false;
    }

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthority::validate(
    const std::string& authorizing_verifying_key,
    const std::string& asset_type_identifier
    ) const
{
    return verify_signature(authorizing_verifying_key, asset_type_identifier);
}
