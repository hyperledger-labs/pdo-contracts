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

#include "Util.h"
#include "Value.h"

#include "exchange/common/Common.h"
#include "identity/crypto/PrivateKey.h"


#define VERIFYING_CONTEXT_SCHEMA                \
    "{"                                         \
        SCHEMA_KW(public_key, "") ","           \
        SCHEMA_KW(chain_code, "" )              \
    "}"

namespace ww
{
namespace identity
{
    // -----------------------------------------------------------------
    class VerifyingContext : public ww::identity::BaseVerifyingContext
    {
    public:
        bool is_valid(void) const;

        bool verify_signature(
            const std::vector<std::string>& context_path,
            const ww::types::ByteArray& message,
            const ww::types::ByteArray& signature) const override;

        bool generate_key(
            const std::vector<std::string>& context_path,
            pdo_contracts::crypto::signing::PublicKey& public_key,
            ww::types::ByteArray& chain_code) const;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, SIGNING_CONTEXT_SCHEMA);
        }

        bool deserialize(const ww::value::Object& serialized_context) override;
        bool serialize(ww::value::Value& serialized_context) const override;

        // Constructors
        VerifyingContext(void) { };

        VerifyingContext(const ww::value::Object& serialized_context) {
            deserialize(serialized_context);
        };
    };

#if 0
    class VerifyingContext : public ww::exchange::SerializeableObject
    {
    protected:
        std::string public_key_;                    // PEM encoded ECDSA public key
        std::string chain_code_;                    // base64 encoded representation of 48 byte random array

    public:
        bool verify_signature(
            const std::vector<std::string>& context_path,
            const ww::types::ByteArray& message,
            const ww::types::ByteArray& signature) const;

        static bool generate_key(
            const std::string& encoded_public_key, // PEM encoded public key
            const std::string& encoded_chain_code, // Base64 encoded chain code
            const std::vector<std::string>& context_path,
            std::string& derived_public_key); // PEM encoded public key returned

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, VERIFYING_CONTEXT_SCHEMA);
        }

        bool deserialize(const ww::value::Object& request);
        bool serialize(ww::value::Value& serialized_request) const;
        bool is_valid(void) const;

        VerifyingContext(const ww::value::Object& context)
        {
            deserialize(context);
        };

        VerifyingContext(const std::string& public_key, const std::string& chain_code)
            : public_key_(public_key), chain_code_(chain_code)
        { };

        VerifyingContext(void) : VerifyingContext("", "")
        { };
    };
#endif
}; // identity
}  // ww
