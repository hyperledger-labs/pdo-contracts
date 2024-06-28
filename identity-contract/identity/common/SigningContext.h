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

#pragma once
#include <string>
#include <vector>

#include "Util.h"
#include "Value.h"

#include "exchange/common/Common.h"

#define SIGNING_CONTEXT_SCHEMA                  \
    "{"                                         \
        SCHEMA_KW(extensible, true) ","         \
        SCHEMA_KW(description, "") ","          \
        SCHEMA_KW(subcontexts, [ "" ])          \
    "}"

// when the extensible flag is true:
//   * all subcontexts are valid
//   * no subcontext registration is allowed
//   * subcontexts field is empty

// when the extensible flag is false:
//   * only registered subcontexts are valid
//   * subcontext registration is allowed
//   * subcontext field contains a list of registered subcontexts

// algorithm to determine if path [p1, p2, .. pn] is valid:
// context = root context
// foreach p in path :
//   if context is extensible :
//     return true
//   if p is not in context.subcontexts :
//     return false
//   context is context.subcontext[p]
// return true

// we need to find a signing context based on the longest prefix. the easiest way
// to do that is to have a signing context for each element of the list.

// subcontexts is necessary because the extensible flag must be inherited correctly
// by any new context that is created below this one

// several ways to do this...
// * build the key when the context is created and store it here
// * store the full context path here and reconstruct the key from this context
// *

#define USE_SECP384R1

// https://en.wikipedia.org/wiki/P-384
#ifdef USE_SECP384R1
#define EXTENDED_KEY_SIZE	48
#define BIGNUM_TYPE		ww::types::BigNum384
#define HASH_FUNCTION		ww::crypto::hash::sha384_hash
#define CURVE_ORDER		"//////////////////////////////////////////7/////AAAAAAAAAAD/////"
#endif

namespace ww
{
namespace identity
{
    class SigningContext : public ww::exchange::SerializeableObject
    {
        friend class SigningContextManager;

    protected:
        bool contains(const std::string& name) const;

        bool extensible_;                              // extensible implies no subcontexts
        std::string description_;                      // human readable description
        std::vector<std::string> subcontexts_;         // registered subcontexts

    public:
        static bool sign_message(
            const ww::types::ByteArray& root_key,
            const std::vector<std::string>& context_path,
            const ww::types::ByteArray& message,
            ww::types::ByteArray& signature);

        static bool verify_signature(
            const ww::types::ByteArray& root_key,
            const std::vector<std::string>& context_path,
            const ww::types::ByteArray& message,
            const ww::types::ByteArray& signature);

        static bool generate_keys(
            const ww::types::ByteArray& root_key, // base64 encoded representation of 48 byte random array
            const std::vector<std::string>& context_path,
            std::string& private_key,     // PEM encoded ECDSA private and public keys
            std::string& public_key);

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, SIGNING_CONTEXT_SCHEMA);
        }

        bool deserialize(const ww::value::Object& request);
        bool serialize(ww::value::Value& serialized_request) const;

        SigningContext(
            const std::vector<std::string>& subcontexts,
            const bool extensible,
            const std::string& description)
            : subcontexts_(subcontexts), extensible_(extensible), description_(description) { };

        SigningContext(
            const bool extensible,
            const std::string& description)
            : extensible_(extensible), description_(description)
            { subcontexts_.resize(0); };

        SigningContext(void) : SigningContext(false, "") { };
    };

}; // identity
}  // ww
