<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

**The protocols and software are for reference purposes only and not intended for production usage.**

# Example Contract Family #

This directory contains an example contract family that can be used as
the basis for implementing your own contract families. This file will
walk you through the process of creating a new contract family.

Note that this description is not intended to be prescriptive. There
are many ways to build and deploy a contract. This directory simply
describes one way that we have found relatively easy to use.

# What is a Contract Family? #

A contract family is a collection of PDO contracts that work together
to create an "application". For example, the contracts in the Exchange
contract family, provide contracts to create digital asset like "red
marbles" with a veriable trust chain and contracts to use those assets
to purchase or exchange goods, services, or other assets. It is the
collection of contracts intentionally designed to work together that
we call a contract family.

Operationally, a contract family consists of a set of PDO contracts
and instructions for how to build them, configuration files that help
to specify the relationship between contracts or contract objects, and
plugins that makes it easier to use the contracts through a PDO shell,
a bash shell, or a Jupyter notebook.

## File System Layout ##

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

# How to Create a New Contract Family Using the Example Template #

The following instructions use the `example` contract family as a
template for building a new contract family that we'll call the
`myfirst` contract family. While each contract family can be
structured to your personal preferences, the `example` contract family
provides an easy way to get started.

1. Copy the `example-contract` directory to a new directory. To be
   picked up by the build system automatically, the new directory
   should be named with `myfirst-contract`.

```bash
    cp -R example-contract myfirst-contract
```

2. Edit `myfirst-contract/family.cmake`. Replace `example` with
   `myfirst` as the value of `CF_NAME`.

3. Edit `setup.py`. Replace `example` with `myfirst` as the value of
   the `contract_family` variable. Replace `example_counter` with
   `myfirst_counter` as the value of the `contract_scripts`
   variable. Update the author information for the Python package.

4. Rename the `example` contract context file, the Python module
   directory and the directory that contains exported header files.

```bash
    mv etc/example.toml etc/myfirst.toml
    mv src/example src/myfirst
    mv pdo/example pdo/myfirst
```

5. Replace references to `example` with `myfirst`. This will update
   contract family references in several locations including the
   contract source namespace in the `src` directory, the contract
   references in the tests, and the plugin and resource references in
   the Python modules.

```bash
find . -type f -exec sed -i s/example/myfirst/g {} \;
find . -type f -exec sed -i s/Example/MyFirst/g {} \;
```

At this point, assuming you have a complete PDO client installation,
you should be able build and test your new contract family. To do
this, add the following line to `Local.cmake` in the PDO contracts
root directory:

```
SET(CONTRACT_FAMILIES myfirst-contract)
```

This will limit the build process to the new contract family to
simplify testing.

Assuming that you have installed and configured a PDO client
environment (and have activated the PDO Python virtual environment),
then you can build and run the tests:

```bash
make install
make test
```

# How to Add a New Contract to the Contract Family #

A PDO contract consists of a set of methods that operate on a
persistent state. Methods are generally grouped together in a
namespace to make them easier to re-use for multiple contracts. The
`counter` methods module (see `src/methods/counter.cpp`) in the
example contract family defines two methods, one for incrementing the
counter and one getting the current value of the counter. The methods
module also includes a function that can be used to initialize the
contract state prior to using either method. These methods can be
imported into any contract so long as the contract invokes the
initialization function prior to invoking either of the counter
methods.

The actual `counter` contract is defined in
`src/contracts/counter.cpp`.  Effectively, the contract consists of an
initialization function that will be called when the contract object
is first created and a dispatch table for methods on the contract
object. The dispatch table maps an external name of the method (all
methods are invoked through a JSON RPC protocol defined in PDO) to the
code that implements the method.

Note that in the `counter` contract, the `initialize_contract`
function calls the `counter` method module initialization function so
that the `counter` methods will work correctly.

## How to Add a New Method ##

To add a new method to the `counter` contract, simply add the code for
the method to `src/methods/counter.cpp` (or create a new method module
in that directory) and add the interface definition to the public
header file `src/example/counter.h`. For example, you could define a
new method for the `counter` method module called `dec_value` to
decrement the value of the counter. The implementation of the method
would be placed in the `counter` method module and the interface added
to the public header file.

To include the new method in the contract, add it to the dispatch
table in the contract definition file `src/contracts/counter.cpp`. The
table uses the PDO macro for specifying the external name of the
method and the contract function that will be invoked through that
name.

## How to Define a New Contract ##

The following steps are taken to create a new type of contract:

1. Define and implement any additional methods that are necessary in a
   method module. Methods may also be imported from other contract
   families. See the `CMakeLists.txt` file in the digital-asset
   contract family for an example of how methods are imported from the
   exchange contract family.

2. Create a new contract definition file in `src/contracts`. The file
   must contain a contract initialization function and a dispatch
   table for the methods exported by the contract.

3. Add the contract to the list of contracts in `family.cmake`. That
   is, add the name of the new contract to the `CF_CONTRACTS` macro.

4. Add the contract mapping to the context configuration file in the
   `etc` directory. The name of the context file for the example
   contract family is `etc/example.toml`. This mapping helps the
   shells to identify the location of the compiled contract when a new
   contract object is created.

Assuming that you have installed and configured a PDO client
environment (and have activated the PDO Python virtual environment),
then you can build and install the new contract:

```bash
make
make install
```

The new contract should be available in the `${PDO_HOME}/contracts`
directory. To test the contract effectively will require a new Python
plugin for the contract.

# How to Define a New Shell Plugin #

Shell plugins provide access to PDO contract method invocations
through the PDO shell, Bash shell, and other Python scripts using a
single implementation.

Plugins come in two flavors. The first are operations derived from the
`pdo.client.builder.contract.contract_op_base` class. These operations
generally have a one-to-one correspondance to methods on the contract
object. The second are commands derived from the
`pdo.client.builder.command.contract_command_base` class. Commands are
generally used for complex operations that involve invocation of
multiple methods potentially across multiple contract objects.

For example, the plugin for `counter` contract objects defines one
operation for each of the methods (`inc_value` and `get_value`) and a
command to create the counter (which creates the contract object and
initializes it).

## How to Write a Plugin for a Contract ##

The easiest way to define a plugin for a new type of contract object
is to simply copy the basic framework for the `counter` plugin and
implement an operation for each method on your new contract. If your
new contract imports methods from another contract family, it is
relatively straightforward to import the plugin operations as well.

Examples for invoking the operations and commands is provided by the
scripts in the `test` directory.

# Jupyter Plugins #
