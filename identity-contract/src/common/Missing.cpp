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

#include <stddef.h>
#include <openssl/crypto.h>

#include "Cryptography.h"
#include "WasmExtensions.h"

// This file contains the definition of functions that are not
// available in the WASI libc but required for openssl.

extern "C" char* getenv(const char* name)
{
    return NULL;
}

// openssl > 3.00.0 requires atexit to be defined unless
// you specifically initialize the library with OPENSSL_init_crypto
extern "C" int atexit(void (*function)(void))
{
    OPENSSL_cleanup();
    return 0;
}

// this is a weird way of replacing getuid, getgid, getegid, getpid
// for the WASM implementations of SSL; see the openssl-wasm github
// repository for more details
extern "C" int getpagesize(void)
{
    return 4096;
}

extern "C" void arc4random_buf(void* buffer, size_t size)
{
    ::random_identifier(size, (uint8_t*)buffer);
}
