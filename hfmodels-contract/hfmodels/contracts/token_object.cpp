/* Copyright 2024 Intel Corporation
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

#include <string>
#include <stddef.h>
#include <stdint.h>

#include "Dispatch.h"

#include "Cryptography.h"
#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Types.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/attestation.h"
#include "contract/base.h"
#include "exchange/token_object.h"
#include "hfmodels/token_object.h"


static KeyValueStore hfmodel_TO_store("hfmodel_TO_store");
static const std::string hfmodel_auth_token_KEY("hfmodel_auth_token");
static const std::string hfmodel_endpoint_url_KEY("hfmodel_endpoint_url");
static const std::string hfmodel_fixed_params_KEY("hfmodel_fixed_params_json_string");
static const std::string hfmodel_user_inputs_schema_KEY("hfmodel_user_inputs_schema");
static const std::string hfmodel_request_payload_type_KEY("hfmodel_request_payload_type");
static const std::string hfmodel_usage_info_KEY("hfmodel_usage_info");
static const std::string hfmodel_max_use_count_KEY("hfmodel_max_use_count");
static const std::string hfmodel_current_use_count_KEY("hfmodel_current_use_count");

static const std::string model_use_capability_kv_store_encryption_key_KEY("model_use_capability_kv_store_encryption_key");
static const std::string model_use_capability_kv_store_root_block_hash_KEY("model_use_capability_kv_store_root_block_hash");
static const std::string model_use_capability_kv_store_input_key_KEY("model_use_capability_kv_store_input_key");
static const std::string model_use_capability_user_inputs_KEY("model_use_capability_user_inputs"); 


// -----------------------------------------------------------------
// METHOD: initialize
//
// 1. Store model owner's authentication token that will be required to invoke Inference API. This is secret and shall never
//    be exposed to anyone other than the model owner.
// 2. Store HF endpoint URL that will be used to invoke the Inference API. This is secret and shall never be exposed to anyone 
//    other than the model owner. 
// 3. Store any fixed model parameters required to invoke Inference API. The model parameters is stored as a JSON string, not parsed by the TO. 
//    The guardian will parse the JSON string while invoking the inference API. There is no schema check. HF API server will return error
//    if the parameters are not correct.
// 4. Store the payload type for the HF model request. Support types are json and binary. Use json while working with language models, 
//    and binary while working with image/audio models. If payload type is binary, the input data must be first send to the key_value 
//    store attached to the guardian. If payload type is json, use user_inputs_schema to specify the schema for the input data.
//    The fixed model model parameters is used only when the payload type is json. Otherwise it is ignored by the guardian.
//    See https://huggingface.co/docs/api-inference/en/detailed_parameters for examples. When payload type is json, the guardian
//    will check user_inputs_schema to ensure that the input data is in the correct format before invoking the inference API.
// 5. Specify limit on the number of times the model can be used. Each use of the model will decrement the limit.
// 6. Store any other model metadata useful for the TO to understand how to use the model. Stored as string
//   
//   Note that the token object is intentionally kept generic and not hard-coded to any specific model. 
// -------------------------------------------------------------------------------------------------------------
bool ww::hfmodels::token_object::initialize(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(HFMODEL_TO_INITIALIZE_PARAM_SCHEMA), 
        "invalid request, missing required parameters for HF model token object initialize");
    

    //Get the params to be stored in hfmodel_TO_store
    const std::string hfmodel_auth_token_value(msg.get_string("hf_auth_token"));
    const std::string hfmodel_endpoint_url_value(msg.get_string("hf_endpoint_url"));
    const std::string hfmodel_fixed_params_value(msg.get_string("fixed_model_params"));
    const std::string hfmodel_user_inputs_schema_value(msg.get_string("user_inputs_schema"));
    const std::string hfmodel_request_payload_type_value(msg.get_string("payload_type"));
    const std::string hfmodel_usage_info_value(msg.get_string("hfmodel_usage_info"));
    const uint32_t hfmodel_max_use_count_value = (uint32_t) msg.get_number("max_use_count");

    //Store params from msg in hfmodel_TO_store
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_auth_token_KEY, hfmodel_auth_token_value), "failed to store hfmodel_auth_token");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_endpoint_url_KEY, hfmodel_endpoint_url_value), "failed to store hfmodel_endpoint_url");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_fixed_params_KEY, hfmodel_fixed_params_value), "failed to store hfmodel_fixed_params");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_user_inputs_schema_KEY, hfmodel_user_inputs_schema_value), "failed to store hfmodel_user_inputs_schema");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_request_payload_type_KEY, hfmodel_request_payload_type_value), "failed to store hfmodel_request_payload_type");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_usage_info_KEY, hfmodel_usage_info_value), "failed to store hfmodel_usage_info");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_max_use_count_KEY, hfmodel_max_use_count_value), "failed to store hfmodel_max_use_count");

    //Set current use count to 0
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_current_use_count_KEY, (uint32_t) 0), "failed to store hfmodel_current_use_count");
    
    // Do the rest of the initialization of the token object via the initialize method in the exchange contract
    ww::value::Structure to_message(TO_INITIALIZE_PARAM_SCHEMA);

    const std::string ledger_verifying_key(msg.get_string("ledger_verifying_key"));
    ww::value::Object initialization_package;
    msg.get_value("initialization_package", initialization_package);
    ww::value::Object asset_authority_chain;
    msg.get_value("asset_authority_chain", asset_authority_chain);

    ASSERT_SUCCESS(rsp, to_message.set_string("ledger_verifying_key", ledger_verifying_key.c_str()), "unexpected error: failed to set the parameter");
    ASSERT_SUCCESS(rsp, to_message.set_value("initialization_package", initialization_package), "unexpected error: failed to set the parameter");
    ASSERT_SUCCESS(rsp, to_message.set_value("asset_authority_chain", asset_authority_chain), "unexpected error: failed to set the parameter");

    return ww::exchange::token_object::initialize(to_message, env, rsp);
}



// -----------------------------------------------------------------
// METHOD: get_model_info
//
// Return fixed model parameters, schema for user-specified model parameters, and 
// model metadata useful for the TO to understand how to use the model required to invoke Inference API. 
// Method is public, and can be invoked by PDO user.
// note that we are not returning the "remaining use count" as part of the model info.
// ideally a prospective token buyer would like access to "remaining use count" before purchasing the token. 
// In such a case, ideally such information shall be provided only after escrow of payment for the token is done.
// Left for future enhancement.
// -----------------------------------------------------------------

bool ww::hfmodels::token_object::get_model_info(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_INITIALIZED(rsp);
    ww::value::Structure v(MODEL_INFO_SCHEMA);

    // Get the payload type
    std::string hfmodel_request_payload_type_string;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_request_payload_type_KEY, hfmodel_request_payload_type_string), "failed to retrieve hfmodel_request_payload_type");
    ASSERT_SUCCESS(rsp, v.set_string("payload_type", hfmodel_request_payload_type_string.c_str()), "failed to set return value for payload_type");

    // Get the fixed model parameters
    std::string hfmodel_fixed_params_string;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_fixed_params_KEY, hfmodel_fixed_params_string), "failed to retrieve hfmodel_fixed_params");
    ASSERT_SUCCESS(rsp, v.set_string("fixed_model_params", hfmodel_fixed_params_string.c_str()), "failed to set return value for hfmodel_fixed_params");

    // Get the schema for user-specified inputs (used only when payload type is json)
    std::string hfmodel_user_inputs_schema_string;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_user_inputs_schema_KEY, hfmodel_user_inputs_schema_string), "failed to retrieve hfmodel_user_inputs_schema");
    ASSERT_SUCCESS(rsp, v.set_string("user_inputs_schema", hfmodel_user_inputs_schema_string.c_str()), "failed to set return value for hfmodel_user_inputs_schema");

    // Get the model metadata
    std::string hfmodel_usage_info_string;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_usage_info_KEY, hfmodel_usage_info_string), "failed to retrieve hfmodel_usage_info");
    ASSERT_SUCCESS(rsp, v.set_string("hfmodel_usage_info", hfmodel_usage_info_string.c_str()), "failed to set return value for hfmodel_usage_info");

    // Get the max use count
    uint32_t hfmodel_max_use_count_value;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_max_use_count_KEY, hfmodel_max_use_count_value), "failed to retrieve hfmodel_max_use_count");
    ASSERT_SUCCESS(rsp, v.set_number("max_use_count", hfmodel_max_use_count_value), "failed to set return value for max_use_count");

    return rsp.value(v, false);

}


// -----------------------------------------------------------------
// METHOD: use_model
//
// 1.  Save the parameters required to generate a use_model capability to kvs, increments the current use count, and returns the call
//     Capability is calculated and returned once proof of commit of state is presented (via the get_capability method).
// 2. Inputs:
//        kvstore_encryption_key
//        kvstore_root_block_hash
//        kvstore_input_key
//        user_inputs
// The first 3 parameters provide flexibility to use large inputs for the model via the kv_store attached to the guardian. 
// Only TO may invoke method
// -----------------------------------------------------------------
bool ww::hfmodels::token_object::use_model(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(USE_MODEL_SCHEMA), "invalid request, missing required parameters");

    const std::string kvstore_encryption_key(msg.get_string("kvstore_encryption_key"));
    const std::string kvstore_root_block_hash(msg.get_string("kvstore_root_block_hash"));
    const std::string kvstore_input_key(msg.get_string("kvstore_input_key"));
    const std::string user_inputs(msg.get_string("user_inputs"));

    // check that current count <  max count. Increment the current count.
    // Note that we use < instead of <= since current count starts at 0.
    uint32_t hfmodel_current_use_count_value;
    uint32_t hfmodel_max_use_count_value;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_current_use_count_KEY, hfmodel_current_use_count_value), "failed to retrieve hfmodel_current_use_count");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_max_use_count_KEY, hfmodel_max_use_count_value), "failed to retrieve hfmodel_max_use_count");
    ASSERT_SUCCESS(rsp, hfmodel_current_use_count_value < hfmodel_max_use_count_value, "max use count is reached, cannot use model");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(hfmodel_current_use_count_KEY, hfmodel_current_use_count_value + 1), "failed to update hfmodel_current_use_count");
 
    // store the parameters required to generate a use_model capability
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(model_use_capability_kv_store_encryption_key_KEY, kvstore_encryption_key), "failed to store model_use_capability_kv_store_enc_key");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(model_use_capability_kv_store_root_block_hash_KEY, kvstore_root_block_hash), "failed to store model_use_capability_kv_store_hash");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(model_use_capability_kv_store_input_key_KEY, kvstore_input_key), "failed to store model_use_capability_kv_store_input_key");
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.set(model_use_capability_user_inputs_KEY, user_inputs), "failed to store model_use_capability_user_inputs");
    
    return rsp.success(true);
}


// -----------------------------------------------------------------
// METHOD: get_capability
//
// Check proof of commit, calculate/return capability. 
// Only TO may invoke method. It is currently possible for the TO to ask for a past capability
// even after token transfer. This is a feature, not a bug. The justification is that 
// any new owner is only getting access to "unused uses" of the model.
// -----------------------------------------------------------------

bool ww::hfmodels::token_object::get_capability(
    const Message& msg,
    const Environment& env,
    Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_INITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(GET_CAPABILITY_SCHEMA), "invalid request, missing required parameters");

    //Ensure that the current use count is greater than 0, so that an attempt to use the model was made.
    //Otherwise, the capability cannot be generated.
    uint32_t hfmodel_current_use_count_value;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_current_use_count_KEY, hfmodel_current_use_count_value), "failed to retrieve hfmodel_current_use_count");
    ASSERT_SUCCESS(rsp, hfmodel_current_use_count_value > 0, "invalid request, capability can be obtained only after use_model is called");

    //check for proof of commit of current state of the token object before returning capability
    std::string ledger_key;
    if (! ww::contract::attestation::get_ledger_key(ledger_key) && ledger_key.length() > 0)
        return rsp.error("contract has not been initialized");

    const std::string ledger_signature(msg.get_string("ledger_signature"));

    ww::types::ByteArray buffer;
    std::copy(env.contract_id_.begin(), env.contract_id_.end(), std::back_inserter(buffer));
    std::copy(env.state_hash_.begin(), env.state_hash_.end(), std::back_inserter(buffer));

    ww::types::ByteArray signature;
    if (! ww::crypto::b64_decode(ledger_signature, signature))
        return rsp.error("failed to decode ledger signature");
    if (! ww::crypto::ecdsa::verify_signature(buffer, ledger_key, signature))
        return rsp.error("failed to verify ledger signature");

    // the current state has been committed so now compute and return the capability
    ww::value::Structure params(GENERATE_CAPABILITY_SCHEMA);

    // Get kvstore_encryption_key from hfmodel_TO_store
    std::string kvstore_encryption_key;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(model_use_capability_kv_store_encryption_key_KEY, kvstore_encryption_key), "failed to retrieve model_use_capability_kv_store_enc_key");
    ASSERT_SUCCESS(rsp, params.set_string("kvstore_encryption_key", kvstore_encryption_key.c_str()), "failed to set return value for kvstore_encryption_key");

    // Get kvstore_root_block_hash from hfmodel_TO_store
    std::string kvstore_root_block_hash;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(model_use_capability_kv_store_root_block_hash_KEY, kvstore_root_block_hash), "failed to retrieve model_use_capability_kv_store_hash");
    ASSERT_SUCCESS(rsp, params.set_string("kvstore_root_block_hash", kvstore_root_block_hash.c_str()), "failed to set return value for kvstore_root_block_hash");

    // Get kvstore_input_key from hfmodel_TO_store
    std::string kvstore_input_key;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(model_use_capability_kv_store_input_key_KEY, kvstore_input_key), "failed to retrieve model_use_capability_kv_store_input_key");
    ASSERT_SUCCESS(rsp, params.set_string("kvstore_input_key", kvstore_input_key.c_str()), "failed to set return value for kvstore_input_key");

    // Get payload_type from hfmodel_TO_store
    std::string payload_type;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_request_payload_type_KEY, payload_type), "failed to retrieve hfmodel_request_payload_type");
    ASSERT_SUCCESS(rsp, params.set_string("payload_type", payload_type.c_str()), "failed to set return value for payload_type");

    // Get user_inputs from hfmodel_TO_store
    std::string user_inputs;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(model_use_capability_user_inputs_KEY, user_inputs), "failed to retrieve model_use_capability_user_inputs");
    ASSERT_SUCCESS(rsp, params.set_string("user_inputs", user_inputs.c_str()), "failed to set return value for user_inputs");

    // Get hf_auth_token from hfmodel_TO_store
    std::string hf_auth_token;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_auth_token_KEY, hf_auth_token), "failed to retrieve hf_auth_token");
    ASSERT_SUCCESS(rsp, params.set_string("hf_auth_token", hf_auth_token.c_str()), "failed to set return value for hf_auth_token");

    // Get hf_endpoint_url from hfmodel_TO_store
    std::string hf_endpoint_url;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_endpoint_url_KEY, hf_endpoint_url), "failed to retrieve hf_endpoint_url");
    ASSERT_SUCCESS(rsp, params.set_string("hf_endpoint_url", hf_endpoint_url.c_str()), "failed to set return value for hf_endpoint_url");

    // Get fixed_model_params from hfmodel_TO_store
    std::string fixed_model_params;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_fixed_params_KEY, fixed_model_params), "failed to retrieve fixed_model_params");
    ASSERT_SUCCESS(rsp, params.set_string("fixed_model_params", fixed_model_params.c_str()), "failed to set return value for fixed_model_params");

    // Get user_inputs_schema from hfmodel_TO_store
    std::string user_inputs_schema;
    ASSERT_SUCCESS(rsp, hfmodel_TO_store.get(hfmodel_user_inputs_schema_KEY, user_inputs_schema), "failed to retrieve user_inputs_schema");
    ASSERT_SUCCESS(rsp, params.set_string("user_inputs_schema", user_inputs_schema.c_str()), "failed to set return value for user_inputs_schema");

   // Calculate capability
    ww::value::Object result;
    ASSERT_SUCCESS(rsp, ww::exchange::token_object::create_operation_package("use_hfmodel", params, result),
                   "unexpected error: failed to generate capability");

    // this assumes that generating the capability does not change state, depending on
    return rsp.value(result, false);

}