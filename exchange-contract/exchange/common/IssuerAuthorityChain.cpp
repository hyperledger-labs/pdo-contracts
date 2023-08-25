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

#include "Common.h"
#include "IssuerAuthorityChain.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::IssuerAuthorityChain
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
ww::exchange::IssuerAuthorityChain::IssuerAuthorityChain(
    const std::string& asset_type_identifier,
    const std::string& vetting_organization_verifying_key) :
    asset_type_identifier_(asset_type_identifier),
    vetting_organization_verifying_key_(vetting_organization_verifying_key)
{
    authority_chain_.clear();
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthorityChain::deserialize(
    const ww::value::Object& chain)
{
    if (! ww::exchange::IssuerAuthorityChain::verify_schema(chain))
        return false;

    asset_type_identifier_ = chain.get_string("asset_type_identifier");
    vetting_organization_verifying_key_ = chain.get_string("vetting_organization_verifying_key");

    ww::value::Array authorities;
    if (! chain.get_value("authority_chain", authorities))
        return false;

    size_t count = authorities.get_count();
    for (size_t index = 0; index < count; index++)
    {
        ww::value::Object authority_object;
        if (! authorities.get_value(index, authority_object))
            return false;

        ww::exchange::IssuerAuthority authority;
        if (! authority.deserialize(authority_object))
            return false;

        authority_chain_.push_back(authority);
    }

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthorityChain::serialize(
    ww::value::Value& serialized_chain) const
{
    ww::value::Structure chain(ISSUER_AUTHORITY_CHAIN_SCHEMA);
    if (! chain.set_string("asset_type_identifier", asset_type_identifier_.c_str()))
        return false;
    if (! chain.set_string("vetting_organization_verifying_key", vetting_organization_verifying_key_.c_str()))
        return false;

    ww::value::Array authority_chain;
    for (size_t index = 0; index < authority_chain_.size(); index++)
    {
        ww::value::Value serialized_authority;
        if (! authority_chain_[index].serialize(serialized_authority))
            return false;
        if (! authority_chain.append_value(serialized_authority))
            return false;
    }

    if (! chain.set_value("authority_chain", authority_chain))
        return false;

    serialized_chain.set(chain);
    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthorityChain::get_issuer_identity(
    std::string& issuer_verifying_key) const
{
    if (authority_chain_.empty())
        return false;

    const ww::exchange::IssuerAuthority& issuer = authority_chain_.back();
    issuer_verifying_key = issuer.authorized_issuer_verifying_key_;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthorityChain::add_issuer_authority(
    const ww::exchange::IssuerAuthority& value)
{
    authority_chain_.push_back(value);
    return true;
}

// -----------------------------------------------------------------
// validate -- verify that the chain establishes the authority of the
// provided issuer verifying key
// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthorityChain::validate_issuer_key(
    const std::string& issuer_verifying_key) const
{
    std::string verifying_key = vetting_organization_verifying_key_;

    for (size_t index = 0; index < authority_chain_.size(); index++)
    {
        if (! authority_chain_[index].validate(verifying_key, asset_type_identifier_))
            return false;       // the authority itself is invalid

        // the key in this authority is used to verify the next authority
        verifying_key = authority_chain_[index].authorized_issuer_verifying_key_;
        if (issuer_verifying_key == verifying_key)
            return true;
    }

    return false;
}

// -----------------------------------------------------------------
bool ww::exchange::IssuerAuthorityChain::add_dependencies_to_response(Response& rsp) const
{
    for (size_t index = 0; index < authority_chain_.size(); index++)
    {
        if (! authority_chain_[index].state_reference_.add_to_response(rsp))
            return false;
    }

    return true;
}
