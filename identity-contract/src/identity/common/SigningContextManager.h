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

#include "KeyValue.h"
#include "Types.h"

#include "SigningContext.h"

namespace ww
{
namespace identity
{
    class SigningContextManager
    {
    private:
        KeyValueStore store_;

        static std::string make_key(
            const std::vector<std::string>& context_path);

        static const std::string root_key_;

    public:
        bool add_context(
            const std::vector<std::string>& context_path,
            const ww::identity::SigningContext& new_context);

        bool remove_context(
            const std::vector<std::string>& context_path);

        bool find_context(
            const std::vector<std::string>& context_path,
            std::vector<std::string>& extended_path,
            ww::identity::SigningContext& context) const;

        bool initialize(void);

        SigningContextManager(const KeyValueStore& store) : store_(store) {};
    };

} /* identity */
} /* ww */
