---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: Bash
    language: bash
    name: bash
---

<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

**The protocols and software are for reference purposes only and not intended for production usage.**

> This tutorial is intended to be viewed through the PDO contract
> Jupyter server. For information on setting up the environment for
> the tutorial, please view the `README.md` in the `example-contract`
> directory.


# Contract Developer Tutorial #

This page is intended to guide a contract developer through the
process of creating a new contract family based on the `Example
Contract Family`. The material here is intended to provide one method
for creating a new contract family; feel free to adjust your process
to your personal preferences.


# What is a Contract Family? #

A contract family is a collection of PDO contracts that work together
to create an "application". For example, the contracts in the Exchange
contract family, provide contracts to create digital assets (like "red
marbles") with a verifiable trust chain, and contracts to use those
assets to purchase or exchange goods, services, or other assets. It is
this collection of contracts intentionally designed to work together
that we call a "contract family".

Operationally, a contract family consists of a set of PDO contracts
and instructions for how to build them, configuration files that help
to specify the relationship between contracts or contract objects, and
plugins that makes it easier to use the contracts through a PDO shell,
a `bash` shell, or a Jupyter notebook.


# Contract Family Directory Layout ##

* The root directory of the contract family generally contains
  information useful for building and deploying contracts in the
  family.

* The `context` directory contains context files that describe the
  relationship between contract objects and help to coordinate the
  configuration of dependent contract objects.

* The `src` directory contains the source files used to build the
  contracts in the contract family. The source directory contains
  several subdirectories:

  * The `common` directory contains modules that will be shared
    amongst all of the contracts.

  * The `packages` directory may contain external dependencies
    required for the contract.

  * The `methods` directory contains modules that implement different
    groups of methods. For simple contracts there is generally one
    method module per contract. More complex contracts may mix and
    match methods from different modules.

  * The `contracts` directory contains the definition of the contracts
    themselves. These are generally specified as a collection of
    methods defined in the `methods` directory.

  * Finally, there is often a directory that contains interface
    definitions that may be used by other contract families to re-use
    methods. For example, this contract family defines an interface
    for the counter contract in the `example` directory.

* The `docs` directory generally contains interface specifications for
  the methods in the contract. It may also contain the templates for
  Jupyter notebooks used to interact with the contracts.

* The `etc` directory contains basic configuration information. When
  you customize your own contract family, you will need to update
  information about the mapping between contract types and compiled
  contract code.

* The `pdo` directory is the root of the Python modules associated
  with the contract family. The Python modules contain plugins for the
  PDO and bash shells, and utility functions that can be invoked from
  a Jupyter notebook.

* The `scripts` directory may optionally contain PDO shell scripts
  that will be installed with the deployed contracts.

* The `test` directory defines system tests for the contract family
  that will be automatically run by the contracts CI system. Tests are
  broken into two parts, one for running a set of commands in a single
  PDO shell invocation and one for running a series of bash shell
  commands. Note that the two are similar but not the same. The PDO
  shell will process transaction commits asynchronously while the bash
  shell tests commit synchronously.


# Set up the Environment for Jupyter #

Several of the shell commands below may be executed directly from the
notebook. The command blocks assume that the document is being viewed
through the Jupyter interface with the current source directory
mounted at `/project/pdo/dev` (the default if you started the Jupyter
Lab server using the `developer` target in the docker Makefile). This
command block should be run before any of the following statements is
run.

```bash
    export CONTRACT_SOURCE=/project/pdo/dev
    cd ${CONTRACT_SOURCE}
```


# Create a New Contract Family Using the Example Template #

The following instructions use the `example` contract family as a
template for building a new contract family that we'll call the
`myfirst` contract family. While each contract family can be
structured to your personal preferences, the `example` contract family
provides an easy way to get started.


## Clone the Example Contract Family ##

1. Copy the `example-contract` directory to a new directory. To be
   picked up by the build system automatically, the new directory
   should be named with `myfirst-contract`.

```bash
    cp -R example-contract myfirst-contract
```

2. Edit `myfirst-contract/family.cmake`. Replace `example` with
   `myfirst` as the value of `CF_NAME`. `CF_NAME` is used to identify
   the contract family. The other macro in that file is a list of
   contracts that belong to the family. This will be addressed below
   when we add a new method to the contract.

```bash
    sed -i s/example/myfirst/ myfirst-contract/family.cmake
```

3. Edit `myfirst-contract/setup.py`. Replace `example` with `myfirst`
   as the value of the `contract_family` variable. Replace
   `example_counter` with `myfirst_counter` as the value of the
   `contract_scripts` variable. This variable provides a list of shell
   scripts that will be installed for the contract family. Finally,
   update the author information for the Python package.

```bash
    sed -i s/example/myfirst/ myfirst-contract/setup.py
```

4. Rename the `example` contract context file, the Python module
   directory and the directory that contains exported header
   files. The context file helps to specify the relationshihp between
   contract objects (like an asset account and the issuer of the
   assets). The other two directories are important for adding methods
   to the contract.

```bash
    mv myfirst-contract/etc/example.toml myfirst-contract/etc/myfirst.toml
    mv myfirst-contract/src/example myfirst-contract/src/myfirst
    mv myfirst-contract/pdo/example myfirst-contract/pdo/myfirst
```

5. Replace references to `example` with `myfirst`. This will update
   contract family references in several locations including the
   contract source namespace in the `src` directory, the contract
   references in the tests, and the plugin and resource references in
   the Python modules.

```bash
find myfirst-contract -type f -exec sed -i s/example/myfirst/g {} \;
find myfirst-contract -type f -exec sed -i s/Example/MyFirst/g {} \;
```


## Test the New Contract Family ##

At this point, assuming you have a complete PDO client installation,
you should be able build and test your new contract family. To do
this, add or edit the following line to `Local.cmake` in the PDO
contracts root directory:

```bash
echo 'LIST(APPEND CONTRACT_FAMILIES myfirst-contract)' >> Local.cmake
```

This will limit the build process to the new contract family to
simplify testing.

Assuming that you have installed and configured a PDO client
environment (and have activated the PDO Python virtual environment),
then you can build and run the tests:

```bash
make clean
make install
make test
```


# Add a New Contract to the MyFirst Contract Family #

A PDO contract consists of a set of methods that operate on a
persistent state. Methods are generally grouped together in a
namespace to make them easier to re-use for multiple contracts.

The `counter` methods module copied from the `example` contract family
initially defines two methods, one for incrementing the counter and
one for returning the current value of the counter (the methods module
is implemented in the file `src/methods/counter.cpp`). The methods
module also includes a function that can be used to initialize the
contract state prior to using either method. These methods can be
imported into any contract so long as the contract invokes the
initialization function prior to invoking either of the counter
methods.

The `counter` contract is defined in `src/contracts/counter.cpp`.
Effectively, the contract consists of an initialization function that
will be called when the contract object is first created and a
dispatch table for methods on the contract object. The dispatch table
maps an external name of the method (all methods are invoked through a
JSON RPC protocol defined in PDO) to the code that implements the
method.

Note that in the `counter` contract, the `initialize_contract`
function calls the `counter` method module initialization function so
that the `counter` methods will work correctly.


## Add a Method to Decrement the Counter ##

This section contains instructions for adding a new method to the
`counter` method module. The new method, `dec_value` will decrement
the value of the counter and return the value as a result. Only the
creator of the contract object may invoke the method. The
implementation of `dec_value` method is provided the file
[dec_value.cpp](../files/dec_value.cpp).

1. Add the method implementation to `src/methods/counter.cpp`: copy
   the contents of [dec_value.cpp](../files/dec_value.cpp) to the end of
   `src/methods/counter.cpp`.

2. Add the interface to the method to the public header file
   `src/myfirst/counter.h` in the `counter` namespace along with the
   other contract methods. The interface can be found in the file
   [dec_value.h](../files/dec_value.h). The public header file exports
   the method to `counter` contracts and any other contract family
   that would like to use the method.

3. Add the new method to the dispatch table in the contract definition
   file `src/contracts/counter.cpp`. The table uses the PDO macro
   `CONTRACT_METHOD2` for specifying the external name of the method
   and the contract function that will be invoked through that
   name. The new method can be added to the contract with the line:

```c++
    CONTRACT_METHOD2(dec_value, ww::myfirst_contract::counter::dec_value),
```


## How to Define a New Contract ##

As discussed in the previous section, the definition of a contract
comes from the dispatch table used to map method names to contract
functions implemented in the method module. In the `myfirst` contract
family, each file in the directory `src/contracts` represents a type
of contract.

The previous section describes the process for adding a new method to
an existing contract. This section describes the steps to create a
new type of contract using the methods in the `counter` method module.

The following steps are taken to create a new type of contract:

1. *OPTIONAL*: Define and implement any additional methods that are
   necessary in a method module. Methods may also be imported from
   other contract families. See the `CMakeLists.txt` file in the
   digital-asset contract family for an example of how methods are
   imported from the exchange contract family.

2. Create a new contract definition file in `src/contracts`. The file
   must contain a contract initialization function and a dispatch
   table for the methods exported by the contract. For example, copy
   `src/contracts/counter.cpp` to `src/contracts/new_counter.cpp`.

3. *OPTIONAL*: Edit the dispatch table in
   `src/contracts/new_counter.cpp` to include any additional methods
   you would like to include in the contract. Note that if you include
   methods from method modules other than the `counter` method module,
   you may need to invoke the initialization function in
   `initialize_contract`.

3. Add the new contract to the list of contracts in
   `family.cmake`. That is, add the name of the new contract to the
   `CF_CONTRACTS` macro. This might look like:

```
SET(CF_CONTRACTS counter new_counter)
```

4. Add the contract mapping to the context configuration file in the
   `etc` directory. The name of the context file for the `myfirst`
   contract family is `etc/myfirst.toml`. This mapping helps the
   shells to identify the location of the compiled contract when a new
   contract object is created.

```
   new_counter = { source = "${home}/contracts/myfirst/_myfirst_new_counter.b64" }
```

Assuming that you have installed and configured a PDO client
environment (and have activated the PDO Python virtual environment),
then you can build and install the new contract:

```bash
make install
```

The new contract should be available in the `${PDO_HOME}/contracts`
directory. To test the contract effectively will require a new Python
plugin for the contract.


# How to Define a New Shell Plugin #

Shell plugins provide access to PDO contract methods through the PDO
shell, Bash shell, and other Python scripts using a single
implementation.

Plugins come in two flavors. The first are *operations* derived from
the `pdo.client.builder.contract.contract_op_base` class. Operations
generally have a one-to-one correspondance to methods on the contract
object. The second are *commands* derived from the
`pdo.client.builder.command.contract_command_base` class. Commands are
generally used for complex interactions that involve invocation of
multiple operations potentially across multiple contract objects.

For example, in the file `pdo/example/plugins/counter.py` the plugin
for `counter` contract objects defines one *operation* for each of the
methods (`inc_value` and `get_value`) and a *command* to create the
counter (which creates the contract object and initializes it).

More information about plugins is available in the client
documentations from PDO.


## Add an Operation for a New Method ##

In a previous tutorial, a `dec_value` method was added to the
`counter` contract object in the `myfirst` contract family. In order
to make that method available, it is recommended that you provide a
shell plugin *operation*. The new *operation* will process command
line parameters and invoke the `dec_value` method on a contract
object. An implementation of the plugin operation can be found in the
file [dec_plugin.py](../files/dec_plugin.py).

1. Copy the contents of [dec_plugin.py](../files/dec_plugin.py) into the
   `counter` plugins file at `pdo/myfirst/plugins/counter.py`.

2. Add the name of the plugin operation, `op_dec_value`, to the
   `__operations__` list in `pdo/myfirst/plugins/counter.py`.

3. *OPTIONAL*: Although it is not necessary, you can add a *command*
   plugin that will simplify scripted access to the `dec_value`
   method. Copy the code from `cmd_inc_value` in the `counter` plugins
   file, change the operation that is invoked to `op_dec_value`, and
   add the new command to the `__commands__` list.


## Add a Plugin Module for a New Contract ##

The easiest way to define a plugin for a new type of contract object
is to simply copy the basic framework for the `counter` plugin and
implement an operation for each method on your new contract. If your
new contract imports methods from another contract family, it is
relatively straightforward to import the plugin operations as well.

Examples for invoking the operations and commands is provided by the
scripts in the `test` directory.


# Add a Juptyer Notebooks for Accessing a Contract #

**This section is under construction.**
