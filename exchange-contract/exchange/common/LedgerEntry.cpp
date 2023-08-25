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

#include "Asset.h"
#include "Common.h"
#include "LedgerEntry.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::LedgerEntry
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
ww::exchange::LedgerEntry::LedgerEntry(void)
{}

// -----------------------------------------------------------------
ww::exchange::LedgerEntry::LedgerEntry(const ww::exchange::Asset& asset) :
    asset_(asset)
{
}

// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::deserialize(const ww::value::Object& serialized_object)
{
    if (! ww::exchange::LedgerEntry::verify_schema(serialized_object))
        return false;

    ww::value::Structure asset_object(ASSET_SCHEMA);
    if (! serialized_object.get_value("asset", asset_object))
    {
        CONTRACT_SAFE_LOG(3, "deserialize asset in LedgerEntry");
        return false;
    }

    if (! asset_.deserialize(asset_object))
        return false;

    ww::value::Array escrow_array;
    if (! serialized_object.get_value("escrow_list", escrow_array))
        return false;

    size_t count = escrow_array.get_count();
    for (size_t index = 0; index < count; index++)
    {
        if (! escrow_array.get_value(index, asset_object))
            return false;

        ww::exchange::Asset asset;
        if (! asset.deserialize(asset_object))
            return false;

        escrow_list_.push_back(asset);
    }

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::serialize(ww::value::Value& serialized_value) const
{
    ww::value::Structure entry_object(LEDGER_ENTRY_SCHEMA);

    ww::value::Value serialized_asset;
    if (! asset_.serialize(serialized_asset))
        return false;
    if (! entry_object.set_value("asset", serialized_asset))
    {
        CONTRACT_SAFE_LOG(3, "serialize ledger entry, no asset");
        return false;
    }

    ww::value::Array escrow_array;
    for (auto& asset : escrow_list_)
    {
        if (! asset.serialize(serialized_asset))
            return false;
        if (! escrow_array.append_value(serialized_asset))
            return false;
    }

    if (! entry_object.set_value("escrow_list", escrow_array))
        return false;

    serialized_value.set(entry_object);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::asset_is_escrowed(
    const std::string& escrow_agent_identity) const
{
    for (auto& asset : escrow_list_)
    {
        if (asset.escrow_agent_identity_ == escrow_agent_identity)
            return true;
    }

    return false;
}

// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::get_escrowed_asset(
    const std::string& escrow_agent_identity,
    ww::exchange::Asset& value) const
{
    for (auto& asset : escrow_list_)
    {
        if (asset.escrow_agent_identity_ == escrow_agent_identity)
        {
            value = asset;
            return true;
        }
    }

    return false;
}

// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::escrow(
    const std::string& escrow_agent_identity,
    const uint32_t count)
{
    uint32_t transfer = (count == 0 ? asset_.count_ : count);
    if (asset_.count_ < transfer)
        return false;

    asset_.count_ = asset_.count_ - transfer;

    // add a new asset if we don't have an escrow
    ww::exchange::Asset asset(asset_);
    asset.count_ = transfer;
    if (! asset.escrow(escrow_agent_identity))
        return false;
    escrow_list_.push_back(asset);

    return true;
}

// -----------------------------------------------------------------
// NOTE: this does not prevent a replay of a release or claim, that
// policy must be implemented at a higher level
// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::release_escrow(
    const std::string& escrow_agent_identity,
    const uint32_t count)
{
    for (auto it = escrow_list_.begin(); it != escrow_list_.end(); ++it)
    {
        if ((*it).escrow_agent_identity_ == escrow_agent_identity)
        {
#ifdef SUPPPORT_PARTIAL_ESCROW
            uint32_t transfer = (count == 0 ? (*it).count_ : count);
            if ((*it).count_ < transfer)
                return false;
#else
            if (count != 0 && count != (*it).count_)
            {
                CONTRACT_SAFE_LOG(3, "partial release not supported");
                return false;
            }

            uint32_t transfer = (*it).count_;
#endif

            // remove the assets from the escrow'ed pool
            (*it).count_ = (*it).count_ - transfer;

            // and put them back into the asset pool
            asset_.count_ = asset_.count_ + transfer;

            // and remove the escrow from the list if there is nothing
            // left to the escrow
            if ((*it).count_ == 0)
                //escrow_list_.erase(escrow_list_.begin() + index);
                escrow_list_.erase(it);

            return true;
        }
    }

    return false;
}

// -----------------------------------------------------------------
// NOTE: this does not prevent a replay of a release or claim, that
// policy must be implemented at a higher level
// -----------------------------------------------------------------
bool ww::exchange::LedgerEntry::transfer_escrow(
    const std::string& escrow_agent_identity,
    const uint32_t count)
{
    for (auto it = escrow_list_.begin(); it != escrow_list_.end(); ++it)
    {
        if ((*it).escrow_agent_identity_ == escrow_agent_identity)
        {
#ifdef SUPPPORT_PARTIAL_ESCROW
            uint32_t transfer = (count == 0 ? (*it).count_ : count);
            if ((*it).count_ < transfer)
                return false;
#else
            if (count != 0 && count != (*it).count_)
            {
                CONTRACT_SAFE_LOG(3, "partial claim not supported");
                return false;
            }

            uint32_t transfer = (*it).count_;
#endif
            // remove the assets from the escrow'ed pool
            (*it).count_ = (*it).count_ - transfer;

            // and remove the escrow from the list if there is nothing
            // left to the escrow
            if ((*it).count_ == 0)
                escrow_list_.erase(it);

            return true;
        }
    }

    return false;
}
