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

#include "identity/common/SigningContext.h"
#include "identity/common/SigningContextManager.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::SigningContextManager
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
const std::string ww::identity::SigningContextManager::root_key_("__ROOT__");

// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::initialize(void)
{
    ww::identity::SigningContext root_context;

    std::vector<std::string> root_path;
    return root_context.save_to_datastore(store_, make_key(root_path));
}

// -----------------------------------------------------------------
std::string ww::identity::SigningContextManager::make_key(
    const std::vector<std::string>& context_path)
{
    std::string p(root_key_);

    std::vector<const std::string>::iterator path_element;
    for ( path_element = context_path.begin(); path_element < context_path.end(); path_element++)
        p += "." + (*path_element);

    return p;
}

// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::add_context(
    const std::vector<std::string>& context_path,
    const ww::identity::SigningContext& new_context)
{
    // must contain at least the new context name
    if (context_path.size() < 1)
        return false;

    const std::string new_context_name = context_path.back();
    const std::vector<std::string> parent_path(context_path.begin(), context_path.end() - 1);

    ww::identity::SigningContext parent;
    std::vector<std::string> extended_path;
    if (! find_context(parent_path, extended_path, parent))
        return false;

    // make sure the context path terminates in a signing context
    if (extended_path.size() > 0)
        return false;

    // make sure the parent context is not extensible; if it is extensible
    // then all paths are legitimate and none may have signing contexts
    if (parent.extensible_)
        return false;

    // make sure the new context does not already exist
    if (parent.contains(new_context_name))
        return false;

    // looks like all tests pass, now update the parent
    parent.subcontexts_.push_back(new_context_name);
    const std::string pkey = make_key(parent_path);
    if (! parent.save_to_datastore(store_, pkey))
        return false;

    // and now save the new context; note that we
    // assume that the new context has been correctly
    // initialized; specifically, the subcontexts vector
    // should be empty on the initial save
    const std::string ckey = make_key(context_path);
    if (! new_context.save_to_datastore(store_, ckey))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::remove_context(
    const std::vector<std::string>& context_path)
{
    return true;
}

// -----------------------------------------------------------------
bool ww::identity::SigningContextManager::find_context(
    const std::vector<std::string>& context_path,
    std::vector<std::string>& extended_path,
    ww::identity::SigningContext& context) const
{
    extended_path.resize(0);

    // empty path should point to the root context
    std::vector<std::string> path;
    if (! context.get_from_datastore(store_, make_key(path)))
    {
        // this shouldn't happen unless the data store has been corrupted
        CONTRACT_SAFE_LOG(3, "failed to locate the root context\n");
        return false;
    }

    // walk the tree of contexts and verify that they exist and are not extensible
    for (auto path_element = context_path.begin(); path_element < context_path.end(); path_element++)
    {
        // make sure that the path element is in the current context, that is, verify
        // that the context path is valid
        if (! context.contains(*path_element))
        {
            CONTRACT_SAFE_LOG(3, "failed to find a path element %s\n", path_element->c_str());
            return false;
        }

        // create the path to retrieve the next context in the path
        path.push_back(*path_element);

        const std::string key = make_key(path);
        if (! context.get_from_datastore(store_, key))
        {
            // this shouldn't happen unless the data store has been corrupted
            CONTRACT_SAFE_LOG(3, "failed to find the context from the path\n");
            return false;
        }

        // if the current context is extensible then we copy whatever is left in the context path
        // into the extended path
        if (context.extensible_)
        {
            for (path_element++; path_element < context_path.end(); path_element++)
                extended_path.push_back(*path_element);

            return true;
        }
    }

    return true;
}
