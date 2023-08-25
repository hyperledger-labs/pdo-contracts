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

#include <string>

#include "Util.h"

#include "common/AssetRequest.h"
#include "common/AuthoritativeAsset.h"

#define EXCH_INITIALIZE_PARAM_SCHEMA                                    \
    "{"                                                                 \
        SCHEMA_KWS(asset_request, ASSET_REQUEST_SCHEMA) ","             \
        SCHEMA_KWS(offered_authoritative_asset, AUTHORITATIVE_ASSET_SCHEMA) \
    "}"

#define EXCHANGE_ASSET_PARAM_SCHEMA                                     \
    "{"                                                                 \
        SCHEMA_KWS(exchanged_authoritative_asset, AUTHORITATIVE_ASSET_SCHEMA) \
    "}"

#define RELEASE_ASSET_PARAM_SCHEMA                                      \
    "{"                                                                 \
        SCHEMA_KWS(escrowed_authoritative_asset,AUTHORITATIVE_ASSET_SCHEMA) \
    "}"

namespace ww
{
namespace exchange
{
namespace exchange
{
    bool initialize_contract(const Environment& env);
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool cancel_exchange(const Message& msg, const Environment& env, Response& rsp);
    bool cancel_exchange_attestation(const Message& msg, const Environment& env, Response& rsp);
    bool examine_offered_asset(const Message& msg, const Environment& env, Response& rsp);
    bool examine_requested_asset(const Message& msg, const Environment& env, Response& rsp);
    bool exchange_asset(const Message& msg, const Environment& env, Response& rsp);
    bool claim_exchanged_asset(const Message& msg, const Environment& env, Response& rsp);
    bool claim_offered_asset(const Message& msg, const Environment& env, Response& rsp);
    bool release_asset(const Message& msg, const Environment& env, Response& rsp);
}; // exchange
}; // exchange
}; // ww
