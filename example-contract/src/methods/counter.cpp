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

#include <malloc.h>
#include <stddef.h>
#include <stdint.h>

#include "Dispatch.h"

#include "KeyValue.h"
#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"
#include "Value.h"
#include "WasmExtensions.h"

#include "example/counter.h"

static KeyValueStore meta_store("meta");
static KeyValueStore value_store("values");

const std::string counter_key("counter");

// -----------------------------------------------------------------
// NAME: initialize_contract
// -----------------------------------------------------------------
bool ww::example_contract::counter::initialize_contract(const Environment& env, Response& rsp)
{
    // create the value and save it to state
    const uint32_t value = 0;

    if (! value_store.set(counter_key, value))
        return rsp.error("failed to create the test key");

    return rsp.success(true);
}

// -----------------------------------------------------------------
// NAME: inc_value
// -----------------------------------------------------------------
bool ww::example_contract::counter::inc_value(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);

    // get the value and increment it
    uint32_t value;
    if (! value_store.get(counter_key, value))
        return rsp.error("no such key");

    value += 1;
    if (! value_store.set(counter_key, value))
        return rsp.error("failed to save the new value");

    ww::value::Number v((double)value);
    return rsp.value(v, true);
}

// -----------------------------------------------------------------
// NAME: get_value
// -----------------------------------------------------------------
bool ww::example_contract::counter::get_value(const Message& msg, const Environment& env, Response& rsp)
{
    ASSERT_SENDER_IS_CREATOR(env, rsp);

    // get the value
    uint32_t value;
    if (! value_store.get(counter_key, value))
        return rsp.error("no such key");

    ww::value::Number v((double)value);
    return rsp.value(v, false);
}
