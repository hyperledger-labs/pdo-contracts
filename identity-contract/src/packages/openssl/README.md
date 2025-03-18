<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

This directory provides a simple script for building OpenSSL for WASM that will run inside an SGX enclave (meaning that no dependencies on syscalls are acceptable). The script and patches were inspired by other projects including
(openssl-wasm)[https://github.com/jedisct1/openssl-wasm] and (SGX-SSL)[https://github.com/intel/intel-sgx-ssl]. Licenses for both projects are included.

Note that there are some ongoing dependencies for missing functions. Any application that wants to use the library will likely have to provide definitions for functions such as `getenv`:

```c
extern "C" char* getenv(const char* name)
{
    return NULL;
}
```
