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
#include "identity/common/SigningContext.h"
#include "identity/common/SigningContextManager.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::SigningContext
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
// -----------------------------------------------------------------
static bool deserialize_timestamp(
    const char* input_timestamp,
    std::string& output_timestamp)
{
    if (input_timestamp == NULL)
        return false;

    // this is just a placeholder, will check format in the future
    output_timestamp.assign(input_timestamp);
    return true;
}

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

    // Required fields
    const char *id = serialized_object.get_string("id");
    if (id == NULL)
        return false;
    id_.assign(id);

    // Optional fields
    const char *name = serialized_object.get_string("name");
    if (name != NULL)
        name_.assign(name);

    const char *description = serialized_object.get_string("description");
    if (description != NULL)
        description_.assign(description);

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Identity::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(IDENTITY_SCHEMA);

    // Required fields
    if (! serializer.set_string("id", id_.c_str()))
        return false;

    // Optional fields
    if (! name_.empty())
        if (! serializer.set_string("name", name_.c_str()))
            return false;

    if (! description_.empty())
        if (! serializer.set_string("description", description_.c_str()))
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

    // Required fields
    const char *id = serialized_object.get_string("id");
    if (id == NULL)
        return false;
    id_.assign(id);

    ww::value::Array context_array;
    if (! serialized_object.get_value("context_path", context_array))
        return false;

    if (! deserialize_context_path(context_array, context_path_))
        return false;

    // Optional fields
    const char *name = serialized_object.get_string("name");
    if (name != NULL)
        name_.assign(name);

    const char *description = serialized_object.get_string("description");
    if (description != NULL)
        description_.assign(description);

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::IdentityKey::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(IDENTITY_KEY_SCHEMA);
    if (! serializer.set_string("id", id_.c_str()))
        return false;

    // Required fields
    ww::value::Array context_array;
    if (! serialize_context_path(context_path_, context_array))
        return false;

    if (! serializer.set_value("context_path", context_array))
        return false;

    // Optional fields
    if (! name_.empty())
        if (! serializer.set_string("name", name_.c_str()))
            return false;

    if (! description_.empty())
        if (! serializer.set_string("description", description_.c_str()))
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

    ww::value::Object subject;
    if (! serialized_object.get_value("subject", subject))
        return false;
    if (! subject_.deserialize(subject))
        return false;

    if (! serialized_object.get_value("claims", claims_))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Claims::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(CLAIMS_SCHEMA);

    ww::value::Object serialized_subject;
    if (! subject_.serialize(serialized_subject))
        return false;
    if (! serializer.set_value("subject", serialized_subject))
        return false;

    if (! serializer.set_value("claims", claims_))
        return false;

    serialized_object.set(serializer);
    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Proof::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::identity::Proof::verify_schema(serialized_object))
        return false;

    // Required fields
    const char *type = serialized_object.get_string("type");
    if (type == NULL)
        return false;
    type_.assign(type);

    ww::value::Structure serialized_identity_key(IDENTITY_KEY_SCHEMA);
    if (! serialized_object.get_value("verificationMethod", serialized_identity_key))
        return false;
    if (! verificationMethod_.deserialize(serialized_identity_key))
        return false;

    const char *proofValue = serialized_object.get_string("proofValue");
    if (proofValue == NULL)
        return false;
    proofValue_.assign(proofValue);

    // Optional fields
    const char *created = serialized_object.get_string("created");
    if (created != NULL)
        if (! deserialize_timestamp(created, created_))
            return false;

    const char *proofPurpose = serialized_object.get_string("proofPurpose");
    if (proofPurpose != NULL)
        proofPurpose_.assign(proofPurpose); // TBD: verify that this is one of the enums

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::Proof::serialize(ww::value::Value& serialized_object) const
{
    ww::value::Structure serializer(PROOF_SCHEMA);

    // Required fields
    if (! serializer.set_string("type", type_.c_str()))
        return false;

    ww::value::Structure serialized_identity_key(IDENTITY_KEY_SCHEMA);
    if (! verificationMethod_.serialize(serialized_identity_key))
        return false;
    if (! serializer.set_value("verificationMethod", serialized_identity_key))
        return false;

    if (! serializer.set_string("proofValue", proofValue_.c_str()))
        return false;

    // Optional fields
    if (! created_.empty())
        if (! serializer.set_string("created", created_.c_str()))
            return false;

    if (! proofPurpose_.empty())
        if (! serializer.set_string("proofPurpose", proofPurpose_.c_str()))
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

    // Optional fields
    const char *name = serialized_object.get_string("name");
    if (name != NULL)
        name_.assign(name);

    const char *description = serialized_object.get_string("description");
    if (description != NULL)
        description_.assign(description);

    const char *nonce = serialized_object.get_string("nonce");
    if (nonce != NULL)
        nonce_.assign(nonce);

    const char *issuanceDate = serialized_object.get_string("issuanceDate");
    if (issuanceDate != NULL)
        if (! deserialize_timestamp(issuanceDate, issuanceDate_))
            return false;

    const char *expirationDate = serialized_object.get_string("expirationDate");
    if (expirationDate != NULL)
        if (! deserialize_timestamp(expirationDate, expirationDate_))
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

    // Optional fields
    if (! name_.empty())
        if (! serializer.set_string("name", name_.c_str()))
            return false;

    if (! description_.empty())
        if (! serializer.set_string("description", description_.c_str()))
            return false;

    if (! nonce_.empty())
        if (! serializer.set_string("nonce", nonce_.c_str()))
            return false;

    if (! issuanceDate_.empty())
        if (! serializer.set_string("issuanceDate", issuanceDate_.c_str()))
            return false;

    if (! expirationDate_.empty())
        if (! serializer.set_string("expirationDate", expirationDate_.c_str()))
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

    const char *serializedCredential = serialized_object.get_string("serializedCredential");
    if (serializedCredential == NULL)
        return false;
    serializedCredential_.assign(serializedCredential);

    // the serialized credential is b64 encoded and must be converted
    // to a string for deserialization
    {
        ww::types::ByteArray decoded_credential_ba;
        if (! ww::crypto::b64_decode(serializedCredential_, decoded_credential_ba))
            return false;
        const std::string decoded_credential = ww::types::ByteArrayToString(decoded_credential_ba);
        if (! credential_.deserialize_string(decoded_credential))
            return false;
    }

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
bool ww::identity::VerifiableCredential::build(
    const ww::value::Object& credential,
    const ww::identity::IdentityKey& identity,
    const ww::types::ByteArray& extended_key_seed)
{
    // De-serializing the input will check for a schema match and
    // will unpack the expected fields
    if (! credential_.deserialize(credential))
        return false;

    // Re-serializing the credential will ensure that the format contains
    // no additional information beyond the credential fields
    std::string serialized_credential;
    if (! credential_.serialize_string(serialized_credential))
        return false;

    // Base64 encode the serialized credential and save it in the
    // serializedCredential_ field
    ww::types::ByteArray serialized_credential_ba(serialized_credential.begin(), serialized_credential.end());
    if (! ww::crypto::b64_encode(serialized_credential_ba, serializedCredential_))
        return false;

    // Sign the serialized credential; in this case we are signing the base64 encoding
    // of the serialized credential, this is not the only approach that would be valid
    // but it does represent a fairly standard way of signing JSON
    // see https://datatracker.ietf.org/doc/rfc7515/
    ww::types::ByteArray signature_ba;
    ww::types::ByteArray message_ba(serializedCredential_.begin(), serializedCredential_.end());
    if (! ww::identity::SigningContext::sign_message(extended_key_seed, identity.context_path_, message_ba, signature_ba))
        return false;

    // Convert the signature to base64
    std::string b64_signature;
    if (! ww::crypto::b64_encode(signature_ba, b64_signature))
        return false;

    // Finally save all the information into the verifiable credential
    proof_.type_ = "ecdsa_secp384r1";
    proof_.verificationMethod_ = identity;
    proof_.proofValue_ = b64_signature;
    proof_.proofPurpose_ = "assertion";

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::VerifiableCredential::check(const ww::types::ByteArray& extended_key_seed) const
{
    // The signature was computed over the base64 encoded credential so we
    // do not need to decode the credential before checking the signature
    ww::types::ByteArray message(serializedCredential_.begin(), serializedCredential_.end());

    ww::types::ByteArray signature;
    if (! ww::crypto::b64_decode(proof_.proofValue_, signature))
        return false;

    return ww::identity::SigningContext::verify_signature(
        extended_key_seed, proof_.verificationMethod_.context_path_, message, signature);
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

    const char* serializedPresentation = serialized_object.get_string("serializedPresentation");
    if (serializedPresentation == NULL)
        return false;
    serializedPresentation_.assign(serializedPresentation);

    // the serialized presentation is b64 encoded and must be converted
    // to a string for deserialization
    {
        ww::types::ByteArray decoded_presentation_ba;
        if (! ww::crypto::b64_decode(serializedPresentation_, decoded_presentation_ba))
            return false;
        const std::string decoded_presentation = ww::types::ByteArrayToString(decoded_presentation_ba);
        if (! presentation_.deserialize_string(decoded_presentation))
            return false;
    }

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
