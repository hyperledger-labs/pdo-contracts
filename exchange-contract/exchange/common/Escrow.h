/* Copyright 2019 Intel Corporation
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

#include "Value.h"

#include "Common.h"
#include "Environment.h"
#include "StateReference.h"

#include "Asset.h"

#define ESCROW_RELEASE_SCHEMA "{"                                       \
    "\"escrow_agent_state_reference\":" STATE_REFERENCE_SCHEMA ","      \
    SCHEMA_KW(escrow_agent_signature,"") ","                            \
    SCHEMA_KW(escrow_agent_identity,"") ","                             \
    SCHEMA_KW(count,0)                                                  \
    "}"

#define ESCROW_CLAIM_SCHEMA "{"                                         \
    SCHEMA_KW(old_owner_identity,"") ","                                \
    "\"escrow_agent_state_reference\":" STATE_REFERENCE_SCHEMA ","      \
    SCHEMA_KW(escrow_agent_signature,"") ","                            \
    SCHEMA_KW(escrow_agent_identity,"") ","                             \
    SCHEMA_KW(count,0)                                                  \
    "}"

namespace ww
{
namespace exchange
{
    // -----------------------------------------------------------------
    class EscrowBase : public ww::exchange::SerializeableObject
    {
    protected:
        EscrowBase(void);

        EscrowBase(
            const Environment& env,
            const std::string& escrow_agent_identity,
            const unsigned int count = 0)
            : escrow_agent_state_reference_(env), escrow_agent_identity_(escrow_agent_identity), count_(count)
        {};

        // Escrow methods
        bool verify_signature(
            const std::string& serialized) const;

        bool sign(
            const std::string& serialized,
            const std::string& escrow_agent_signing_key);

    public:
        ww::value::StateReference escrow_agent_state_reference_;
        std::string encoded_escrow_agent_signature_;
        std::string escrow_agent_identity_; /* escrow agent's verifying key */
        unsigned int count_;
    };

    // -----------------------------------------------------------------
    class EscrowRelease : public ww::exchange::EscrowBase
    {
    private:
        bool serialize_for_signing(
            const ww::exchange::Asset& asset,
            std::string& serialized) const;

    public:
        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, ESCROW_RELEASE_SCHEMA);
        }

        bool deserialize(const ww::value::Object& request);
        bool serialize(ww::value::Value& serialized_request) const;

        // EscrowRequest methods
        bool verify_signature(
            const ww::exchange::Asset& asset) const;

        bool sign(
            const ww::exchange::Asset& asset,
            const std::string& escrow_agent_signing_key);

        EscrowRelease(
            const Environment& env,
            const std::string& escrow_agent_identity,
            const unsigned int count = 0)
            : EscrowBase(env, escrow_agent_identity, count)
        {};

        EscrowRelease(void);
    };

    // -----------------------------------------------------------------
    class EscrowClaim : public ww::exchange::EscrowBase
    {
    private:
        bool serialize_for_signing(
            const ww::exchange::Asset& asset,
            const std::string& new_owner_identity,
            std::string& serialized) const;

    public:
        std::string old_owner_identity_;

        // SerializeableObject virtual methods
        static bool verify_schema(const ww::value::Object& deserialized_object)
        {
            return ww::exchange::SerializeableObject::verify_schema_actual(
                deserialized_object, ESCROW_CLAIM_SCHEMA);
        }

        bool deserialize(const ww::value::Object& request);
        bool serialize(ww::value::Value& serialized_request) const;

        // EscrowClaim methods
        bool verify_signature(
            const ww::exchange::Asset& asset,
            const std::string& new_owner_identity) const;

        bool sign(
            const ww::exchange::Asset& asset,
            const std::string& new_owner_identity,
            const std::string& escrow_agent_signing_key);

        EscrowClaim(
            const Environment& env,
            const std::string& escrow_agent_identity,
            const unsigned int count = 0)
            : EscrowBase(env, escrow_agent_identity, count)
        {};

        EscrowClaim(void);
    };

};
}
