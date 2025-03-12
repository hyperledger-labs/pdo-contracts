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
signing::PublicKey::PublicKey(const int curve, const ww::types::ByteArray& numeric_key) : Key(curve)
{
    InitializeFromNumericKey(numeric_key);
}

// -----------------------------------------------------------------
// Constructor from PrivateKey
// -----------------------------------------------------------------
signing::PublicKey::PublicKey(const signing::PrivateKey& privateKey)
{
    InitializeFromPrivateKey(privateKey);
}

// -----------------------------------------------------------------
// Constructor from PublicKey
// -----------------------------------------------------------------
signing::PublicKey::PublicKey(const signing::PublicKey& publicKey)
{
    InitializeFromPublicKey(publicKey);
}

// -----------------------------------------------------------------
// Move constructor
// -----------------------------------------------------------------
signing::PublicKey::PublicKey(signing::PublicKey&& publicKey)
{
    // when the publicKey does not have a key associated with it,
    // e.g. when publicKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    key_ = publicKey.key_;
    curve_ = publicKey.curve_;

    publicKey.key_ = nullptr;
}

// -----------------------------------------------------------------
// Constructor from encoded string
// -----------------------------------------------------------------
signing::PublicKey::PublicKey(const std::string& encoded) : Key(NID_undef)
{
    Deserialize(encoded);
}

// -----------------------------------------------------------------
// Destructor
signing::PublicKey::~PublicKey()
{
    ResetKey();
}  // signing::PublicKey::~PublicKey

// -----------------------------------------------------------------
void signing::PublicKey::ResetKey(void)
{
    // reset the the key, do not change the curve details
    if (key_)
        EC_KEY_free(key_);

    key_ = nullptr;
    curve_ = NID_undef;
}

// -----------------------------------------------------------------
// InitializeFromNumericKey
//
// This function initializes the public key from a numeric key. It is
// implemented as a separate function because WASM constructors cannot
// easily throw an exception when an error occurs.
// -----------------------------------------------------------------
bool signing::PublicKey::InitializeFromNumericKey(const ww::types::ByteArray& numeric_key)
{
    int res;

    crypto::BN_CTX_ptr b_ctx(BN_CTX_new(), BN_CTX_free);
    ERROR_IF_NULL(b_ctx, "Crypto Error (PublicKey::InitializeFromNumericKey): Cound not create BN context");

    EC_GROUP_ptr group(EC_GROUP_new_by_curve_name(curve_), EC_GROUP_clear_free);
    ERROR_IF_NULL(group, "Crypto Error (PublicKey::InitializeFromNumericKey): Cound not create group");

    EC_GROUP_set_point_conversion_form(group.get(), POINT_CONVERSION_COMPRESSED);

    EC_KEY_ptr public_key(EC_KEY_new(), EC_KEY_free);
    ERROR_IF_NULL(public_key, "Crypto Error (PublicKey::InitializeFromNumericKey): Cound not create public_key");

    res = EC_KEY_set_group(public_key.get(), group.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::InitializeFromNumericKey): Could not set EC_GROUP");

    EC_POINT_ptr point(EC_POINT_new(group.get()), EC_POINT_free);
    ERROR_IF_NULL(point, "Crypto Error (PublicKey::InitializeFromNumericKey): Cound not create point");

    res = EC_POINT_oct2point(group.get(), point.get(), numeric_key.data(), numeric_key.size(), b_ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::InitializeFromNumericKey): Cound not convert octet to point");

    res = EC_KEY_set_public_key(public_key.get(), point.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::InitializeFromNumericKey): Cound not set public key");

    key_ = public_key.get();
    public_key.release();

    return true;
}

// -----------------------------------------------------------------
// InitializeFromPrivateKey
//
// Initialize the public key from the private key. This function is
// necessary because WASM does not support constructors that can throw
// exceptions.
// -----------------------------------------------------------------
bool signing::PublicKey::InitializeFromPrivateKey(const signing::PrivateKey& privateKey)
{
    key_ = nullptr;
    curve_ = privateKey.curve_;

    // when the privateKey does not have a key associated with it,
    // e.g. when privateKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    if (privateKey)
    {
        int res;

        crypto::EC_KEY_ptr public_key(EC_KEY_new(), EC_KEY_free);
        ERROR_IF_NULL(public_key, "Crypto Error (PublicKey::InitializeFromPrivateKey): Could not create new public EC_KEY");

        crypto::EC_GROUP_ptr ec_group(EC_GROUP_new_by_curve_name(curve_), EC_GROUP_clear_free);
        ERROR_IF_NULL(ec_group, "Crypto Error (PublicKey::InitializeFromPrivateKey): Could not create EC_GROUP");

        EC_GROUP_set_point_conversion_form(ec_group.get(), POINT_CONVERSION_COMPRESSED);

        crypto::BN_CTX_ptr context(BN_CTX_new(), BN_CTX_free);
        ERROR_IF_NULL(context, "Crypto Error (PublicKey::InitializeFromPrivateKey): Could not create new CTX");

        res = EC_KEY_set_group(public_key.get(), ec_group.get());
        ERROR_IF(res <= 0, "Crypto Error (PublicKey::InitializeFromPrivateKey): Could not set EC_GROUP");

        const EC_POINT* p = EC_KEY_get0_public_key(privateKey.key_);
        ERROR_IF_NULL(p, "Crypto Error (PublicKey::InitializeFromPrivateKey): Could not create new EC_POINT");

        res = EC_KEY_set_public_key(public_key.get(), p);
        ERROR_IF(res <= 0, "Crypto Error (PublicKey::InitializeFromPrivateKey): Could not set public EC_KEY");

        key_ = public_key.get();
        public_key.release();
    }

    return true;
}

