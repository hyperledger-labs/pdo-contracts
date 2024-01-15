/* Copyright 2024 Intel Corporation
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
#include <vector>

#include "Types.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "Cryptography.h"

#include "exchange/common/Common.h"
#include "identity/common/Credential.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::SigningContext
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
// -----------------------------------------------------------------
static bool deserialize_context_path(
    const ww::value::Array& context_array,
    std::vector<std::string>& context_path)
{
    context_path.resize(0);

    const size_t count = context_array.get_count();
    for (size_t index = 0; index < count; index++)
    {
        const std::string c = context_array.get_string(index);
        context_path.push_back(c);
    }

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
static bool serialize_context_path(
    const std::vector<std::string>& context_path,
    ww::value::Array& context_array)
{
    for (size_t index = 0; index < context_path.size(); index++)
    {
        if (! context_array.append_string(context_path[index].c_str()))
            return false;
    }

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Identity::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::Identity::verify_schema(serialized_object))
        return false;

    id_ = serialized_object.get_string("id");
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Identity::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(IDENTITY_SCHEMA);
    if (! serializer.set_string("id", id_.c_str()))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::IdentityKey::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::IdentityKey::verify_schema(serialized_object))
        return false;

    id_ = serialized_object.get_string("id");

    ww::value::Array context_array;
    if (! serialized_object.get_value("context_path", context_array))
        return false;

    if (! deserialize_context_path(context_array, context_path_))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::IdentityKey::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(IDENTITY_KEY_SCHEMA);
    if (! serializer.set_string("id", id_.c_str()))
        return false;

    ww::value::Array context_array;
    if (! serialize_context_path(context_path_, context_array))
        return false;

    if (! serializer.set_value("context_path", context_array))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Claims::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::Claims::verify_schema(serialized_object))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Claims::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(CLAIMS_SCHEMA);

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Proof::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::Proof::verify_schema(serialized_object))
        return false;

    type_ = serialized_object.get_string("type");

    ww::value::Structure serialized_identity_key(IDENTITY_KEY_SCHEMA);
    if (! serialized_object.get_value("verificationMethod", serialized_identity_key))
        return false;
    if (! verificationMethod_.deserialize(serialized_identity_key))
        return false;

    proofValue_ = serialized_object.get_string("proofValue");

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Proof::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(PROOF_SCHEMA);

    if (! serializer.set_string("type", type_.c_str()))
        return false;

    ww::value::Structure serialized_identity_key(IDENTITY_KEY_SCHEMA);
    if (! verificationMethod_.serialize(serialized_identity_key))
        return false;
    if (! serializer.set_value("verificationMethod", serialized_identity_key))
        return false;

    if (! serializer.set_string("proofValue", proofValue_.c_str()))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Credential::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::Credential::verify_schema(serialized_object))
        return false;

    ww::value::Object serialized_issuer;
    if (! serialized_object.get_value("issuer", serialized_issuer))
        return false;
    if (! issuer_.deserialize(serialized_issuer))
        return false;

    ww::value::Object serialized_claims;
    if (! serialized_object.get_value("credentialSubject", serialized_claims))
        return false;
    if (! credentialSubject_.deserialize(serialized_claims))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Credential::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(CREDENTIAL_SCHEMA);

    ww::value::Value serialized_issuer;
    if (! issuer_.serialize(serialized_issuer))
        return false;
    if (! serializer.set_value("issuer", serialized_issuer))
        return false;

    ww::value::Value serialized_claims;
    if (! credentialSubject_.serialize(serialized_claims))
        return false;
    if (! serializer.set_value("credentialSubject", serialized_claims))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::VerifiableCredential::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::VerifiableCredential::verify_schema(serialized_object))
        return false;

    serializedCredential_ = serialized_object.get_string("serializedCredential");

    ww::value::Object serialized_proof;
    if (! serialized_object.get_value("proof", serialized_proof))
        return false;
    if (! proof_.deserialize(serialized_proof))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::VerifiableCredential::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(VERIFIABLE_CREDENTIAL_SCHEMA);

    serialized_object.set(serializer);
    if (! serializer.set_string("serializedCredential", serializedCredential_.c_str()))
        return false;

    ww::value::Value serialized_proof;
    if (! proof_.serialize(serialized_proof))
        return false;
    if (! serializer.set_value("proof", serialized_proof))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Presentation::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::Presentation::verify_schema(serialized_object))
        return false;

    ww::value::Object serialized_holder;
    if (! serialized_object.get_value("holder", serialized_holder))
        return false;
    if (! holder_.deserialize(serialized_holder))
        return false;

    ww::value::Array serialized_credential_list;
    if (! serialized_object.get_value("verifiableCredential", serialized_credential_list))
        return false;

    const size_t count = serialized_credential_list.get_count();
    for (size_t index = 0; index < count; index++)
    {
        ww::value::Object serialized_credential;
        if (! serialized_credential_list.get_value(index, serialized_credential))
            return false;

        ww::identity::VerifiableCredential credential;
        if (! credential.deserialize(serialized_credential))
            return false;

        verifiableCredential_.push_back(credential);
    }

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Presentation::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(PRESENTATION_SCHEMA);

    ww::value::Value serialized_holder;
    if (! holder_.serialize(serialized_holder))
        return false;
    serializer.set_value("holder", serialized_holder);

    ww::value::Array serialized_credential_list;
    for (size_t index = 0; index < verifiableCredential_.size(); index++)
    {
        ww::value::Object serialized_credential;
        if (! verifiableCredential_[index].serialize(serialized_credential))
            return false;
        if (! serialized_credential_list.append_value(serialized_credential))
            return false;
    }
    if (! serializer.set_value("verifiableCredential", serialized_credential_list))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::VerifiablePresentation::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::VerifiablePresentation::verify_schema(serialized_object))
        return false;

    serializedPresentation_ = serialized_object.get_string("serializedPresentation");
    ww::value::Object serialized_proof;
    if (! serialized_object.get_value("proof", serialized_proof))
        return false;
    if (! proof_.deserialize(serialized_proof))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::VerifiablePresentation::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(VERIFIABLE_PRESENTATION_SCHEMA);

    serialized_object.set(serializer);
    if (! serializer.set_string("serializedPresentation", serializedPresentation_.c_str()))
        return false;

    ww::value::Value serialized_proof;
    if (! proof_.serialize(serialized_proof))
        return false;
    if (! serializer.set_value("proof", serialized_proof))
        return false;

    return true;
}
