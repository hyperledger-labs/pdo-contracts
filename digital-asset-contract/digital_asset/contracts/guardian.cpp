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

#include <algorithm>
#include <stddef.h>
#include <stdint.h>
#include <map>
#include <string>

#include "Dispatch.h"

#include "Cryptography.h"
#include "Environment.h"
#include "KeyValue.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "contract/base.h"
#include "contract/attestation.h"
#include "exchange/data_guardian.h"

#include "digital_asset/guardian.h"
#include "digital_asset/packages/bitmap/bitmap_image.hpp"

static KeyValueStore image_store("image");
static const std::string md_image_key("image");
static const std::string md_image_hash_key("image_hash");
static const std::string md_border_width_key("border_width");
static const std::string transfer_key("_transfer_");

static std::map<std::string, contract_method_t> initialize_capability_map(void)
{
    std::map<std::string, contract_method_t> result;
    result["get_public_image"] = ww::digital_asset::guardian::get_public_image;
    result["get_original_image"] = ww::digital_asset::guardian::get_original_image;
    result["get_image_metadata"] = ww::digital_asset::guardian::get_image_metadata;
    return result;
}

static const std::map<std::string, contract_method_t> capability_map = initialize_capability_map();

// -----------------------------------------------------------------
static bool set_public_border_width(const uint32_t border_width)
{
    return image_store.set(md_border_width_key, border_width);
}

// -----------------------------------------------------------------
static bool get_public_border_width(uint32_t& border_width)
{
    return image_store.get(md_border_width_key, border_width);
}

// -----------------------------------------------------------------
static bool set_image(const ww::types::ByteArray& image_data)
{
    if (! image_store.set(md_image_key, image_data))
        return false;

    ww::types::ByteArray hash_data;

    if (! ww::crypto::crypto_hash(image_data, hash_data))
        return false;

    if (! image_store.set(md_image_hash_key, hash_data))
        return false;

    return true;
}

// -----------------------------------------------------------------
static bool get_image(ww::types::ByteArray& image_data)
{
    if (! image_store.get(md_image_key, image_data))
        return false;

    return true;
}

// -----------------------------------------------------------------
static bool get_image(bitmap_image& image)
{
    ww::types::ByteArray image_array;
    if (! get_image(image_array))
        return false;

    image.load_image(image_array);
    return image.error_code_ == 0;
}

// -----------------------------------------------------------------
// NAME: initialize_contract
// -----------------------------------------------------------------
bool ww::digital_asset::guardian::initialize_contract(const Environment& env)
{
    return ww::exchange::data_guardian::initialize_contract(env);
}

