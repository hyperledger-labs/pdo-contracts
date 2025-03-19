/* Copyright 2018 Intel Corporation
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
#include <memory>

#include <openssl/crypto.h>
#include <openssl/ec.h>
#include <openssl/pem.h>

#include "exchange/common/Common.h"

#include "identity/crypto/Crypto.h"
#include "identity/crypto/PrivateKey.h"
#include "identity/crypto/PublicKey.h"

#include "Types.h"

namespace signing = pdo_contracts::crypto::signing;
namespace crypto = pdo_contracts::crypto;

// -----------------------------------------------------------------
// Constructor from numeric key
// -----------------------------------------------------------------
signing::PrivateKey::PrivateKey(const int curve, const ww::types::ByteArray& numeric_key) : Key(curve)
{
    InitializeFromNumericKey(numeric_key);
}

// -----------------------------------------------------------------
// Copy constructor
// -----------------------------------------------------------------
signing::PrivateKey::PrivateKey(const signing::PrivateKey& privateKey)
{
    InitializeFromPrivateKey(privateKey);
}

// -----------------------------------------------------------------
// Move constructor
// -----------------------------------------------------------------
signing::PrivateKey::PrivateKey(signing::PrivateKey&& privateKey)
{
    // when the privateKey does not have a key associated with it,
    // e.g. when privateKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    key_ = privateKey.key_;
    curve_ = privateKey.curve_;

    privateKey.key_ = nullptr;
}

// -----------------------------------------------------------------
// Constructor from encoded string
// -----------------------------------------------------------------
signing::PrivateKey::PrivateKey(const std::string& encoded)
{
    Deserialize(encoded);
}

// -----------------------------------------------------------------
// Destructor
// -----------------------------------------------------------------
signing::PrivateKey::~PrivateKey()
{
    ResetKey();
}

// -----------------------------------------------------------------
void signing::PrivateKey::ResetKey(void)
{
    // reset the the key, do not change the curve details
    if (key_)
        EC_KEY_free(key_);

    key_ = nullptr;
    curve_ = NID_undef;
}

// -----------------------------------------------------------------
// Custom curve constructor with initial key specified as a bignum
// -----------------------------------------------------------------
bool signing::PrivateKey::InitializeFromNumericKey(
    const ww::types::ByteArray& numeric_key)
{
    int res;

    crypto::BIGNUM_ptr bn_key(BN_bin2bn((const unsigned char*)numeric_key.data(), numeric_key.size(), NULL), BN_free);
    ERROR_IF_NULL(bn_key, "Crypto Error (PrivateKey::InitializeFromNumericKey): Could not create bignum");

    crypto::BN_CTX_ptr b_ctx(BN_CTX_new(), BN_CTX_free);
    ERROR_IF_NULL(b_ctx, "Crypto Error (PrivateKey::InitializeFromNumericKey): Cound not create BN context");

    crypto::BIGNUM_ptr r(BN_new(), BN_free);
    ERROR_IF_NULL(r, "Crypto Error (PrivateKey::InitializeFromNumericKey): Cound not create BN");

    crypto::BIGNUM_ptr o(BN_new(), BN_free);
    ERROR_IF_NULL(o, "Crypto Error (PrivateKey::InitializeFromNumericKey): Cound not create BN");

    // setup the private key
    crypto::EC_KEY_ptr private_key(EC_KEY_new(), EC_KEY_free);
    ERROR_IF_NULL(private_key, "Crypto Error (PrivateKey::InitializeFromNumericKey): Could not create new EC_KEY");

    crypto::EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(curve_), EC_GROUP_clear_free);
    ERROR_IF_NULL(ec_group, "Crypto Error (PrivateKey::InitializeFromNumericKey): Could not create EC_GROUP");

    res = EC_KEY_set_group(private_key.get(), ec_group.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::InitializeFromNumericKey): Could not set EC_GROUP");

    EC_GROUP_get_order(ec_group.get(), o.get(), b_ctx.get());

    res = BN_mod(r.get(), bn_key.get(), o.get(), b_ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::InitializeFromNumericKey): Bignum modulus failed");

    res = EC_KEY_set_private_key(private_key.get(), r.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::InitializeFromNumericKey): Could not create new key");

    // setup the public key
    crypto::EC_POINT_ptr public_point(EC_POINT_new(ec_group.get()), EC_POINT_free);
    ERROR_IF_NULL(public_point, "Crypto Error (PrivateKey::InitializeFromNumericKey): Could not allocate point");

    res = EC_POINT_mul(ec_group.get(), public_point.get(), r.get(), NULL, NULL, b_ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::InitializeFromNumericKey): point multiplication failed");

    res = EC_KEY_set_public_key(private_key.get(), public_point.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::InitializeFromNumericKey): failed to set public key");

    // complete the sanity check
    res = EC_KEY_check_key(private_key.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::InitializeFromNumericKey): invalid key");

    key_ = private_key.get();
    private_key.release();

    return true;
}

// -----------------------------------------------------------------
// InitializeFromPrivateKey
// -----------------------------------------------------------------
bool signing::PrivateKey::InitializeFromPrivateKey(const signing::PrivateKey& privateKey)
{
    key_ = nullptr;
    curve_ = privateKey.curve_;

    // when the privateKey does not have a key associated with it,
    // e.g. when privateKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    if (privateKey.key_ != nullptr)
    {
        key_ = EC_KEY_dup(privateKey.key_);
        ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::InitializeFromPrivateKey): Could not copy private key");
    }

    return true;
}

// -----------------------------------------------------------------
// boolean conversion operator, returns true if there is a
// key associated with the object
signing::PrivateKey::operator bool(void) const
{
    return key_ != nullptr;
}

// -----------------------------------------------------------------
// assignment operator overload
// throws RuntimeError
signing::PrivateKey& signing::PrivateKey::operator=(
    const signing::PrivateKey& privateKey)
{
    if (this == &privateKey)
        return *this;

    ResetKey();

    // when the privateKey does not have a key associated with it,
    // e.g. when privateKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    if (privateKey)
        key_ = EC_KEY_dup(privateKey.key_);

    curve_ = privateKey.curve_;

    return *this;
}  // signing::PrivateKey::operator =

// -----------------------------------------------------------------
// Deserialize ECDSA Private Key
// -----------------------------------------------------------------
bool signing::PrivateKey::Deserialize(const std::string& encoded)
{
    ResetKey();

    crypto::BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    ERROR_IF_NULL(bio, "Crypto Error (PrivateKey::Deserialize): Could not create BIO");

    // generally we would throw a CryptoError if an OpenSSL function fails; however, in this
    // case, the conversion really means that we've been given a bad value for the key
    // so throw a value error instead
    key_ = PEM_read_bio_ECPrivateKey(bio.get(), NULL, NULL, NULL);
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::Deserialize): Could not deserialize private ECDSA key");

    curve_ = EC_GROUP_get_curve_name(EC_KEY_get0_group(key_));

    return true;
}

// -----------------------------------------------------------------
// Generate ECDSA private key
// -----------------------------------------------------------------
bool signing::PrivateKey::Generate()
{
    ResetKey();

    crypto::EC_KEY_ptr private_key(EC_KEY_new(), EC_KEY_free);
    ERROR_IF_NULL(private_key, "Crypto Error (PrivateKey::Generate): Could not create new EC_KEY");

    crypto::EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(curve_), EC_GROUP_clear_free);
    ERROR_IF(ec_group, "Crypto Error (PrivateKey::Generate): Could not create EC_GROUP");

    int res;

    res = EC_KEY_set_group(private_key.get(), ec_group.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::Generate): Could not set EC_GROUP");

    res = EC_KEY_generate_key(private_key.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::Generate): Could not generate EC_KEY");

    key_ = private_key.get();
    private_key.release();

    return true;
}

// -----------------------------------------------------------------
// Derive Digital Signature public key from private key
// -----------------------------------------------------------------
bool signing::PrivateKey::GetPublicKey(signing::PublicKey& publicKey) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::GetPublicKey): Private key is not initialized");

    PublicKey key(*this);
    publicKey = key;

    return true;
}

// -----------------------------------------------------------------
// Serialize ECDSA PrivateKey
// -----------------------------------------------------------------
bool signing::PrivateKey::Serialize(std::string& encoded) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::Serialize): Private key not initialized");

    crypto::BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);
    ERROR_IF_NULL(bio, "Crypto Error (PrivateKey::Serialize): Could not create BIO");

    int res;

    res = PEM_write_bio_ECPrivateKey(bio.get(), key_, NULL, NULL, 0, 0, NULL);
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::Serialize) failed to write PEM key");

    int keylen = BIO_pending(bio.get());
    ww::types::ByteArray pem_str(keylen + 1);
    res = BIO_read(bio.get(), pem_str.data(), keylen);
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::Serialize): Could not read BIO");

    pem_str[keylen] = '\0';
    encoded = reinterpret_cast<char*>(pem_str.data());

    return true;
}

// -----------------------------------------------------------------
// Computes SHA256 hash of message.data(), signs with ECDSA privkey and
// returns ww::types::ByteArray containing raw binary data
// -----------------------------------------------------------------
bool signing::PrivateKey::SignMessage(
    const ww::types::ByteArray& message,
    ww::types::ByteArray& signature,
    HashFunctionType hash_function) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::SignMessage): Private key not initialized");

    // Hash, will throw exception on failure
    ww::types::ByteArray hash;
    hash_function(message, hash);

    // Then Sign
    crypto::ECDSA_SIG_ptr sig(ECDSA_do_sign(hash.data(), hash.size(), key_), ECDSA_SIG_free);
    ERROR_IF_NULL(sig, "Crypto Error (PrivateKey::SignMessage): Could not compute ECDSA signature");

    // These are pointers into the signature and do not need to be free'd after use
    const BIGNUM* rc = ECDSA_SIG_get0_r(sig.get());
    ERROR_IF_NULL(rc, "Crypto Error (PrivateKey::SignMessage): bad r value");

    const BIGNUM* sc = ECDSA_SIG_get0_s(sig.get());
    ERROR_IF_NULL(sc, "Crypto Error (PrivateKey::SignMessage): bad s value");

    crypto::BIGNUM_ptr s(BN_dup(sc), BN_free);
    ERROR_IF_NULL(s, "Crypto Error (PrivateKey::SignMessage): Could not dup BIGNUM for s");

    crypto::BIGNUM_ptr r(BN_dup(rc), BN_free);
    ERROR_IF_NULL(r, "Crypto Error (PrivateKey::SignMessage): Could not dup BIGNUM for r");

    crypto::BIGNUM_ptr ord(BN_new(), BN_free);
    ERROR_IF_NULL(ord, "Crypto Error (PrivateKey::SignMessage): Could not create BIGNUM for ord");

    crypto::BIGNUM_ptr ordh(BN_new(), BN_free);
    ERROR_IF_NULL(ordh, "Crypto Error (PrivateKey::SignMessage): Could not create BIGNUM for ordh");

    int res;

    res = EC_GROUP_get_order(EC_KEY_get0_group(key_), ord.get(), NULL);
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::SignMessage): Could not get order");

    res = BN_rshift(ordh.get(), ord.get(), 1);
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::SignMessage): Could not shft order BN");

    if (BN_cmp(s.get(), ordh.get()) >= 0)
    {
        res = BN_sub(s.get(), ord.get(), s.get());
        ERROR_IF(res <= 0, "Crypto Error (PrivateKey::SignMessage): Could not sub BNs");
    }

    res = ECDSA_SIG_set0(sig.get(), r.get(), s.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::SignMessage): Could not set r and s");

    // when we invoke ECDSA_SIG_set0 control of the allocated objects is passed
    // back to the signature and released when the signature is released so we
    // need to drop control from the unique_ptr objects we've been using
    r.release();
    s.release();

    signature.resize(i2d_ECDSA_SIG(sig.get(), nullptr));
    unsigned char* data = signature.data();

    res = i2d_ECDSA_SIG(sig.get(), &data);
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::SignMessage): Could not convert signatureto DER");

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool signing::PrivateKey::GetNumericKey(ww::types::ByteArray& numeric_key) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::GetNumericKey): Key not initialized");

    const BIGNUM *bn = EC_KEY_get0_private_key(key_);
    ERROR_IF_NULL(bn, "Crypto Error (PrivateKey::GetNumericKey) failed to retrieve the private key");

    numeric_key.resize(BN_num_bytes(bn));
    int res;

    res = BN_bn2bin(bn, numeric_key.data());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::GetNumericKey) failed to convert bignum");

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool signing::PrivateKey::DeriveKey(
    const ww::types::ByteArray& parent_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const ww::types::ByteArray& data,
    signing::PrivateKey& extended_key,
    ww::types::ByteArray& extended_chain_code) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::DeriveHardenedKey): Key not initialized");

    int res;

    // --------------- Setup the big number context  ---------------

    BN_CTX_ptr ctx(BN_CTX_new(), BN_CTX_free);
    ERROR_IF_NULL(ctx, "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to create BN context");

    // --------------- Get curve information ---------------

    const EC_GROUP *ec_group = EC_KEY_get0_group(key_);

    BIGNUM_ptr curve_order_ptr(BN_new(), BN_free);
    ERROR_IF_NULL(curve_order_ptr, "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to create curve order bignum");

    res = EC_GROUP_get_order(ec_group, curve_order_ptr.get(), ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to get curve order");

    // make sure the chain code is the correct size
    ERROR_IF(parent_chain_code.size() != BN_num_bytes(curve_order_ptr.get()), "Invalid parent chain code size");

    // --------------- Start the derivation process ----------------

    // First step is to build the data array to be hashed
    // BIP: HMAC-SHA512(Key = cpar, Data = 0x00 || ser256(kpar) || ser32(i)).

    const BIGNUM *parent_key_ptr = EC_KEY_get0_private_key(key_);

    // Next step is to compute the HMAC in order to derive the child key and chain code
    // BIP: Split I into two 32-byte sequences, IL and IR.
    ww::types::ByteArray child_key;
    ww::types::ByteArray child_chain_code;
    if (! DeriveChildKey(parent_chain_code, data, child_key, child_chain_code))
        return false;

    // The final step is to add the child key to the parent key to get the next extended key
    // BIP: The returned child key ki is parse256(IL) + kpar (mod n).
    BIGNUM_ptr child_key_ptr(BN_bin2bn((const unsigned char*)child_key.data(), child_key.size(), NULL), BN_free);
    ERROR_IF_NULL(child_key_ptr, "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to create child key bignum");

    res = BN_mod_add(
            child_key_ptr.get(), // destination
            child_key_ptr.get(),    // value 1
            parent_key_ptr, // value 2
            curve_order_ptr.get(),  // modulus
            ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to add child key to parent key");

    // Write the updated child key back to a byte array
    res = BN_bn2bin(child_key_ptr.get(), child_key.data());
    ERROR_IF(res <= 0, "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to convert child key to byte array");

    // --------------- Create the return values ----------------
    extended_key = signing::PrivateKey(curve_, child_key);
    extended_chain_code = child_chain_code;

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool signing::PrivateKey::DeriveHardenedKey(
    const ww::types::ByteArray& parent_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const std::string& path_element, // array of strings, path to the current key
    signing::PrivateKey& extended_key,
    ww::types::ByteArray& extended_chain_code) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::DeriveHardenedKey): Key not initialized");

    // Convert the parent key into a byte array
    ww::types::ByteArray parent_key;
    ERROR_IF(! GetNumericKey(parent_key), "Crypto Error (PrivateKey::DeriveHardenedKey): Failed to get parent key");

    ww::types::ByteArray data;
    data.push_back(0x00);  // this is part of the BIP32 specification for extended keys
    data.insert(data.end(), parent_key.begin(), parent_key.end());

    // Append the current context key to the material to be hashed
    size_t path_hash = std::hash<std::string>{}(path_element);
    path_hash = path_hash | 0x80000000; // this is part of the BIP32 specification for hardened keys
    auto ptr = reinterpret_cast<uint8_t*>(&path_hash);
    data.insert(data.end(), ptr, ptr + sizeof(size_t));

    return DeriveKey(parent_chain_code, data, extended_key, extended_chain_code);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool signing::PrivateKey::DeriveNormalKey(
    const ww::types::ByteArray& parent_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const std::string& path_element, // array of strings, path to the current key
    signing::PrivateKey& extended_key,
    ww::types::ByteArray& extended_chain_code) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PrivateKey::DeriveNormalKey): Key not initialized");

    signing::PublicKey public_key;
    ERROR_IF(! GetPublicKey(public_key), "Crypto Error (PrivateKey::DeriveNormalKey): Failed to get public key");

    // Convert the extended public key into a byte array, this is point(kpar)
    // Push the public key into the data array
    ww::types::ByteArray data;
    ERROR_IF(! public_key.GetNumericKey(data), "Crypto Error (PrivateKey::DeriveNormalKey): Failed to get numeric key");

    // Append the current context key to the material to be hashed, this is ser32(i)
    size_t path_hash = std::hash<std::string>{}(path_element);
    path_hash = path_hash & 0x7FFFFFFF; // this is part of the BIP32 specification for normal keys
    auto ptr = reinterpret_cast<uint8_t*>(&path_hash);
    data.insert(data.end(), ptr, ptr + sizeof(size_t));

    return DeriveKey(parent_chain_code, data, extended_key, extended_chain_code);
}
