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

#include "Types.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "Cryptography.h"

#include "exchange/common/Common.h"
#include "identity/common/BigNum.h"
#include "identity/common/SigningContext.h"

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

#define CHUNK_HASH_FUNCTION ww::crypto::hash::sha256_hmac
#define EXTENDED_CHUNK_SIZE 16

const std::string index_base("PDO SigningContext:");

#ifdef DEBUG_BIGNUM
void DumpByteArray(const char* msg, const ww::types::ByteArray ba)
{
    std::string s;
    ww::crypto::b64_encode(ba, s);
    CONTRACT_SAFE_LOG(3, "[BA] %s: %s", msg, s.c_str());
}

void DumpBigNum(const char* msg, BIGNUM_TYPE bn)
{
    std::string s;
    bn.encode(s);
    CONTRACT_SAFE_LOG(3, "[BN] %s: %s", msg, s.c_str());
}
#endif

// -----------------------------------------------------------------
bool ww::identity::SigningContext::generate_keys(
    const ww::types::ByteArray& root_key, // base64 encoded representation of 48 byte random array
    const std::vector<std::string>& context_path,
    std::string& private_key,     // PEM encoded ECDSA private and public keys
    std::string& public_key)
{
    // Root key must contain EXTENDED_KEY_SIZE bytes
    if (root_key.size() != EXTENDED_KEY_SIZE)
        return false;

    // Create the initial extended key, this is a fixed value based on the
    // index_base strings
    ww::types::ByteArray base(index_base.begin(), index_base.end());
    ww::types::ByteArray hashed_base;
    if (! HASH_FUNCTION(base, hashed_base))
        return false;

    // CURVE_ORDER is a base64 encoded number
    const BIGNUM_TYPE curve_order(CURVE_ORDER);
    BIGNUM_TYPE extended_key;
    if (! extended_key.decode(hashed_base))
        return false;

    // Decode the root key, this is the chain code for the first iteration
    ww::types::ByteArray extended_chain_code = root_key;
    std::vector<const std::string>::iterator path_element;
    for ( path_element = context_path.begin(); path_element < context_path.end(); path_element++)
    {
        // For the purpose of the hashing, we are concatenating the index and the parent private key
        size_t path_hash = std::hash<std::string>{}(*path_element);

        ww::types::ByteArray ba_extended_key;
        extended_key.encode(ba_extended_key);

        ww::types::ByteArray index;
        index.push_back(0x00);  // this is part of the BIP32 specification for extended keys
        index.insert(index.end(), ba_extended_key.begin(), ba_extended_key.end());
        auto ptr = reinterpret_cast<uint8_t*>(&path_hash);
        index.insert(index.end(), ptr, ptr + sizeof(size_t));

        ww::types::ByteArray child_key_ba;
        ww::types::ByteArray child_chain_code;

        for (int i = 0; i < EXTENDED_KEY_SIZE / EXTENDED_CHUNK_SIZE; i++) {
            const size_t seg_start = i * EXTENDED_CHUNK_SIZE;
            const size_t seg_end = (i + 1) * EXTENDED_CHUNK_SIZE;
            ww::types::ByteArray chain_code_segment(
                extended_chain_code.begin() + seg_start, extended_chain_code.begin() + seg_end);

            ww::types::ByteArray hmac;
            CHUNK_HASH_FUNCTION(index, chain_code_segment, hmac);
            if (hmac.size() != 2 * EXTENDED_CHUNK_SIZE)
                return false;

            child_key_ba.insert(child_key_ba.end(), hmac.begin(), hmac.begin() + EXTENDED_CHUNK_SIZE);
            child_chain_code.insert(child_chain_code.end(), hmac.begin() + EXTENDED_CHUNK_SIZE, hmac.end());
        }

        // Add the extended key to the value created...
        BIGNUM_TYPE child_key;
        if (! child_key.decode(child_key_ba))
            return false;

        extended_key = (extended_key + child_key) % curve_order;
        extended_chain_code = child_chain_code;
    }

    // now convert the extended_key into an ECDSA key, for the moment the key
    // generation function only understands byte arrays
    ww::types::ByteArray extended_key_ba;
    if (! extended_key.encode(extended_key_ba))
        return false;

    return ww::crypto::ecdsa::generate_keys(extended_key_ba, private_key, public_key);
}
