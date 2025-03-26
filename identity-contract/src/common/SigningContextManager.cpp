/* Copyright 2023 Intel Corporation
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

#include <algorithm>
#include <functional>
#include <string>
#include <vector>

#include "KeyValue.h"
#include "Types.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "exchange/common/Common.h"
#include "identity/common/SigningContext.h"
#include "identity/common/SigningContextManager.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::SigningContextManager
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
const std::string ww::identity::SigningContextManager::store_key_root_("__ROOT__");
const std::string ww::identity::SigningContextManager::store_key_separator_("$$$");
const std::string ww::identity::SigningContextManager::extended_key_base_ = "PDO SigningContext:";

// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::initialize(void)
{
    ww::identity::SigningContext root_context(false, "Signing context root");

    // ---------- create the root chain code ----------
    ww::types::ByteArray root_chain_code(EXTENDED_KEY_SIZE);
    ERROR_IF_NOT(ww::crypto::random_identifier(root_chain_code),
                 "Failed to generate random identifier for root extended key");
    ERROR_IF_NOT(root_context.set_chain_code(root_chain_code),
                 "Failed to set root chain code");

    // Root key --> fixed value derived from a common string
    ww::types::ByteArray base(extended_key_base_.begin(), extended_key_base_.end());
    ww::types::ByteArray root_key;

    ERROR_IF(HASH_FUNCTION(base, root_key) <= 0, "Failed to hash base string");

    pdo_contracts::crypto::signing::PrivateKey root_private_key(CURVE_NID, root_key);
    ERROR_IF_NOT(root_context.set_private_key(root_private_key),
                 "Failed to set root private key");

    // Save the root context to the persistent store
   return root_context.save_to_datastore(store_, store_key_root_);
}

// -----------------------------------------------------------------
// make_key
//
// make a string that can be used to identify the signing context in the
// key value store; the key must be unique for each signing context
// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::make_store_key(
    const std::vector<std::string>& context_path,
    std::string& key)
{
    key = store_key_root_;

    std::vector<const std::string>::iterator path_element;
    for ( path_element = context_path.begin(); path_element < context_path.end(); path_element++)
    {
        // make sure that the path element does not contain the key separator
        ERROR_IF((*path_element).find(store_key_separator_) != std::string::npos,
                 "path element contains the key separator");

        key += store_key_separator_ + (*path_element);
    }

    return true;
}

// -----------------------------------------------------------------
// add_context
//
// Add a new signing context to the context tree. The context path
// can only extend an existing context by a single path element. And
// it may not point to an extensible context. That is, there can be
// no registered contexts beneath an extensible context.
// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::add_context(
    bool extensible,
    const std::string& description,
    const std::vector<std::string>& context_path) const
{
    // must contain at least the new context name
    ERROR_IF(context_path.size() < 1, "context path is empty");

    // new_context_name is the name of the new context relative to the parent
    const std::string new_context_name = context_path.back();

    // ---------- find the parent context ----------
    // parent_path is the path to the parent context that will be extended
    const std::vector<std::string> parent_path(context_path.begin(), context_path.end() - 1);

    ww::identity::SigningContext parent;
    std::vector<std::string> extended_path;
    if (! find_context(parent_path, extended_path, parent))
        return false;

    // make sure the context path terminates in a signing context,
    // since we are only extending a context by a single element, the
    // extended_path must be empty
    ERROR_IF(extended_path.size() > 0, "parent context does not exist");

    // make sure the parent context is not extensible; if it is
    // extensible then all paths are legitimate and none may have
    // signing contexts
    ERROR_IF(parent.extensible_, "parent context is extensible");

    // make sure the new context does not already exist
    ERROR_IF(parent.contains(new_context_name), "context already exists");

    // ---------- looks like all tests pass, now update the parent ----------
    std::string pkey;
    ERROR_IF_NOT(make_store_key(parent_path, pkey), "failed to make the parent storage key");

    parent.subcontexts_.push_back(new_context_name);
    if (! parent.save_to_datastore(store_, pkey))
        return false;

    // ---------- finish initializing the new context ----------
    ww::identity::SigningContext new_context(extensible, description);

    // Generate the private key and chain code for the the signing context
    pdo_contracts::crypto::signing::PrivateKey new_private_key;
    ww::types::ByteArray new_chain_code(EXTENDED_KEY_SIZE);
    std::vector<std::string>new_context_path = { new_context_name };
    ERROR_IF_NOT(parent.generate_keys(new_context_path, new_private_key, new_chain_code),
                 "failed to generate new private key");

    new_context.set_private_key(new_private_key);
    new_context.set_chain_code(new_chain_code);

    // And save it in the data store
    std::string ckey;
    ERROR_IF_NOT(make_store_key(context_path, ckey), "failed to make the child storage key");

    if (! new_context.save_to_datastore(store_, ckey))
        return false;

    return true;
}

// -----------------------------------------------------------------
// remove_context
//
// not implemented
// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::remove_context(
    const std::vector<std::string>& context_path) const
{
    return true;
}

// -----------------------------------------------------------------
// find_context
//
// Given a context path, find the context with the longest matching
// path prefix. If the matching context is extensible, then the
// remaining path elements are placed in the extended_path vector. If
// the context is not extensible, then the extended_path vector will
// be empty and there must be an exact match between the context path
// and the context.
// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::find_context(
    const std::vector<std::string>& context_path,
    std::vector<std::string>& extended_path,
    ww::identity::SigningContext& context) const
{
    extended_path.resize(0);

    // empty path should point to the root context
    std::vector<std::string> path;
    std::string key;

    ERROR_IF_NOT(make_store_key(path, key), "failed to make the storage key");

    ERROR_IF_NOT(context.get_from_datastore(store_, key), "failed to locate the root context");

    // walk the tree of contexts and verify that they exist and are not extensible
    for (auto path_element = context_path.begin(); path_element < context_path.end(); path_element++)
    {
        // make sure that the path element is in the current context, that is, verify
        // that the context path is valid, this can fail if there is an attempt to
        // extend a context that is not extensible or if the path is simply invalid
        ERROR_IF_NOT(context.contains(*path_element),
                     "failed to find a path element %s", path_element->c_str());

        // create the path to retrieve the next context in the path
        path.push_back(*path_element);

        ERROR_IF_NOT(make_store_key(path, key), "failed to make the storage key");
        ERROR_IF_NOT(context.get_from_datastore(store_, key), "failed to find the context from the path");

        // if the current context is extensible then we copy whatever
        // is left in the context path into the extended path
        if (context.extensible_)
        {
            for (path_element++; path_element < context_path.end(); path_element++)
                extended_path.push_back(*path_element);

            return true;
        }
    }

    return true;
}