// -----------------------------------------------------------------
// InitializeFromPublicKey
//
// This function initializes the public key from another public key.
// -----------------------------------------------------------------
bool signing::PublicKey::InitializeFromPublicKey(const signing::PublicKey& publicKey)
{
    key_ = nullptr;
    curve_ = publicKey.curve_;

    // when the publicKey does not have a key associated with it,
    // e.g. when publicKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    if (publicKey)
    {
        key_ = EC_KEY_dup(publicKey.key_);
        ERROR_IF_NULL(key_, "Crypto Error (PublicKey::InitializeFromPublicKey): Could not copy public key");
    }

    return true;
}

// -----------------------------------------------------------------
// boolean conversion operator, returns true if there is a
// key associated with the object
signing::PublicKey::operator bool(void) const
{
    return key_ != nullptr;
}

// -----------------------------------------------------------------
// assignment operator overload
// ***** RETURN VALUE *****
// -----------------------------------------------------------------
signing::PublicKey& signing::PublicKey::operator=(
    const signing::PublicKey& publicKey)
{
    if (this == &publicKey)
        return *this;

    ResetKey();

    // when the publicKey does not have a key associated with it,
    // e.g. when publicKey.key_ == nullptr, we simply copy the
    // uninitialized state; the alternative is to throw and exception
    // with the assumption that uninitialized keys should not be assigned
    if (publicKey)
        key_ = EC_KEY_dup(publicKey.key_);

    curve_ = publicKey.curve_;

    return *this;
}

// -----------------------------------------------------------------
// Deserialize Digital Signature Public Key
// -----------------------------------------------------------------
bool signing::PublicKey::Deserialize(const std::string& encoded)
{
    ResetKey();

    crypto::BIO_ptr bio(BIO_new_mem_buf(encoded.c_str(), -1), BIO_free_all);
    ERROR_IF_NULL(bio, "Crypto Error (PublicKey::Deserialize): Could not create BIO");

    key_ = PEM_read_bio_EC_PUBKEY(bio.get(), NULL, NULL, NULL);
    ERROR_IF_NULL(key_, "Crypto Error (PublicKey::Deserialize): Could not deserialize public ECDSA key");

    curve_ = EC_GROUP_get_curve_name(EC_KEY_get0_group(key_));

    return true;
}

// -----------------------------------------------------------------
// Serialize Digital Signature Public Key
// -----------------------------------------------------------------
bool signing::PublicKey::Serialize(std::string& encoded) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PublicKey::Serialize): public key not initialized");

    crypto::BIO_ptr bio(BIO_new(BIO_s_mem()), BIO_free_all);
    ERROR_IF_NULL(bio, "Crypto Error (PublicKey::Serialize): Could not create BIO");

    int res;

    res = PEM_write_bio_EC_PUBKEY(bio.get(), key_);
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::Serialize): Could not serialize key");

    int keylen = BIO_pending(bio.get());

    ww::types::ByteArray pem_str(keylen + 1);

    res = BIO_read(bio.get(), pem_str.data(), keylen);
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::Serialize): Could not read BIO");

    pem_str[keylen] = '\0';
    encoded = reinterpret_cast<char*>(pem_str.data());

    return true;
}

