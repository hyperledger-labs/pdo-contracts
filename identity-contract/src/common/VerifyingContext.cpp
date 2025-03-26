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
#include "identity/crypto/PublicKey.h"
#include "identity/common/SigningContext.h"
#include "identity/common/VerifyingContext.h"


// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::identity::VerifyingContext
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
bool ww::identity::VerifyingContext::deserialize(const ww::value::Object& context)
{
    if (! ww::identity::VerifyingContext::verify_schema(context))
        return false;

    public_key_ = context.get_string("public_key");
    chain_code_ = context.get_string("chain_code");

    return true;
}

// -----------------------------------------------------------------
bool ww::identity::VerifyingContext::serialize(ww::value::Value& serialized_context) const
{
    ww::value::Structure context(VERIFYING_CONTEXT_SCHEMA);

    if (! context.set_string("public_key", public_key_.c_str()))
        return false;
    if (! context.set_string("chain_code", chain_code_.c_str()))
        return false;

    serialized_context.set(context);
    return true;
}

// -----------------------------------------------------------------
// initialize
//
// Validate the format of the public key and chain code. This is
// intended to provide a means of checking input from the user.
// -----------------------------------------------------------------
bool ww::identity::VerifyingContext::initialize(
    const std::string& encoded_public_key, // PEM encoded public key
    const std::string& encoded_chain_code) // base64 encoded chaincode
{
    pdo_contracts::crypto::signing::PublicKey public_key;
    ERROR_IF_NOT(public_key.Deserialize(encoded_public_key), "Invalid public key");

    ww::types::ByteArray chain_code;
    ERROR_IF_NOT(ww::crypto::b64_decode(encoded_chain_code, chain_code), "Invalid chain code");
    ERROR_IF(chain_code.size() != EXTENDED_KEY_SIZE, "Invalid chain code size");

    public_key_ = encoded_public_key;
    chain_code_ = encoded_chain_code;

    return true;
}

// -----------------------------------------------------------------
// verify
//
// Verify a signature using an extended key generated from the context
// path. The assumption is that the context path has been validated.
// -----------------------------------------------------------------
bool ww::identity::VerifyingContext::verify_signature(
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& signature) const
{
    pdo_contracts::crypto::signing::PublicKey public_key;
    ww::types::ByteArray chain_code;

    if (! generate_keys(public_key, chain_code))
        return false;

    return public_key.VerifySignature(message, signature, HASH_FUNCTION);
    // return ww::crypto::ecdsa::verify_signature(message, derived_public_key, signature);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::identity::VerifyingContext::generate_keys(
    pdo_contracts::crypto::signing::PublicKey& public_key,
    ww::types::ByteArray& chain_code) const
{
    ww::types::ByteArray parent_chain_code;
    ERROR_IF_NOT(ww::crypto::b64_decode(chain_code_, parent_chain_code), "Failed to decode chain code");

    pdo_contracts::crypto::signing::PublicKey parent_public_key(public_key_);
    std::vector<const std::string>::iterator path_element;

    ww::types::ByteArray extended_chain_code;
    pdo_contracts::crypto::signing::PublicKey extended_key(CURVE_NID);

    for (path_element = context_path_.begin(); path_element < context_path_.end(); path_element++)
    {
        ERROR_IF((*path_element)[0] == '#', "Hardened keys are not supported");
        ERROR_IF(! parent_public_key.DerivePublicKey(parent_chain_code, *path_element, extended_key, extended_chain_code),
                "Failed to generate child keys");

        // Prepare for the next iteration
        parent_public_key = extended_key;
        parent_chain_code = extended_chain_code;
    }

    public_key = parent_public_key;
    chain_code = parent_chain_code;

    return true;
}
