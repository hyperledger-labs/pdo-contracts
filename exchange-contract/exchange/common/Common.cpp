/* Copyright 2021 Intel Corporation
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

#include "KeyValue.h"
#include "Message.h"
#include "Value.h"
#include "Types.h"

#include "Common.h"

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// Class: ww::exchange::SerializeableObject
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

// -----------------------------------------------------------------
bool ww::exchange::SerializeableObject::get_from_message(
    const Message& msg,
    const char* name)
{
    ww::value::Object serialized_object;
    if (! msg.get_value(name, serialized_object))
        return false;

    if (! deserialize(serialized_object))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::SerializeableObject::get_from_datastore(
    const KeyValueStore& data_store,
    const std::string& name)
{
    std::string serialized_string;
    if (! data_store.get(name, serialized_string))
        return false;

    if (! deserialize_string(serialized_string))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::SerializeableObject::save_to_datastore(
    const KeyValueStore& data_store,
    const std::string& name) const
{
    std::string serialized_string;
    if (! serialize_string(serialized_string))
        return false;

    if (! data_store.set(name, serialized_string))
        return false;

    return true;
}

// -----------------------------------------------------------------
bool ww::exchange::SerializeableObject::verify_schema_actual(
    const ww::value::Object& deserialized_object,
    const char* schema)
{
    return deserialized_object.validate_schema(schema);
}

// -----------------------------------------------------------------
bool ww::exchange::SerializeableObject::deserialize_string(const std::string& serialized_string)
{
    ww::value::Object value;
    if (! value.deserialize(serialized_string.c_str()))
        return false;

    return deserialize(value);
}

// -----------------------------------------------------------------
bool ww::exchange::SerializeableObject::serialize_string(std::string& serialized_string) const
{
    ww::value::Value value;
    if (! serialize(value))
        return false;

    return value.serialize(serialized_string);
}
