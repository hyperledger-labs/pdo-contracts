/* Copyright 2025 Intel Corporation
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


#pragma once
#include <string>
#include <vector>

#include "Util.h"
#include "Value.h"

#include "exchange/common/Common.h"
#include "identity/crypto/PrivateKey.h"
#include "identity/crypto/PublicKey.h"

#define USE_SECP384R1

// https://en.wikipedia.org/wiki/P-384
#ifdef USE_SECP384R1
#define EXTENDED_KEY_SIZE	48
#define HASH_FUNCTION		pdo_contracts::crypto::SHA384Hash
#define CURVE_NID               NID_secp384r1
#endif

namespace ww
{
namespace identity
{
    // -----------------------------------------------------------------
    // This class abstracts the functions necessary for verifying
    // a signature with support for extended keys.
    // -----------------------------------------------------------------
    class BaseVerifyingContext : public ww::exchange::SerializeableObject
    {
    protected:
        std::string public_key_; // PEM encoded public key
        std::string chain_code_; // Base64 encoded byte array

    public:

        bool set_chain_code(const ww::types::ByteArray& chain_code);
        bool get_chain_code(ww::types::ByteArray& chain_code) const;

        bool set_public_key(const pdo_contracts::crypto::signing::PublicKey& key);
        bool get_public_key(pdo_contracts::crypto::signing::PublicKey& key) const;


        bool virtual verify_signature(
            const std::vector<std::string>& context_path,
            const ww::types::ByteArray& message,
            const ww::types::ByteArray& signature) const = 0;
    };

    // -----------------------------------------------------------------
    // This class abstracts the functions necessary for signing a message
    // using an extended key.
    // -----------------------------------------------------------------
    class BaseSigningContext : public BaseVerifyingContext
    {
    protected:
        std::string private_key_; // PEM encoded private key

    public:

        bool set_private_key(const pdo_contracts::crypto::signing::PrivateKey& key);
        bool get_private_key(pdo_contracts::crypto::signing::PrivateKey& key) const;

        bool virtual sign_message(
            const std::vector<std::string>& context_path,
            const ww::types::ByteArray& message,
            ww::types::ByteArray& signature) const = 0;
    };



}; // identity
}  // ww
