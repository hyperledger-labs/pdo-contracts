/* Copyright 2022 Intel Corporation
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

#include <openssl/evp.h>
#include <openssl/core_names.h>

#include "Types.h"
#include "WasmExtensions.h"

#include "exchange/common/Common.h"
#include "identity/crypto/Crypto.h"

namespace pcrypto = pdo_contracts::crypto;

#define USE_EVP_HASH_FUNCTIONS 1

// -----------------------------------------------------------------
// Hash Functions
// -----------------------------------------------------------------
static bool _ComputeHash_(
    const EVP_MD *hashfunc(void),
    const ww::types::ByteArray& message,
    ww::types::ByteArray& hash)
{
    // **** NOTE ****
    // There does not appear to be anything wrong with this code, but it
    // fails consistently on DigestInit. The alternatives below work but
    // use deprecated functions. This needs to be revisited.

    pcrypto::EVP_MD_CTX_ptr evp_md_ctx(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    ERROR_IF_NULL(evp_md_ctx.get(), "invalid hash context");

    const EVP_MD *md = hashfunc();
    hash.resize(EVP_MD_size(md));

    int ret;

    ret = EVP_DigestInit_ex(evp_md_ctx.get(), md, nullptr);
    ERROR_IF(ret == 0, "hash digest init failed");

    ret = EVP_DigestUpdate(evp_md_ctx.get(), message.data(), message.size());
    ERROR_IF(ret == 0, "hash update failed");

    ret = EVP_DigestFinal_ex(evp_md_ctx.get(), hash.data(), NULL);
    ERROR_IF(ret == 0, "hash final failed");

    return true;
}

bool pcrypto::SHA256Hash(const ww::types::ByteArray& message, ww::types::ByteArray& hash)
{
#if USE_EVP_HASH_FUNCTIONS
    return _ComputeHash_(EVP_sha256, message, hash);
#else
    hash.resize(SHA256_DIGEST_LENGTH);

    SHA256_CTX ctx;
    ERROR_IF(SHA256_Init(&ctx) <= 0, "sha56 init failed");
    ERROR_IF(SHA256_Update(&ctx, message.data(), message.size()) <= 0, "sha256 update failed");
    ERROR_IF(SHA256_Final(hash.data(), &ctx) <= 0, "sha256 final failed");

    return true;
#endif
}

bool pcrypto::SHA384Hash(const ww::types::ByteArray& message, ww::types::ByteArray& hash)
{
#if USE_EVP_HASH_FUNCTIONS
    return _ComputeHash_(EVP_sha384, message, hash);
#else
    hash.resize(SHA384_DIGEST_LENGTH);

    SHA512_CTX ctx;
    ERROR_IF(SHA384_Init(&ctx) <= 0, "sha384 init failed");
    ERROR_IF(SHA384_Update(&ctx, message.data(), message.size()) <= 0, "sha384 update failed");
    ERROR_IF(SHA384_Final(hash.data(), &ctx) <= 0, "sha384 final failed");

    return true;
#endif
}

bool pcrypto::SHA512Hash(const ww::types::ByteArray& message, ww::types::ByteArray& hash)
{
#if USE_EVP_HASH_FUNCTIONS
    return _ComputeHash_(EVP_sha512, message, hash);
#else
    hash.resize(SHA384_DIGEST_LENGTH);

    SHA512_CTX ctx;
    ERROR_IF(SHA512_Init(&ctx) <= 0, "sha512 init failed");
    ERROR_IF(SHA512_Update(&ctx, message.data(), message.size()) <= 0, "sha512 update failed");
    ERROR_IF(SHA512_Final(hash.data(), &ctx) <= 0, "sha512 final failed");

    return true;
#endif
}

// -----------------------------------------------------------------
// HMAC Functions
// -----------------------------------------------------------------
static bool _ComputeHMAC_(
    const std::string& digest_name,
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& key,
    ww::types::ByteArray& hmac)
{
    int res;

    OSSL_LIB_CTX *library_context = OSSL_LIB_CTX_new();

    EVP_MAC* mac = EVP_MAC_fetch(library_context, "HMAC", nullptr);
    ERROR_IF_NULL(mac, "failed to fetch MAC algorithm");

    pcrypto::EVP_MAC_CTX_ptr ctx(EVP_MAC_CTX_new(mac), EVP_MAC_CTX_free);
    ERROR_IF_NULL(ctx.get(), "failed create the MAC context");

    // 3. Set the MAC parameters (key and digest)
    OSSL_PARAM params[3];
    params[0] = OSSL_PARAM_construct_utf8_string(
        OSSL_MAC_PARAM_DIGEST, const_cast<char*>(digest_name.c_str()), digest_name.size());
    params[1] = OSSL_PARAM_construct_end();

    res = EVP_MAC_init(ctx.get(), key.data(), key.size(), params);
    ERROR_IF(res <= 0, "Failed to initialize MAC context");

    res = EVP_MAC_update(ctx.get(), (const unsigned char*)message.data(), message.size());
    ERROR_IF(res <= 0, "Failed to update MAC context");

    size_t outlen = EVP_MAC_CTX_get_mac_size(ctx.get());
    unsigned char* mac_value = (unsigned char*)OPENSSL_malloc(outlen);
    ERROR_IF_NULL(mac_value, "Failed to allocate memory for mac value");

    size_t mac_len = 0;
    res = EVP_MAC_final(ctx.get(), mac_value, &mac_len, outlen);
    ERROR_IF(res <= 0, "Failed to finalize MAC context");

    hmac.assign(mac_value, mac_value + mac_len);

    return true;
}

bool pcrypto::SHA256HMAC(
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& key,
    ww::types::ByteArray& hmac)
{
    return _ComputeHMAC_("SHA256", message, key, hmac);
}

bool pcrypto::SHA384HMAC(
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& key,
    ww::types::ByteArray& hmac)
{
    return _ComputeHMAC_("SHA384", message, key, hmac);
}

bool pcrypto::SHA512HMAC(
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& key,
    ww::types::ByteArray& hmac)
{
    return _ComputeHMAC_("SHA512", message, key, hmac);
}

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
static bool _ComputePasswordBasedKeyDerivation_(
    const EVP_MD *hashfunc(void),
    const std::string& password,
    const ww::types::ByteArray& salt,
    const unsigned int iterations,
    ww::types::ByteArray& key)
{
    const EVP_MD *md = hashfunc();
    key.resize(EVP_MD_size(md));

    int ret;
    ret = PKCS5_PBKDF2_HMAC(
        password.c_str(), password.size(),
        salt.data(), salt.size(),
        iterations, md,
        key.size(), key.data());
    ERROR_IF(ret == 0, "password derivation failed");

    return true;
}

bool pcrypto::SHA512PasswordBasedKeyDerivation(
    const std::string& password,
    const ww::types::ByteArray& salt,
    ww::types::ByteArray& key)
{
    return _ComputePasswordBasedKeyDerivation_(EVP_sha512, password, salt, pcrypto::PBDK_Iterations, key);
}
