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

#include "Types.h"
#include "Value.h"

#include "Asset.h"
#include "Common.h"

#define LEDGER_ENTRY_SCHEMA                     \
    "{"                                         \
        SCHEMA_KWS(asset, ASSET_SCHEMA) ","     \
        "\"escrow_list\": [ " ASSET_SCHEMA " ]" \
    "}"

namespace ww
{
namespace exchange
{

    class LedgerEntry : public ww::exchange::SerializeableObject
    {

    public:
        ww::exchange::Asset asset_;
        std::vector<ww::exchange::Asset> escrow_list_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, LEDGER_ENTRY_SCHEMA);
        }

        bool deserialize(const ww::value::Object& serialized_object);
        bool serialize(ww::value::Value& serialized_value) const;

        // LedgerEntry methods

        bool asset_is_escrowed(
            const std::string& escrow_agent_identity) const;

        bool get_escrowed_asset(
            const std::string& escrow_agent_identity,
            ww::exchange::Asset& value) const;

        bool escrow(
            const std::string& escrow_agent_identity,
            const uint32_t count = 0);

        bool release_escrow(
            const std::string& escrow_agent_identity,
            const uint32_t count = 0);

        bool transfer_escrow(
            const std::string& escrow_agent_identity,
            const uint32_t count = 0);

        LedgerEntry(const ww::exchange::Asset& asset);
        LedgerEntry(void);
    };

};
}
