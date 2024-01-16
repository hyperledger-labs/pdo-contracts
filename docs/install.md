<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Installation Guide #

The following instructions assume that the PDO contracts source is available in
the directory pointed to by the environment variable `PDO_CONTRACTS_ROOT` and
will be installed to the directory pointed to by the environment variable
`PDO_INSTALL_ROOT`.

## Install Pre-Built Packages

To install from pre-built packages requires that you have installed the PDO
client into a virtual environment in the directory `${PDO_INSTALL_ROOT}`. Once
that is done, you can install the pre-built packages with the following
commands:

```
$ ${PDO_INSTALL_ROOT}/bin/pip3 install ${EXCHANGE_PACKAGE} ${DIGITAL_ASSET_PACKAGE}
$ ${PDO_INSTALL_ROOT}/bin/pdo-install-plugin-resources --module pdo.exchange --family exchange
$ ${PDO_INSTALL_ROOT}/bin/pdo-install-plugin-resources --module pdo.digital_asset --family digital_asset
```

Note that the build process described below will create the Python packages in
the directory `${PDO_CONTRACTS_ROOT}/build/dist`.

## Build and Install Process Overview

- Install required build dependencies
- Install the WASM development toolchain
- Build and install the PDO client environment
- Build and install the PDO contracts packages

## <a name="environment">Install Build Dependencies</a>

On a minimal Ubuntu system, the following packages are required. Other
distributions will require similar packages.

```
sudo apt install -y cmake curl git pkg-config unzip xxd libssl-dev build-essential
sudo apt install -y swig python3 python3-dev python3-venv virtualenv
sudo apt install -y liblmdb-dev libprotobuf-dev libsecp256k1-dev protobuf-compiler libncurses5-dev
```

Set the minimal configuration variables for the PDO client installation:
```
export PDO_SOURCE_ROOT=${PDO_CONTRACTS_ROOT}/private-data-objects
source ${PDO_SOURCE_ROOT}/build/common-config.sh
```

More information about the PDO common configuration is available in the
[PDO documentation](../private-data-objects/docs/environment.md).

## <a name="wasi">Install WASM Development Toolchain</a>

PDO contracts are compiled into WASM code for evaluation.  There are
many toolchains that could be used to build a WASM code. By default,
Wawaka contracts are compiled with the compilers provided by [WASI
SDK](https://github.com/WebAssembly/wasi-sdk). To use WASI SDK,
download and install the appropriate package file from
https://github.com/WebAssembly/wasi-sdk/releases (we have verified
that release wasi-sdk-12 works with WAMR version WAMR-1.1.2).

```
wget -q -P /tmp https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-12/wasi-sdk_12.0_amd64.deb
sudo dpkg --install /tmp/wasi-sdk_12.0_amd64.deb
```

## <a name="client">Build and Install the PDO Client Environment</a>

Assuming you have installed and configured the pre-requisites in the default
location, the following commands will build and install PDO into a Python
virtual environment in the directory `${PDO_INSTALL_ROOT}`.

```
make -C ${PDO_SOURCE_ROOT}/build client
```

Finally, activate the PDO Python virtual environment:

```
source ${PDO_INSTALL_ROOT}/bin/activate
```

More information about PDO client installation is found in the
[PDO documentation](../private-data-objects/docs/client_install.md).

## <a name="contracts">Build and Install the PDO Contracts Packages</a>

Finally, build and install the Python packages associated with the PDO contract
families. The packages will be built in the directory
`${PDO_CONTRACTS_ROOT}/build/dist`.

```
make -C ${PDO_CONTRACTS_ROOT}
make -C ${PDO_CONTRACTS_ROOT} install
```

Assuming that your PDO services are correctly configured and running
on ${SERVICE_HOST}, you can test the installation with the following:

```
TEST_SERVICE_HOST=${SERVICE_HOST} make -C ${PDO_CONTRACTS_ROOT} test
```
