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
#include "WasmExtensions.h"

#include "Asset.h"
#include "Common.h"
#include "IssuerAuthorityChain.h"
#include "StateReference.h"

#define AUTHORITATIVE_ASSET_SCHEMA                                      \
    "{"                                                                 \
        SCHEMA_KWS(asset, ASSET_SCHEMA) ","                             \
        SCHEMA_KWS(issuer_state_reference, STATE_REFERENCE_SCHEMA) ","  \
        SCHEMA_KWS(issuer_authority_chain, ISSUER_AUTHORITY_CHAIN_SCHEMA) "," \
        SCHEMA_KW(issuer_identity,"") ","                               \
        SCHEMA_KW(issuer_signature,"")                                  \
    "}"

namespace ww
{
namespace exchange
{

    class AuthoritativeAsset : public ww::exchange::SerializeableObject
    {
    private:
        bool serialize_for_signing(std::string& serialized) const;

    public:
        ww::exchange::Asset asset_;
        ww::value::StateReference issuer_state_reference_;
        ww::exchange::IssuerAuthorityChain issuer_authority_chain_;
        std::string issuer_identity_;
        std::string encoded_signature_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, AUTHORITATIVE_ASSET_SCHEMA);
        }

        bool deserialize(const ww::value::Object& request);
        bool serialize(ww::value::Value& serialized_request) const;

        // AuthoritativeAsset methods
        bool sign(const std::string& authorizing_signing_key);
        bool verify_signature(const std::string& authorizing_verifying_key) const;
        bool validate(void) const;

        bool get_issuer_identity(std::string& issuer_verifying_key) const;

        AuthoritativeAsset(void);
    };

};
}
