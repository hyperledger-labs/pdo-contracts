/* Copyright 2023 Intel Corporation
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

#pragma once
#include <string>
#include <vector>

#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "exchange/common/Common.h"

// All PDO contract identifiers are assumed to be of the form:
//     PDO://<ledger_url>/<contract_identifier>
// This identifier uniques identifies a PDO contract object and
// the ledger where its authenticity can be established.

// Identity Schema
//
// Provides a reference to a specific identity contract object
//
// Required fields include:
//    id -- a PDO contract identifier
// Optional fields include:
//    name -- a human readable name of the object, need not be unique or meaningful
//    description -- a human readable description of the object
//    identified_by -- a JSON object with properties to identify holder, definition TBD
#define IDENTITY_SCHEMA                         \
    "{"                                         \
        SCHEMA_KW(id, "")                       \
    "}"

namespace ww
{
namespace identity
{
    class Identity : public ww::exchange::SerializeableObject
    {
    private:
    public:
        std::string id_;
        std::string name_;
        std::string description_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, IDENTITY_SCHEMA);
        }

        bool deserialize(const ww::value::Object& credential);
        bool serialize(ww::value::Value& serialized_credential) const;
    };
}
}

// Identity Key Schema
//
// Provides information to identify a specific key in the context of
// an identity object.
//
// Required fields include:
//    id -- a PDO contract identifier
//    context_path -- a list of strings that contextualizes the identity
// Optional fields include:
//    name -- a human readable name of the object, need not be unique or meaningful
//    description -- a human readable description of the object
#define IDENTITY_KEY_SCHEMA                     \
    "{"                                         \
        SCHEMA_KW(id, "") ","                   \
        SCHEMA_KW(context_path, [ "" ])         \
    "}"

namespace ww
{
namespace identity
{
    class IdentityKey : public ww::exchange::SerializeableObject
    {
    private:
    public:
        std::string id_;
        std::vector<std::string> context_path_;
        std::string name_;
        std::string description_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, IDENTITY_KEY_SCHEMA);
        }

        bool deserialize(const ww::value::Object& credential);
        bool serialize(ww::value::Value& serialized_credential) const;

        IdentityKey(void) { }
        IdentityKey(const std::string id, const std::vector<std::string>& context_path) :
            id_(id), context_path_(context_path) { }
    };
}
}

// Claims Schema
//
// Provides a set of assertions about a subject
//
// Required fields include:
//    id -- the PDO contract identifier for the subject of the claim,
//    claims -- an object whose properties are attributes of the subject;
//        specific details of claims about the subject will be provided
//        at contract configuration time
#define CLAIMS_SCHEMA                                   \
    "{"                                                 \
        SCHEMA_KWS(subject, IDENTITY_SCHEMA) ","        \
        SCHEMA_KW(claims, {})                           \
    "}"

namespace ww
{
namespace identity
{
    class Claims : public ww::exchange::SerializeableObject
    {
    private:
    public:
        ww::identity::Identity subject_;
        ww::value::Object claims_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, CLAIMS_SCHEMA);
        }

        bool deserialize(const ww::value::Object& credential);
        bool serialize(ww::value::Value& serialized_credential) const;
    };
}
}

// Proof Schema
//
// There are many forms of proof that can accompany the credential, the
// proof is intended to verify the authenticity of the credential (that
// is, that the issuer really issued this credential).

// Required fields include:
//    type -- identify the signature method, for now always "ecdsa_secp384r1"
//    verificationMethod -- identifier plus an optional context [#context]
//    proofValue -- base64 encoded signature
// Optional fields include:
//    proofPurpose -- keyword that identifies what the proof claims
//    created -- time when the proof was createdxc
#define PROOF_SCHEMA                                            \
    "{"                                                         \
        SCHEMA_KW(type, "") ","                                 \
        SCHEMA_KWS(verificationMethod, IDENTITY_KEY_SCHEMA) "," \
        SCHEMA_KW(proofValue, "")                               \
    "}"

namespace ww
{
namespace identity
{
    class Proof : public ww::exchange::SerializeableObject
    {
    private:
    public:
        std::string type_;
        ww::identity::IdentityKey verificationMethod_;
        std::string proofValue_;
        std::string proofPurpose_;
        std::string created_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, PROOF_SCHEMA);
        }

        bool deserialize(const ww::value::Object& credential);
        bool serialize(ww::value::Value& serialized_credential) const;
    };
}
}

// Credential Schema
//
// Required fields include:
//    issuer -- identifier for the issuer of the credential, should be
//        verifiable by the signature in the proof section
//    credentialSubject -- specifies a claim, while strictly speaking a
//        verifiable credential may contain claims about a list of subjects,
//        we are limiting the number of subjects to one, though there may be
//        multiple claims about that subject

// Optional fields include:
//    name -- a human readable name of the credential, need not be unique or meaningful
//    description -- a human readable description of the credential
//    nonce -- base64 encoded number that serves to protect against replay attacks
//    issuanceDate -- data-time string, earliest time when claims are valid
//    expirationDate -- date-time string when the credential will expire
//    type -- list of type identifiers for type objects, VerifiableCredential is assumed
#define CREDENTIAL_SCHEMA                               \
    "{"                                                 \
        SCHEMA_KWS(issuer, IDENTITY_SCHEMA) ","         \
        SCHEMA_KWS(credentialSubject, CLAIMS_SCHEMA)    \
    "}"

namespace ww
{
namespace identity
{
    class Credential : public ww::exchange::SerializeableObject
    {
    private:
    public:
        ww::identity::Identity issuer_;
        ww::identity::Claims credentialSubject_;

        std::string name_;
        std::string description_;
        std::string nonce_;
        std::string issuanceDate_;
        std::string expirationDate_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, CREDENTIAL_SCHEMA);
        }

        bool deserialize(const ww::value::Object& credential);
        bool serialize(ww::value::Value& serialized_credential) const;
    };
}
}

// Verifiable Credential Schema
//
// To avoid the need for common JSON serialization schemes necessary for
// verifiable signatures, we are just passing a base64 encoding of the
// serialized credential that will be signed. This ensures that inconsistent
// serialization will not be an issue.
#define VERIFIABLE_CREDENTIAL_SCHEMA            \
    "{"                                         \
        SCHEMA_KW(serializedCredential, "") "," \
        SCHEMA_KWS(proof, PROOF_SCHEMA)         \
    "}"

namespace ww
{
namespace identity
{
    class VerifiableCredential : public ww::exchange::SerializeableObject
    {
    private:
        std::string serializedCredential_; // Base64 encoding of serialized credential

    public:
        ww::identity::Credential credential_;
        ww::identity::Proof proof_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, VERIFIABLE_CREDENTIAL_SCHEMA);
        }

        bool deserialize(const ww::value::Object& verifiable_credential);
        bool serialize(ww::value::Value& serialized_verifiable_credential) const;

        bool build(
            const ww::value::Object& credential,
            const ww::identity::IdentityKey& identity,
            const ww::types::ByteArray& extended_key_seed);
        bool check(
            const ww::types::ByteArray& extended_key_seed) const;
    };
}
}

// Presentation Schema
//
//
#define PRESENTATION_SCHEMA                                             \
    "{"                                                                 \
        SCHEMA_KWS(holder, IDENTITY_SCHEMA) ","                         \
        SCHEMA_KWS(verifiableCredential, "[" VERIFIABLE_CREDENTIAL_SCHEMA "]") \
    "}"

namespace ww
{
namespace identity
{
    class Presentation : public ww::exchange::SerializeableObject
    {
    private:
    public:
        ww::identity::Identity holder_;
        std::vector<ww::identity::VerifiableCredential> verifiableCredential_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, PRESENTATION_SCHEMA);
        }

        bool deserialize(const ww::value::Object& verifiable_credential);
        bool serialize(ww::value::Value& serialized_verifiable_credential) const;
    };
}
}

// Verifiable Presentation Schema
//
//
#define VERIFIABLE_PRESENTATION_SCHEMA                  \
    "{"                                                 \
        SCHEMA_KW(serializedPresentation, "") ","       \
        SCHEMA_KWS(proof, PROOF_SCHEMA)                 \
    "}"

namespace ww
{
namespace identity
{
    class VerifiablePresentation : public ww::exchange::SerializeableObject
    {
    private:
        std::string serializedPresentation_;
    public:
        ww::identity::Presentation presentation_;
        ww::identity::Proof proof_;

        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, VERIFIABLE_PRESENTATION_SCHEMA);
        }

        bool deserialize(const ww::value::Object& verifiable_credential);
        bool serialize(ww::value::Value& serialized_verifiable_credential) const;
    };
}
}
