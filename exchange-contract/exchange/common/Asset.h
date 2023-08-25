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

#define ASSET_SCHEMA "{"                   \
    SCHEMA_KW(asset_type_identifier,"") ","     \
    SCHEMA_KW(count,0) ","                      \
    SCHEMA_KW(owner_identity,"") ","            \
    SCHEMA_KW(escrow_agent_identity,"") ","     \
    SCHEMA_KW(escrow_identifier,"")             \
    "}"

namespace ww
{
namespace exchange
{
    class Asset : public ww::exchange::SerializeableObject
    {
    private:
        bool serialize_for_escrow_signing(
            const ww::value::StateReference& escrow_agent_state_reference,
            std::string& serialized) const;

    public:
        unsigned int count_;
        std::string asset_type_identifier_;
        std::string owner_identity_;
        std::string escrow_agent_identity_;
        std::string escrow_identifier_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, ASSET_SCHEMA);
        }

        bool deserialize(const ww::value::Object& asset);
        bool serialize(ww::value::Value& serialized_asset) const;

        // Asset methods
        bool escrow(
            const std::string& escrow_agent_identity);

        bool verify_escrow_signature(
            const ww::value::StateReference& escrow_agent_state_reference,
            const std::string& encoded_signature) const;

        bool sign_for_escrow(
            const ww::value::StateReference& escrow_agent_state_reference,
            const std::string& escrow_agent_signing_key,
            std::string& encoded_signature) const;

        Asset(
            const std::string& owner_identity = "",
            const std::string& asset_type_identifier = "",
            uint32_t count = 0);
    };

};  // namespace exchange
}  // namespace ww
