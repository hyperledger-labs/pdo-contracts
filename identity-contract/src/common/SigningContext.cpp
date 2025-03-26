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

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::SigningContext
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::contains(const std::string& name) const
{
    return std::find(subcontexts_.begin(), subcontexts_.end(), name) != subcontexts_.end();
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

    public_key_ = context.get_string("public_key");
    private_key_ = context.get_string("private_key");
    chain_code_ = context.get_string("chain_code");

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

    context.set_string("public_key", public_key_.c_str());
    context.set_string("private_key", private_key_.c_str());
    context.set_string("chain_code", chain_code_.c_str());

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
    const ww::types::ByteArray& message,
    ww::types::ByteArray& signature) const
{
    pdo_contracts::crypto::signing::PrivateKey private_key;
    ww::types::ByteArray chain_code;

    if (! generate_keys(private_key, chain_code))
        return false;

    return private_key.SignMessage(message, signature, HASH_FUNCTION);
}

// -----------------------------------------------------------------
// verify
//
// Verify a signature using an extended key generated from the context
// path. The assumption is that the context path has been validated.
// -----------------------------------------------------------------
bool ww::identity::SigningContext::verify_signature(
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& signature) const
{
    pdo_contracts::crypto::signing::PrivateKey private_key;
    ww::types::ByteArray chain_code;

    if (! generate_keys(private_key, chain_code))
        return false;

    pdo_contracts::crypto::signing::PublicKey public_key(private_key);
    return public_key.VerifySignature(message, signature, HASH_FUNCTION);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    std::string& private_key_str,     // PEM encoded ECDSA private and public keys
    std::string& public_key_str) const
{
    pdo_contracts::crypto::signing::PrivateKey private_key;
    ww::types::ByteArray chain_code;

    if (! ww::identity::SigningContext::generate_keys(private_key, chain_code))
        return false;

    pdo_contracts::crypto::signing::PublicKey public_key(private_key);

    ERROR_IF_NOT(private_key.Serialize(private_key_str), "Failed to serialize private key");
    ERROR_IF_NOT(public_key.Serialize(public_key_str), "Failed to serialize public key");

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    pdo_contracts::crypto::signing::PrivateKey& private_key,
    ww::types::ByteArray& chain_code) const
{
    ww::types::ByteArray root_chain_code;
    if (! get_chain_code(root_chain_code))
        return false;

    pdo_contracts::crypto::signing::PrivateKey root_key(CURVE_NID);
    if (! get_private_key(root_key))
        return false;

    return generate_keys(context_path_, root_key, root_chain_code, private_key, chain_code);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    const std::vector<std::string>& context_path,
    pdo_contracts::crypto::signing::PrivateKey& private_key,
    ww::types::ByteArray& chain_code) const
{
    ww::types::ByteArray root_chain_code;
    if (! get_chain_code(root_chain_code))
        return false;

    pdo_contracts::crypto::signing::PrivateKey root_key(CURVE_NID);
    if (! get_private_key(root_key))
        return false;

    return generate_keys(context_path, root_key, root_chain_code, private_key, chain_code);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    const std::vector<std::string>& context_path,
    const pdo_contracts::crypto::signing::PrivateKey& root_key,
    const ww::types::ByteArray& root_chain_code,
    pdo_contracts::crypto::signing::PrivateKey& private_key,
    ww::types::ByteArray& chain_code)
{
    ww::types::ByteArray parent_chain_code(root_chain_code);
    pdo_contracts::crypto::signing::PrivateKey parent_key(root_key);

    ww::types::ByteArray child_chain_code;
    pdo_contracts::crypto::signing::PrivateKey child_key(CURVE_NID);

    std::vector<const std::string>::iterator path_element;
    for (path_element = context_path.begin(); path_element < context_path.end(); path_element++)
    {
        if ((*path_element)[0] == '#')
        {
            ERROR_IF_NOT(parent_key.DeriveHardenedKey(parent_chain_code, *path_element, child_key, child_chain_code),
                     "Failed to generate hardened child keys");
        }
        else
        {
            ERROR_IF_NOT(parent_key.DeriveNormalKey(parent_chain_code, *path_element, child_key, child_chain_code),
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
