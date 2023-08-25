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

#include <stddef.h>
#include <stdint.h>
#include <string>

#include "Dispatch.h"

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "exchange/asset_type.h"
#include "contract/base.h"

static KeyValueStore asset_type_store("asset_type_store");

const std::string md_asset_type_id_key("asset_type_identifier");
const std::string md_description_key("description");
const std::string md_link_key("link");
const std::string md_name_key("name");

// -----------------------------------------------------------------
// METHOD: initialize_contract
//   contract initialization method
//
// JSON PARAMETERS:
//   none
//
// RETURNS:
//   true if successfully initialized
// -----------------------------------------------------------------
bool ww::exchange::asset_type::initialize_contract(const Environment& env)
{
    // ---------- initialize the base contract ----------
    if (! ww::contract::base::initialize_contract(env))
        return false;

    // ---------- save the type identifier ----------
    const std::string asset_type_identifier(env.contract_id_);
    if (! asset_type_store.set(md_asset_type_id_key, asset_type_identifier))
        return false;

    return true;
}

// -----------------------------------------------------------------
// METHOD: initialize
//   set the basic information for the asset type
//
// JSON PARAMETERS:
//   description -- string description of the type
//   link -- URL for more information
//   name -- short handle for the asset type
//
// RETURNS:
//   true if successfully initialized
// -----------------------------------------------------------------
bool ww::exchange::asset_type::initialize(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(AT_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // save the description
    const std::string description(msg.get_string("description"));
    ASSERT_SUCCESS(rsp, asset_type_store.set(md_description_key, description),
                   "failed to store the description");

    // save the link
    const std::string link(msg.get_string("link"));
    ASSERT_SUCCESS(rsp, asset_type_store.set(md_link_key, link),
                   "failed to store the link");

    // save the name
    const std::string name(msg.get_string("name"));
    ASSERT_SUCCESS(rsp, asset_type_store.set(md_name_key, name),
                   "failed to store the name");

    // Mark as initialized
    ASSERT_SUCCESS(rsp, ww::contract::base::mark_initialized(), "initialization failed");

    // ---------- RETURN ----------
    return rsp.success(true);
}

// -----------------------------------------------------------------
// METHOD: get_asset_type_identifier
//   set asset type identifier
//
// JSON PARAMETERS:
//   None
//
// RETURNS:
//   asset type identifier (the contract id)
// -----------------------------------------------------------------
bool ww::exchange::asset_type::get_asset_type_identifier(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    std::string asset_type_identifier;
    ASSERT_SUCCESS(rsp, asset_type_store.get(md_asset_type_id_key, asset_type_identifier),
                   "contract state corrupted, no asset type identifier");

    ww::value::String v(asset_type_identifier.c_str());
    return rsp.value(v, false);
}

// -----------------------------------------------------------------
// METHOD: get_description
//   set asset type description
//
// JSON PARAMETERS:
//   None
//
// RETURNS:
//   asset type description
// -----------------------------------------------------------------
bool ww::exchange::asset_type::get_description(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    std::string description;
    ASSERT_SUCCESS(rsp, asset_type_store.get(md_description_key, description),
                   "contract state corrupted, no description");

    ww::value::String v(description.c_str());
    return rsp.value(v, false);
}

// -----------------------------------------------------------------
// METHOD: get_link
//   set asset type link
//
// JSON PARAMETERS:
//   None
//
// RETURNS:
//   asset type link
// -----------------------------------------------------------------
bool ww::exchange::asset_type::get_link(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    std::string link;
    ASSERT_SUCCESS(rsp, asset_type_store.get(md_link_key, link),
                   "contract state corrupted, no link");

    ww::value::String v(link.c_str());
    return rsp.value(v, false);
}

// -----------------------------------------------------------------
// METHOD: get_name
//   set asset type name
//
// JSON PARAMETERS:
//   None
//
// RETURNS:
//   asset type name
// -----------------------------------------------------------------
bool ww::exchange::asset_type::get_name(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    std::string name;
    ASSERT_SUCCESS(rsp, asset_type_store.get(md_name_key, name),
                   "contract state corrupted, no name");

    ww::value::String v(name.c_str());
    return rsp.value(v, false);
}
