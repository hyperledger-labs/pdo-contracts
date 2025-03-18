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

#include <functional>
#include <string>
#include <vector>

#include "Cryptography.h"
#include "Types.h"
#include "Value.h"

#include "exchange/common/Common.h"
#include "identity/crypto/Crypto.h"
#include "identity/crypto/PrivateKey.h"
#include "identity/crypto/PublicKey.h"
#include "identity/common/SigningContext.h"

const std::string ww::identity::SigningContext::index_base = "PDO SigningContext:";

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::SigningContext
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::contains(const std::string& name) const
{
    for (auto i = subcontexts_.begin(); i != subcontexts_.end(); i++)
    {
        if ((*i) == name)
            return true;
    }

    return false;
}

// -----------------------------------------------------------------
bool ww::identity::SigningContext::deserialize(const ww::value::Object& context)
{
    if (! ww::identity::SigningContext::verify_schema(context))
        return false;

    extensible_ = context.get_boolean("extensible");
    description_ = context.get_string("description");
    subcontexts_.resize(0);

    ww::value::Array subcontexts;
    if (! context.get_value("subcontexts", subcontexts))
        return false;

    size_t count = subcontexts.get_count();
    for (size_t index = 0; index < count; index++)
    {
        const std::string context_name(subcontexts.get_string(index));
        subcontexts_.push_back(context_name);
    }

    return true;
}

// -----------------------------------------------------------------
bool ww::identity::SigningContext::serialize(ww::value::Value& serialized_context) const
{
    ww::value::Structure context(SIGNING_CONTEXT_SCHEMA);
    if (! context.set_boolean("extensible", extensible_))
        return false;

    if (! context.set_string("description", description_.c_str()))
        return false;

    ww::value::Array subcontexts;
    for (auto c = subcontexts_.begin(); c < subcontexts_.end(); c++)
    {
        ww::value::String s(c->c_str());
        if (! subcontexts.append_value(s))
            return false;
    }
    context.set_value("subcontexts", subcontexts);

    serialized_context.set(context);
    return true;
}

// -----------------------------------------------------------------
// sign
//
// Generate an extended key from the context path and use that to sign
// the buffer. The assumption is that the context path has been validated.
// -----------------------------------------------------------------
bool ww::identity::SigningContext::sign_message(
    const ww::types::ByteArray& root_key,
    const std::vector<std::string>& context_path,
    const ww::types::ByteArray& message,
    ww::types::ByteArray& signature)
{
    std::string private_key, public_key;
    if (! ww::identity::SigningContext::generate_keys(root_key, context_path, private_key, public_key))
        return false;

    return ww::crypto::ecdsa::sign_message(message, private_key, signature);
}

// -----------------------------------------------------------------
// verify
//
// Verify a signature using an extended key generated from the context
// path. The assumption is that the context path has been validated.
// -----------------------------------------------------------------
bool ww::identity::SigningContext::verify_signature(
    const ww::types::ByteArray& root_key,
    const std::vector<std::string>& context_path,
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& signature)
{
    std::string private_key, public_key;
    if (! ww::identity::SigningContext::generate_keys(root_key, context_path, private_key, public_key))
        return false;

    return ww::crypto::ecdsa::verify_signature(message, public_key, signature);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
// generate_key implements a version of the bip32 protocol for generating
// extended keys. more information about bip32 is available here:
// https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
// the main difference is that this implementation currently only performs
// hardened derivations (private key) and it focuses on the secp384r1
// curve rather than the bitcoin focused secp256k1 curve.
// -----------------------------------------------------------------
// -----------------------------------------------------------------

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    const ww::types::ByteArray& root_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const std::vector<std::string>& context_path, // array of strings, path to the current key
    std::string& private_key,     // PEM encoded ECDSA private and public keys
    std::string& public_key)
{
    pdo_contracts::crypto::signing::PrivateKey extended_private_key;
    ww::types::ByteArray extended_chain_code;

    if (! ww::identity::SigningContext::generate_keys(
            root_chain_code, context_path, extended_private_key, extended_chain_code))
        return false;

    if (! extended_private_key.Serialize(private_key))
        return false;

    pdo_contracts::crypto::signing::PublicKey extended_public_key(extended_private_key);
    if (! extended_public_key.Serialize(public_key))
        return false;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    const ww::types::ByteArray& root_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const std::vector<std::string>& context_path, // array of strings, path to the current key
    pdo_contracts::crypto::signing::PrivateKey& private_key,
    ww::types::ByteArray& chain_code)
{
    ERROR_IF(context_path.size() == 0, "Invalid empty context path");
    ERROR_IF(root_chain_code.size() != EXTENDED_KEY_SIZE, "Invalid root chain code size");

    // Root key --> fixed value derived from a common string
    ww::types::ByteArray base(index_base.begin(), index_base.end());
    ww::types::ByteArray root_key;

    int res = HASH_FUNCTION(base, root_key);
    ERROR_IF(res <= 0, "Failed to hash base string");

    // And start processing the context path. The context path is a list of strings
    ww::types::ByteArray parent_chain_code = root_chain_code;
    pdo_contracts::crypto::signing::PrivateKey parent_key(CURVE_NID, root_key);
    std::vector<const std::string>::iterator path_element;

    ww::types::ByteArray child_chain_code;
    pdo_contracts::crypto::signing::PrivateKey child_key(CURVE_NID);

    for (path_element = context_path.begin(); path_element < context_path.end(); path_element++)
    {
        if ((*path_element)[0] == '#')
        {
            //CONTRACT_SAFE_LOG(3, "generate hardened key for element %s", (*path_element).c_str());
            ERROR_IF(! parent_key.DeriveHardenedKey(parent_chain_code, *path_element, child_key, child_chain_code),
                "Failed to generate hardened child keys");
        }
        else
        {
            //CONTRACT_SAFE_LOG(3, "generate normal key for element %s", (*path_element).c_str());
            ERROR_IF(! parent_key.DeriveNormalKey(parent_chain_code, *path_element, child_key, child_chain_code),
                "Failed to generate normal child keys");
        }

        // Prepare for the next iteration
        parent_key = child_key;
        parent_chain_code = child_chain_code;
    }

    private_key = parent_key;
    chain_code = parent_chain_code;

    return true;
}
