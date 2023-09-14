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

#include "Response.h"
#include "Value.h"

#include "IssuerAuthority.h"

#define ISSUER_AUTHORITY_CHAIN_SCHEMA                           \
    "{"                                                         \
        SCHEMA_KW(asset_type_identifier,"") ","                 \
        SCHEMA_KW(vetting_organization_verifying_key,"") ","    \
        "\"authority_chain\": []"                               \
    "}"

namespace ww
{
namespace exchange
{

    class IssuerAuthorityChain : public ww::exchange::SerializeableObject
    {
    public:
        std::string asset_type_identifier_;
        std::string vetting_organization_verifying_key_;
        std::vector<ww::exchange::IssuerAuthority> authority_chain_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, ISSUER_AUTHORITY_CHAIN_SCHEMA);
        }

        bool deserialize(const ww::value::Object& chain);
        bool serialize(ww::value::Value& serialized_chain) const;

        // IssuerAuthorityChain methods
        bool add_issuer_authority(const ww::exchange::IssuerAuthority& value);
        bool get_issuer_identity(std::string& issuer_identity) const;

        bool validate_issuer_key(const std::string& issuer_verifying_key) const;
        bool add_dependencies_to_response(Response& rsp) const;

        IssuerAuthorityChain(
            const std::string& asset_type_identifier = "",
            const std::string& vetting_organization_verifying_key = "");
    };

};
}