// -----------------------------------------------------------------
// NAME: initialize
// -----------------------------------------------------------------
bool ww::digital_asset::guardian::initialize(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_OWNER(env, rsp);
    ASSERT_UNINITIALIZED(rsp);

    ASSERT_SUCCESS(rsp, msg.validate_schema(DAG_INITIALIZE_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    // Initialize the image asset and the save the parameters
    const uint32_t border_width = (unsigned int)msg.get_number("public_border_width");
    ASSERT_SUCCESS(rsp, 0 < border_width, "border width must be positive integer");

    // Grab the image from the transferred KV store
    const std::string encoded_encryption_key(msg.get_string("encryption_key"));
    const std::string encoded_state_hash(msg.get_string("state_hash"));
    const std::string transfer_key(msg.get_string("transfer_key"));

    ww::types::ByteArray encryption_key;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(encoded_encryption_key, encryption_key),
                   "invalid encryption key");

    ww::types::ByteArray state_hash;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_decode(encoded_state_hash, state_hash),
                   "invalid state hash");

    int handle = KeyValueStore::open(state_hash, encryption_key);
    if (handle < 0)
        return rsp.error("failed to open the key value store");

    ww::types::ByteArray image_vector;
    KeyValueStore input_store("", handle);

    ASSERT_SUCCESS(rsp, input_store.get(transfer_key, image_vector),
                   "store does not contain a value");

    ww::types::ByteArray new_state_hash;
    ASSERT_SUCCESS(rsp, input_store.finalize(handle, new_state_hash),
                   "failed to close the output store");

    // verify and store the image in the contract state
    bitmap_image image(image_vector);
    ASSERT_SUCCESS(rsp, image.error_code_ == 0, "invalid image format");

    ASSERT_SUCCESS(rsp, (border_width * 2) < image.width(), "invalid image width");
    ASSERT_SUCCESS(rsp, (border_width * 2) < image.height(), "invalid image height");

    ASSERT_SUCCESS(rsp, set_image(image_vector), "failed to store the image");
    ASSERT_SUCCESS(rsp, set_public_border_width(border_width), "failed to store the border width");

    // Initialize the data guardian
    ww::value::Object guardian_message;
    ASSERT_SUCCESS(rsp, msg.get_value("guardian", guardian_message),
                   "unexpected error: failed to get the parameter");

    return ww::exchange::data_guardian::initialize(guardian_message, env, rsp);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::digital_asset::guardian::get_image_metadata(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    bitmap_image image;
    ASSERT_SUCCESS(rsp, get_image(image), "failed to retrieve the image");

    ww::value::Structure v(DAG_IMAGE_METADATA_SCHEMA);

    const ww::value::Number width((double)image.width());
    v.set_value("width", width);

    const ww::value::Number height((double)image.height());
    v.set_value("height", height);

    const ww::value::Number bpp((double)image.bytes_per_pixel());
    v.set_value("bytes-per-pixel", bpp);

    uint32_t border_width;
    ASSERT_SUCCESS(rsp, get_public_border_width(border_width), "failed to retrieve border width");
    const ww::value::Number bw((double)border_width);
    v.set_value("public-border-width", bw);

    ww::types::ByteArray image_hash;
    ASSERT_SUCCESS(rsp, image_store.get(md_image_hash_key, image_hash), "failed to locate the image hash");

    std::string encoded_image_hash;
    ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(image_hash, encoded_image_hash), "failed to encode image hash");

    const ww::value::String hash(encoded_image_hash.c_str());
    v.set_value("image_hash", hash);

    return rsp.value(v, false);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::digital_asset::guardian::get_original_image(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ww::types::ByteArray image_vector;

    {
        // Get the image
        bitmap_image image;
        ASSERT_SUCCESS(rsp, get_image(image), "failed to retrieve the image");
        image.save_image(image_vector);
    }

    ww::types::ByteArray encryption_key;
    ASSERT_SUCCESS(rsp, ww::crypto::aes::generate_key(encryption_key),
                   "unexpected error: failed to create encryption key");

    // Save it to the output store
    int handle = KeyValueStore::create(encryption_key);
    if (handle < 0)
        return rsp.error("failed to create the key value store");

    KeyValueStore output_store("", handle);
    ASSERT_SUCCESS(rsp, output_store.set(transfer_key, image_vector),
                   "unexpected error: failed to save value");

    ww::types::ByteArray state_hash;
    ASSERT_SUCCESS(rsp, output_store.finalize(handle, state_hash),
                   "failed to close the output store");

    // Package the result
    ww::value::Structure result(DAG_IMAGE_TRANSFER_SCHEMA);

    {
        const ww::value::String v(transfer_key.c_str());
        result.set_value("transfer_key", v);
    }

    {
        std::string encoded_encryption_key;
        ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(encryption_key, encoded_encryption_key),
                       "unexpected error: failed to encode key");
        const ww::value::String v(encoded_encryption_key.c_str());
        result.set_value("encryption_key", v);
    }

    {
        std::string encoded_hash;
        ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(state_hash, encoded_hash),
                       "unexpected error: failed to encode hash");
        const ww::value::String v(encoded_hash.c_str());
        result.set_value("state_hash", v);
    }

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// -----------------------------------------------------------------
bool ww::digital_asset::guardian::get_public_image(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_INITIALIZED(rsp);

    ww::types::ByteArray image_vector;

    {
        // Get the image
        bitmap_image image;
        ASSERT_SUCCESS(rsp, get_image(image), "failed to retrieve the image");
        image.convert_to_grayscale();
        image.save_image(image_vector);
    }

    ww::types::ByteArray encryption_key;
    ASSERT_SUCCESS(rsp, ww::crypto::aes::generate_key(encryption_key),
                   "unexpected error: failed to create encryption key");

    // Save it to the output store
    int handle = KeyValueStore::create(encryption_key);
    if (handle < 0)
        return rsp.error("failed to create the key value store");

    KeyValueStore output_store("", handle);
    ASSERT_SUCCESS(rsp, output_store.set(transfer_key, image_vector),
                   "unexpected error: failed to save value");

    ww::types::ByteArray state_hash;
    ASSERT_SUCCESS(rsp, output_store.finalize(handle, state_hash),
                   "failed to close the output store");

    // Package the result
    ww::value::Structure result(DAG_IMAGE_TRANSFER_SCHEMA);

    {
        const ww::value::String v(transfer_key.c_str());
        result.set_value("transfer_key", v);
    }

    {
        std::string encoded_encryption_key;
        ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(encryption_key, encoded_encryption_key),
                       "unexpected error: failed to encode key");
        const ww::value::String v(encoded_encryption_key.c_str());
        result.set_value("encryption_key", v);
    }

    {
        std::string encoded_hash;
        ASSERT_SUCCESS(rsp, ww::crypto::b64_encode(state_hash, encoded_hash),
                       "unexpected error: failed to encode hash");
        const ww::value::String v(encoded_hash.c_str());
        result.set_value("state_hash", v);
    }

    return rsp.value(result, false);
}

// -----------------------------------------------------------------
// process_capability
//
// Perform an operation on the asset in the guardian.
// -----------------------------------------------------------------
bool ww::digital_asset::guardian::process_capability(const Message& msg, const Environment& env, Response& rsp)
{
    // note that we specifically DO NOT verify the identity of the
    // invoker... possession of a valid capability is sufficient to
    // prove the right to invoke the operation

    ASSERT_INITIALIZED(rsp);
    ASSERT_SUCCESS(rsp, msg.validate_schema(DG_PROCESS_CAPABILITY_PARAM_SCHEMA),
                   "invalid request, missing required parameters");

    const std::string minted_identity(msg.get_string("minted_identity"));
    ww::value::Object operation_secret;
    ASSERT_SUCCESS(rsp, msg.get_value("operation", operation_secret),
                   "unexpected error: failed to get value");

    ww::value::Object operation;
    ASSERT_SUCCESS(rsp, ww::exchange::data_guardian::parse_capability(minted_identity, operation_secret, operation),
                   "invalid capability");

    const std::string method_name(operation.get_string("method_name"));
    ww::value::Object params;
    ASSERT_SUCCESS(rsp, operation.get_value("parameters", params),
                   "unexpected error: failed to get value");

    const auto& method_map = capability_map.find(method_name);
    if (method_map == capability_map.end())
        return rsp.error("unexpected error: unknown capability method");

    return method_map->second(params, env, rsp);
}
