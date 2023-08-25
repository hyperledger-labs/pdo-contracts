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

#include "KeyValue.h"
#include "Message.h"
#include "Types.h"
#include "Value.h"

namespace ww
{
namespace exchange
{
    class SerializeableObject
    {
    protected:
        // common functions implemented by this class
        static bool verify_schema_actual(
            const ww::value::Object& deserialized_chain,
            const char* schema);

    public:
        bool get_from_message(const Message& msg, const char* name);
        bool get_from_datastore(const KeyValueStore& data_store, const std::string& name);
        bool save_to_datastore(const KeyValueStore& data_store, const std::string& name) const;

        bool deserialize_string(const std::string& serialized_chain);
        bool serialize_string(std::string& serialized_chain) const;

        // virtual functions that must be implemented by the derived class
        bool virtual deserialize(const ww::value::Object& chain) = 0;
        bool virtual serialize(ww::value::Value& serialized_chain) const = 0;
    };
};
}