// -----------------------------------------------------------------
// Verifies SHA256 ECDSA signature of message
// input signature ww::types::ByteArray contains raw binary data
// returns 1 if signature is valid, 0 if signature is invalid and -1 if there is
// an internal error
// ***** FIX HASH *****
// -----------------------------------------------------------------
int signing::PublicKey::VerifySignature(
    const ww::types::ByteArray& message,
    const ww::types::ByteArray& signature,
    HashFunctionType hash_function) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PublicKey::VerifySignature): public key not initialized");

    ww::types::ByteArray hash;
    ERROR_IF(! hash_function(message, hash), "Crypto Error (PublicKey::VerifySignature): Could not hash message");

    // Decode signature B64 -> DER -> ECDSA_SIG, must be null terminated
    ERROR_IF(signature.back() != 0, "Crypto Error (PublicKey::VerifySignature): Invalid signature format");

   const unsigned char* der_SIG = (const unsigned char*)signature.data();
    crypto::ECDSA_SIG_ptr sig(
        d2i_ECDSA_SIG(NULL, (const unsigned char**)(&der_SIG), signature.size()), ECDSA_SIG_free);
    if (sig == nullptr)
        return -1;

    // Verify
    // ECDSA_do_verify() returns 1 for a valid sig, 0 for an invalid sig and -1 on error
    return ECDSA_do_verify(hash.data(), hash.size(), sig.get(), key_);
}  // signing::PublicKey::VerifySignature

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool signing::PublicKey::GetNumericKey(ww::types::ByteArray& numeric_key) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PublicKey::GetNumericKey): Key not initialized");

    crypto::BN_CTX_ptr b_ctx(BN_CTX_new(), BN_CTX_free);
    ERROR_IF_NULL(b_ctx, "Crypto Error (PublicKey::GetNumericKey): Cound not create BN context");

    const EC_GROUP *group = EC_KEY_get0_group(key_);
    const EC_POINT *point = EC_KEY_get0_public_key(key_);

    int converted_size;

    // this call just returns the size of the buffer that is necessary
    converted_size = EC_POINT_point2oct(group, point, POINT_CONVERSION_COMPRESSED, NULL, 0, b_ctx.get());
    numeric_key.resize(converted_size);

    // this call writes the data to the numeric_key
    int res;
    res = EC_POINT_point2oct(
        group, point, POINT_CONVERSION_COMPRESSED, numeric_key.data(), numeric_key.size(), b_ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::GetNumericKey): Cound not convert point to octet");

    return true;
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool signing::PublicKey::DerivePublicKey(
    const ww::types::ByteArray& parent_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const std::string& path_element, // path to the current key
    signing::PublicKey& extended_key,
    ww::types::ByteArray& extended_chain_code) const
{
    ERROR_IF_NULL(key_, "Crypto Error (PublicKey::DerivePublicKey): Key not initialized");

    int res;

    // --------------- Setup the big number context  ---------------

    BN_CTX_ptr ctx(BN_CTX_new(), BN_CTX_free);
    ERROR_IF_NULL(ctx, "Crypto Error (PublicKey::DerivePublicKey): Failed to create BN context");

    // --------------- Get curve information ---------------

    const EC_GROUP *ec_group = EC_KEY_get0_group(key_);

    BIGNUM_ptr curve_order_ptr(BN_new(), BN_free);
    ERROR_IF_NULL(curve_order_ptr, "Crypto Error (PublicKey::DerivePublicKey): Failed to create curve order bignum");

    res = EC_GROUP_get_order(ec_group, curve_order_ptr.get(), ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::DerivePublicKey): Failed to get curve order");

    // make sure the chain code is the correct size
    ERROR_IF(parent_chain_code.size() != BN_num_bytes(curve_order_ptr.get()), "Invalid parent chain code size");

    // --------------- Start the derivation process ----------------

    // First step is to build the data array to be hashed
    // BIP: HMAC-SHA512(Key = cpar, Data = serP(Kpar) || ser32(i)).

    // Convert the extended public key into a byte array, this is point(kpar)
    // Push the public key into the data array
    ww::types::ByteArray data;
    ERROR_IF(! GetNumericKey(data), "Crypto Error (PublicKey::DerivePublicKey): Failed to get numeric key");

    // Append the current context key to the material to be hashed, this is ser32(i)
    size_t path_hash = std::hash<std::string>{}(path_element);
    path_hash = path_hash & 0x7FFFFFFF; // this is part of the BIP32 specification for normal keys
    auto ptr = reinterpret_cast<uint8_t*>(&path_hash);
    data.insert(data.end(), ptr, ptr + sizeof(size_t));

    // Next step is to compute the HMAC in order to derive the child key and chain code
    // BIP: Split I into two 32-byte sequences, IL and IR.
    ww::types::ByteArray child_key;
    ww::types::ByteArray child_chain_code;
    if (! DeriveChildKey(parent_chain_code, data, child_key, child_chain_code))
        return false;

    // The final step is to add the child key to the parent key to get the next extended key
    // BIP:  Ki is point(parse256(IL)) + Kpar

    const EC_POINT *ec_point = EC_KEY_get0_public_key(key_);

    // convert child_key bytearray to a point
    crypto::EC_POINT_ptr child_key_point_ptr(EC_POINT_new(ec_group), EC_POINT_free);
    ERROR_IF_NULL(child_key_point_ptr, "Crypto Error (PublicKey::DerivePublicKey): Failed to create child key point");

    res = EC_POINT_oct2point(ec_group, child_key_point_ptr.get(), child_key.data(), child_key.size(), ctx.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::DerivePublicKey): Failed to convert child key to point");

    // add the child key point to the parent key point
    res = EC_POINT_add(ec_group, child_key_point_ptr.get(), ec_point, child_key_point_ptr.get(), ctx.get());

    // --------------- Create the return values ----------------
    extended_key.curve_ = curve_;
    res = EC_KEY_set_public_key(extended_key.key_, child_key_point_ptr.get());
    ERROR_IF(res <= 0, "Crypto Error (PublicKey::DerivePublicKey): Failed to set public key");

    extended_chain_code = child_chain_code;

    return true;
}
