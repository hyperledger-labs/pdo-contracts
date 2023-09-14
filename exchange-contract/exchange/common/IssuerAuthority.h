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

#pragma once

#include <string>

#include "Value.h"

#include "Common.h"
#include "StateReference.h"

#define ISSUER_AUTHORITY_SCHEMA                                         \
    "{"                                                                 \
        SCHEMA_KW(authorized_issuer_verifying_key,"") ","               \
        SCHEMA_KW(authorizing_signature,"") ","                         \
        SCHEMA_KWS(issuer_state_reference, STATE_REFERENCE_SCHEMA)      \
    "}"

namespace ww
{
namespace exchange
{

    class IssuerAuthority : public ww::exchange::SerializeableObject
    {
    private:
        bool serialize_for_signing(
            const std::string& asset_type_identifier,
            std::string& serialized) const;

    public:
        std::string authorized_issuer_verifying_key_;
        std::string authorizing_signature_; /* b64 encoded signature */
        ww::value::StateReference state_reference_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, ISSUER_AUTHORITY_SCHEMA);
        }

        bool deserialize(const ww::value::Object& chain);
        bool serialize(ww::value::Value& serialized_chain) const;

        // IssuerAuthority methods
        bool sign(
            const std::string& authorizing_signing_key,
            const std::string& asset_type_identifier);

        bool verify_signature(
            const std::string& authorizing_verifying_key,
            const std::string& asset_type_identifier) const;

        bool validate(
            const std::string& authorizing_verifying_key,
            const std::string& asset_type_identifier) const;

        IssuerAuthority(void);

        IssuerAuthority(
            const std::string& issuer_verifying_key,
            const ww::value::StateReference& reference);

    };

};
}
