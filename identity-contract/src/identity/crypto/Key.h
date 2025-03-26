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

#pragma once

#include <string>
#include <openssl/ec.h>

#include "Cryptography.h"
#include "Types.h"

#define CHUNK_HMAC_FUNCTION pdo_contracts::crypto::SHA384HMAC
#define EXTENDED_CHUNK_SIZE 24
#define DEFAULT_CURVE_NID NID_secp384r1

namespace pdo_contracts
{
namespace crypto
{
    namespace signing
    {
        class Key
        {
        protected:
            EC_KEY* key_;
            int curve_;

            static bool DeriveChildKey(
                const ww::types::ByteArray& extended_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
                const ww::types::ByteArray& data,                // data to be hashed with HMAC
                ww::types::ByteArray& child_key,
                ww::types::ByteArray& child_chain_code);

        public:
            Key(int curve = DEFAULT_CURVE_NID) {
                key_ = nullptr;
                curve_ = curve;
            };
        };
    }
}
}
