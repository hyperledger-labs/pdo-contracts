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

#include "AssetRequest.h"
#include "Common.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::AssetRequest
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
ww::exchange::AssetRequest::AssetRequest(void) :
    asset_type_identifier_(""),
    count_(0),
    owner_identity_(""),
    issuer_verifying_key_("")
{
}

// -----------------------------------------------------------------
bool ww::exchange::AssetRequest::deserialize(
    const ww::value::Object& request)
{
    if (! ww::exchange::AssetRequest::verify_schema(request))
        return false;

    asset_type_identifier_ = request.get_string("asset_type_identifier");
    count_ = (unsigned int)request.get_number("count");
    owner_identity_ = request.get_string("owner_identity");
    issuer_verifying_key_ = request.get_string("issuer_verifying_key");

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AssetRequest::serialize(
    ww::value::Value& serialized_request) const
{
    ww::value::Structure request(ASSET_REQUEST_SCHEMA);

    if (! request.set_string("asset_type_identifier", asset_type_identifier_.c_str()))
        return false;
    if (! request.set_number("count", count_))
        return false;
    if (! request.set_string("owner_identity", owner_identity_.c_str()))
        return false;
    if (! request.set_string("issuer_verifying_key", issuer_verifying_key_.c_str()))
        return false;

    serialized_request.set(request);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::AssetRequest::check_for_match(
    const ww::exchange::AuthoritativeAsset& authoritative_asset) const
{
    // check the asset type requirement, this is a mandatory check
    if (authoritative_asset.asset_.asset_type_identifier_ != asset_type_identifier_)
        return false;

    // check the count, this is a mandatory check
    if (authoritative_asset.asset_.count_ < count_)
        return false;

    // check to see if the requested owner matches, optional check
    if (owner_identity_ != "")
    {
        if (authoritative_asset.asset_.owner_identity_ != owner_identity_)
            return false;
    }

    // check to see if the requested issuer key is in the chain of authorizations, optional check
    if (issuer_verifying_key_ != "")
    {
        if (issuer_verifying_key_ != authoritative_asset.issuer_authority_chain_.vetting_organization_verifying_key_)
        {
            if (! authoritative_asset.issuer_authority_chain_.validate_issuer_key(issuer_verifying_key_))
                return false;
        }
    }

    return true;
}
