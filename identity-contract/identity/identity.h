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

#define IDENTITY_INITIALIZE_PARAM_SCHEMA        \
    "{"                                         \
        SCHEMA_KW(description, "")              \
    "}"

// At some point, we would like to add a context administrator to the
// registration. The administrator of the context or of any parent
// context would be the only ones allowed to register additional
// contexts in the tree below this one or to sign objects with the
// keys in the subcontexts. The basic idea is that we can create some
// level of accountability for how subcontexts are used.

#define IDENTITY_REGISTER_SIGNING_CONTEXT_PARAM_SCHEMA  \
    "{"                                                 \
        SCHEMA_KW(context_path, [ "" ]) ","             \
        SCHEMA_KW(description, "") ","                  \
        SCHEMA_KW(extensible, true)                     \
    "}"

// At some point, we need to add an operation to unregister a signing
// context. While it may sound straightforward (and might actually be
// so), there may be issues to address with usefulness of keys that
// have been used previously

#define IDENTITY_DESCRIBE_SIGNING_CONTEXT_PARAM_SCHEMA  \
    "{"                                                 \
        SCHEMA_KW(context_path, [ "" ])                 \
    "}"

#define IDENTITY_DESCRIBE_SIGNING_CONTEXT_RESULT_SCHEMA \
    "{"                                                 \
        SCHEMA_KW(subcontexts, [ "" ]) ","              \
        SCHEMA_KW(description, "") ","                  \
        SCHEMA_KW(extensible, true)                     \
    "}"

#define IDENTITY_SIGN_PARAM_SCHEMA              \
    "{"                                         \
        SCHEMA_KW(context_path, [ "" ]) ","     \
        SCHEMA_KW(message, "")                  \
    "}"

#define IDENTITY_SIGN_RESULT_SCHEMA             \
    "{"                                         \
        SCHEMA_KW(signature, "")                \
    "}"

#define IDENTITY_VERIFY_PARAM_SCHEMA            \
    "{"                                         \
        SCHEMA_KW(context_path, [ "" ]) ","     \
        SCHEMA_KW(message, "") ","              \
        SCHEMA_KW(signature, "")                \
    "}"

// At some point, we might benefit from formalizing the attributes
// used to verify that an identity is bound to a specific object. For
// example, a picture may be used to connect the identity object to a
// person. Or a SHA256 hash may be used to verify that the identity
// corresponds to a software artifact.

#define IDENTITY_ADD_CREDENTIAL_PARAM_SCHEMA "{" "}"

#define IDENTITY_REMOVE_CREDENTIAL_PARAM_SCHEMA "{" "}"

#define IDENTITY_CREATE_PRESENTATION_PARAM_SCHEMA "{" "}"

#define IDENTITY_CREATE_PRESENTATION_RESULT_SCHEMA "{" "}"

namespace ww
{
namespace identity
{
namespace identity
{
    bool initialize_contract(const Environment& env);
    bool initialize(const Message& msg, const Environment& env, Response& rsp);
    bool register_signing_context(const Message& msg, const Environment& env, Response& rsp);
    bool describe_signing_context(const Message& msg, const Environment& env, Response& rsp);
    bool sign(const Message& msg, const Environment& env, Response& rsp);
    bool verify(const Message& msg, const Environment& env, Response& rsp);
    bool add_credential(const Message& msg, const Environment& env, Response& rsp);
    bool remove_credential(const Message& msg, const Environment& env, Response& rsp);
    bool create_presentation(const Message& msg, const Environment& env, Response& rsp);
}; // identity
}; // identity
}; // ww
