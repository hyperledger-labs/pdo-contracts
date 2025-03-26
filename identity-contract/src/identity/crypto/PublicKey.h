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

#include "identity/crypto/Crypto.h"
#include "identity/crypto/Key.h"

#include "Types.h"

namespace pdo_contracts
{
namespace crypto
{
    namespace signing
    {
        class PrivateKey;

        class PublicKey: public Key
        {
        private:
            void ResetKey(void);
            bool InitializeFromNumericKey(const ww::types::ByteArray& numeric_key);
            bool InitializeFromPrivateKey(const PrivateKey& privateKey);
            bool InitializeFromPublicKey(const PublicKey& publicKey);

        public:
            PublicKey(const int curve = NID_undef) : Key(curve) {};
            PublicKey(const int curve, const ww::types::ByteArray& numeric_key);
            PublicKey(const PrivateKey& privateKey);
            PublicKey(const PublicKey& publicKey);
            PublicKey(PublicKey&& publicKey);
            PublicKey(const std::string& encoded);

            ~PublicKey();

            PublicKey& operator=(const PublicKey& publicKey);
            operator bool() const;

            bool Deserialize(const std::string& encoded);
            bool Serialize(std::string& encoded) const;

            bool VerifySignature(
                const ww::types::ByteArray& message,
                const ww::types::ByteArray& signature,
                HashFunctionType hash_function) const;

            bool GetNumericKey(ww::types::ByteArray& numeric_key) const;

            bool DerivePublicKey(
                const ww::types::ByteArray& parent_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
                const std::string& path_element,
                PublicKey& extended_key,
                ww::types::ByteArray& extended_chain_code) const;

        };
    }
}
}
