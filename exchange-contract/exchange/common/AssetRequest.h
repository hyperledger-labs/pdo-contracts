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

#include "AuthoritativeAsset.h"
#include "Common.h"

#define ASSET_REQUEST_SCHEMA "{"                \
    SCHEMA_KW(asset_type_identifier,"") ","     \
    SCHEMA_KW(count,0) ","                      \
    SCHEMA_KW(owner_identity,"") ","            \
    SCHEMA_KW(issuer_verifying_key,"")          \
    " } "

namespace ww
{
namespace exchange
{

    class AssetRequest : public ww::exchange::SerializeableObject
    {
    public:
        std::string asset_type_identifier_;
        std::string issuer_verifying_key_;
        unsigned int count_;
        std::string owner_identity_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, ASSET_REQUEST_SCHEMA);
        }

        bool deserialize(const ww::value::Object& request);
        bool serialize(ww::value::Value& serialized_request) const;

        // AssetRequest methods
        bool check_for_match(const ww::exchange::AuthoritativeAsset& authoritative_asset) const;

        AssetRequest(void);
    };

};
}
