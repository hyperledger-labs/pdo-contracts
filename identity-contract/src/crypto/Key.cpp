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

#include "Types.h"

#include "exchange/common/Common.h"

#include "identity/crypto/Crypto.h"
#include "identity/crypto/Key.h"

namespace signing = pdo_contracts::crypto::signing;

// -----------------------------------------------------------------
// DeriveChildKey
//
// This function is used to derive a child key and chain code from an
// extended key.  The extended chain code normally serves as the key
// in the HMAC function. However, to accommodate longer keys, the
// extended chain code is split into segments, each of which is used
// as a key to compute an HMAC.The HMAC is then split into two halves,
// the first half is used as the child key and the second half is used
// as the child chain code.
// -----------------------------------------------------------------
bool signing::Key::DeriveChildKey(
    const ww::types::ByteArray& extended_chain_code, // array of random bytes, EXTENDED_KEY_SIZE
    const ww::types::ByteArray& data,                // data to be hashed with HMAC
    ww::types::ByteArray& child_key,
    ww::types::ByteArray& child_chain_code)
{
    // empty out anything that is in the arrays
    child_key.resize(0);
    child_chain_code.resize(0);

    for (int i = 0; i < extended_chain_code.size() / EXTENDED_CHUNK_SIZE; i++)
    {
        const size_t seg_start = i * EXTENDED_CHUNK_SIZE;
        const size_t seg_end = (i + 1) * EXTENDED_CHUNK_SIZE;

        // Pull out the segment of the chain code to use for this iteration
        ww::types::ByteArray chain_code_segment(
            extended_chain_code.begin() + seg_start, extended_chain_code.begin() + seg_end);

        // Compute the HMAC, this will give us a chunk that can be split and
        // put into a key and the chaincode
        ww::types::ByteArray hmac;
        ERROR_IF(! CHUNK_HMAC_FUNCTION(data, chain_code_segment, hmac), "HMAC failed");
        ERROR_IF(hmac.size() != 2 * EXTENDED_CHUNK_SIZE, "HMAC returned the wrong size");

        // Put this chunk into the child key and chain code
        child_key.insert(child_key.end(), hmac.begin(), hmac.begin() + EXTENDED_CHUNK_SIZE);
        child_chain_code.insert(child_chain_code.end(), hmac.begin() + EXTENDED_CHUNK_SIZE, hmac.end());
    }

    return true;
}
