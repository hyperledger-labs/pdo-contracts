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
        SCHEMA_KW(prefix_path, [ "" ]) ","     \
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
    protected:
        bool generate_keys(
            pdo_contracts::crypto::signing::PublicKey& public_key,
            ww::types::ByteArray& chain_code) const;

        std::vector<std::string> prefix_path_; // path to the key relative to the root

    public:
        bool initialize(
            const std::vector<std::string>& prefix_path,
            const std::string& public_key,
            const std::string& chain_code);

        bool extend_context_path(const std::vector<std::string>& context_path);

        bool verify_signature(
            const ww::types::ByteArray& message,
            const ww::types::ByteArray& signature) const override;

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

}; // identity
}  // ww
