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

#include <string>

#include "Types.h"
#include "WasmExtensions.h"

#include "LedgerStore.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// CLASS: LedgerStore
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bool ww::exchange::LedgerStore::exists(const std::string& owner_identity) const
{
    std::string serialized_entry;
    return get(owner_identity, serialized_entry);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bool ww::exchange::LedgerStore::get_entry(
    const std::string& owner_identity,
    ww::exchange::LedgerEntry& value) const
{
    std::string serialized_entry;
    if (! get(owner_identity, serialized_entry))
        return false;

    if (! value.deserialize_string(serialized_entry))
        return false;

    return true;
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bool ww::exchange::LedgerStore::set_entry(
    const std::string& owner_identity,
    const ww::exchange::LedgerEntry& value) const
{
    std::string serialized_entry;
    if (! value.serialize_string(serialized_entry))
        return false;

    return set(owner_identity, serialized_entry);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bool ww::exchange::LedgerStore::add_entry(
    const std::string& owner_identity,
    const std::string& asset_type_identifier,
    uint32_t count) const
{
    ww::exchange::Asset asset(owner_identity, asset_type_identifier, count);
    ww::exchange::LedgerEntry entry(asset);

    return set_entry(owner_identity, entry);
}
