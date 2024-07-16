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

#include "Util.h"
#include "Secret.h"
#include "exchange/token_object.h"
#include "exchange/issuer_authority_base.h"


#define HFMODEL_TO_INITIALIZE_PARAM_SCHEMA               \
    "{"                                         \
        SCHEMA_KW(hf_auth_token, "") ","                 \
        SCHEMA_KW(hf_endpoint_url, "") ","                 \
        SCHEMA_KW(fixed_model_params, "") ","                 \
        SCHEMA_KW(user_inputs_schema, "") ","                 \
        SCHEMA_KW(payload_type, "") ","                 \
        SCHEMA_KW(hfmodel_usage_info, "") ","          \
        SCHEMA_KW(max_use_count, 0) ","          \
        SCHEMA_KW(ledger_verifying_key, "") ","           \
        SCHEMA_KWS(initialization_package, CONTRACT_SECRET_SCHEMA) ","          \
        SCHEMA_KWS(asset_authority_chain, ISSUER_AUTHORITY_CHAIN_SCHEMA)\
    "}"

#define MODEL_INFO_SCHEMA               \
    "{"                                         \
        SCHEMA_KW(fixed_model_params, "") ","                 \
        SCHEMA_KW(user_inputs_schema, "") ","                 \
        SCHEMA_KW(payload_type, "") ","                 \
        SCHEMA_KW(hfmodel_usage_info, "") ","                 \
        SCHEMA_KW(max_use_count, "")                  \
    "}"

#define USE_MODEL_SCHEMA               \
    "{"                                         \
        SCHEMA_KW(kvstore_encryption_key, "") ","                 \
        SCHEMA_KW(kvstore_root_block_hash, "") ","                 \
        SCHEMA_KW(kvstore_input_key, "") ","                 \
        SCHEMA_KW(user_inputs, "")                 \
    "}"

#define GET_CAPABILITY_SCHEMA  \
    "{"                                                 \
        SCHEMA_KW(ledger_signature,"")               \
   "}"


#define GENERATE_CAPABILITY_SCHEMA  \
   "{"                                         \
        SCHEMA_KW(kvstore_encryption_key, "") ","                 \
        SCHEMA_KW(kvstore_root_block_hash, "") ","                 \
        SCHEMA_KW(kvstore_input_key, "") ","                 \
        SCHEMA_KW(hf_auth_token, "") ","                 \
        SCHEMA_KW(hf_endpoint_url, "") ","                 \
        SCHEMA_KW(payload_type, "") ","                 \
        SCHEMA_KW(fixed_model_params, "") ","                 \
        SCHEMA_KW(user_inputs_schema, "") ","                 \
        SCHEMA_KW(user_inputs, "")                 \
    "}"



namespace ww
{
namespace hfmodels
{
namespace token_object
{
    // methods
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool get_model_info(const Message& msg, const Environment& env, Response& rsp);
    bool use_model(const Message& msg, const Environment& env, Response& rsp);
    bool get_capability(const Message& msg, const Environment& env, Response& rsp);
}; // token_object
}; // hfmodels
}; // ww
