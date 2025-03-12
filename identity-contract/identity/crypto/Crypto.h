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

#include "Types.h"

extern "C" {
#include <openssl/crypto.h>
#include <openssl/bn.h>
#include <openssl/ec.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
}

#include <memory>

typedef bool (*HashFunctionType)(const ww::types::ByteArray& message, ww::types::ByteArray& hash);

namespace pdo_contracts
{
namespace crypto
{
    // Typedefs for memory management
    typedef std::unique_ptr<BIGNUM, void (*)(BIGNUM*)> BIGNUM_ptr;
    typedef std::unique_ptr<BIO, void (*)(BIO*)> BIO_ptr;
    typedef std::unique_ptr<BN_CTX, void (*)(BN_CTX*)> BN_CTX_ptr;
    typedef std::unique_ptr<ECDSA_SIG, void (*)(ECDSA_SIG*)> ECDSA_SIG_ptr;
    typedef std::unique_ptr<EC_GROUP, void (*)(EC_GROUP*)> EC_GROUP_ptr;
    typedef std::unique_ptr<EC_KEY, void (*)(EC_KEY*)> EC_KEY_ptr;
    typedef std::unique_ptr<EC_POINT, void (*)(EC_POINT*)> EC_POINT_ptr;
    typedef std::unique_ptr<EVP_CIPHER_CTX, void (*)(EVP_CIPHER_CTX*)> CTX_ptr;
    typedef std::unique_ptr<EVP_MD_CTX, void (*)(EVP_MD_CTX*)> EVP_MD_CTX_ptr;
    typedef std::unique_ptr<HMAC_CTX, void (*)(HMAC_CTX*)> HMAC_CTX_ptr;

    typedef std::unique_ptr<EVP_MAC_CTX, void (*)(EVP_MAC_CTX*)> EVP_MAC_CTX_ptr;

    const unsigned int PBDK_Iterations = 10000;

    bool SHA256Hash(
        const ww::types::ByteArray& message, ww::types::ByteArray& hash);
    bool SHA256HMAC(
        const ww::types::ByteArray& message, const ww::types::ByteArray& key, ww::types::ByteArray& hmac);

    bool SHA384Hash(
        const ww::types::ByteArray& message, ww::types::ByteArray& hash);
    bool SHA384HMAC(
        const ww::types::ByteArray& message, const ww::types::ByteArray& key, ww::types::ByteArray& hmac);

    bool SHA512Hash(
        const ww::types::ByteArray& message, ww::types::ByteArray& hash);
    bool SHA512HMAC(
        const ww::types::ByteArray& message, const ww::types::ByteArray& key, ww::types::ByteArray& hmac);

    bool SHA512PasswordBasedKeyDerivation(
        const std::string& password, const ww::types::ByteArray& salt, ww::types::ByteArray& hmac);
}
}
