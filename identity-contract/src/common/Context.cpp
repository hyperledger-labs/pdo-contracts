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
#include "identity/common/Context.h"

bool ww::identity::BaseVerifyingContext::set_chain_code(const ww::types::ByteArray& chain_code)
{
    ERROR_IF(chain_code.size() != EXTENDED_KEY_SIZE, "Invalid chain code size");
    ERROR_IF_NOT(ww::crypto::b64_encode(chain_code, chain_code_), "Failed to encode chain code");

    return true;
}

bool ww::identity::BaseVerifyingContext::get_chain_code(ww::types::ByteArray& chain_code) const
{
    ERROR_IF_NOT(ww::crypto::b64_decode(chain_code_, chain_code),
                 "Failed to decode chain code; %s", chain_code_.c_str());

    return true;
}

bool ww::identity::BaseVerifyingContext::set_public_key(const pdo_contracts::crypto::signing::PublicKey& key)
{
    ERROR_IF_NOT(key.Serialize(public_key_), "failed to serialize public key");

    return true;
}

bool ww::identity::BaseVerifyingContext::get_public_key(pdo_contracts::crypto::signing::PublicKey& key) const
{
    ERROR_IF_NOT(key.Deserialize(public_key_), "failed to deserialize public key; %s", public_key_.c_str());

    return true;
}

bool ww::identity::BaseSigningContext::set_private_key(const pdo_contracts::crypto::signing::PrivateKey& key)
{
    ERROR_IF_NOT(key.Serialize(private_key_), "failed to serialize private key");

    pdo_contracts::crypto::signing::PublicKey public_key(key);
    ERROR_IF_NOT(public_key.Serialize(public_key_), "failed to serialize public key");

    return true;
}

bool ww::identity::BaseSigningContext::get_private_key(pdo_contracts::crypto::signing::PrivateKey& key) const
{
    ERROR_IF_NOT(key.Deserialize(private_key_), "Failed to deserialize private key; %s", private_key_.c_str());
    return true;
}
