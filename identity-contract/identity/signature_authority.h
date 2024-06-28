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

#include "Environment.h"
#include "Message.h"
#include "Response.h"
#include "Util.h"

#include "common/Credential.h"

#define SIGNATURE_AUTHORITY_SIGN_CREDENTIAL_PARAM_SCHEMA        \
    "{"                                                         \
        SCHEMA_KW(context_path, [ "" ]) ","                     \
        SCHEMA_KWS(credential, CREDENTIAL_SCHEMA)               \
    "}"

#define SIGNATURE_AUTHORITY_SIGN_CREDENTIAL_RESULT_SCHEMA       \
    VERIFIABLE_CREDENTIAL_SCHEMA

#define SIGNATURE_AUTHORITY_VERIFY_CREDENTIAL_PARAM_SCHEMA      \
    "{"                                                         \
        SCHEMA_KWS(credential, VERIFIABLE_CREDENTIAL_SCHEMA)    \
    "}"

namespace ww
{
namespace identity
{
namespace signature_authority
{
    bool sign_credential(const Message& msg, const Environment& env, Response& rsp);
    bool verify_credential(const Message& msg, const Environment& env, Response& rsp);
}; // signature_authority
}; // identity
}; // ww
