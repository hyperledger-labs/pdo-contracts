<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Using Jupyter Labs for Exchange Contracts #

This directory contains several sample Jupyter notebooks that can be
used to create and interact with contract objects (or collections of
objects) in the Exchange contract family.

## Installation ##

There are many places to find information about [installation of
Jupyter](https://jupyter.org/install). Please consult one of the very
good guides for a complete installation and configuration.

A basic installation of Jupyter notebook is relatively easy assuming
that you have successfully installed the PDO client in a Python
virutal environment and that the Exchange contract family has been installed.

* Activate the virtual environment: `source $PDO_INSTALL_ROOT/bin/activate`
* Install the Jupyter notebook package: `pip install notebook`
* Install [Papermill](https://papermill.readthedocs.io/en/latest/): `pip install papermill`
* Install [Jupytext](https://jupytext.readthedocs.io/en/latest/): `pip install jupytext`
* Install [IPYWidgets](https://ipywidgets.readthedocs.io/en/stable/): `pip install ipywidgets`

Note that you will need to reinstall Jupyter and papermill any time
you rebuild the Python virtual environment.

## Running Jupyter Notebook Server ##

Please consult the Jupyter documentation for information about
configuration of the Jupyter server.

Notebook files will automatically be installed to the directory
`${PDO_HOME}/notebooks`.  The files may be copied to another directory
if you prefer. Feel free to adjust the instructions below to put your
notebooks in a different directory or change the parameters for the
Jupyter server.

Assuming that Jupyter and Papermill are installed in the PDO virtual
environment, the Jupyter server can be started as follows:

* Activate the virtual environment:
```bash
source $PDO_INSTALL_ROOT/bin/activate
```

* Set the environment variable `PDO_JUPYTER_ROOT` to the directory
  where the notebooks were installed:
```bash
export PDO_JUPYTER_ROOT=${PDO_HOME}/notebooks
```

* Start the Jupyter notebook server:
```bash
cd ${PDO_JUPYTER_ROOT}
jupyter lab --no-browser --port=8888
```

## Structure of a Notebook ##

The templates provided generally share five common sections:

* Configure the Contract Object
* Initialize the Interpreter and the PDO Environment
* Initialize the Contract Object Context
* Operate on the Contract
* View Contract Metadata

To initialize the interpreter, the notebook loads the Juptyer
helper module. This module imports all of the relevant PDO and
Exchange modules to simplify access for code in the notebook. It also
defines several procedures that are useful for initializing and
interacting with the environment.

In addition, the interpreter initialization configures an IPython
extension that makes it easier to provide code for multiple types of
operations that can be performed on the contract object. Specifically,
the extension defines a magic keyword, `skip`, that takes a value or
expression that, if it evaluates to True, causes the code section to
be skipped during notebook execution.

The next section in the notebook configures information about the
contract object associated with the notebook. In some cases, the
variables will set by the notebook using the Papermill extensions. In
some cases, the variables may be customized for the specific behavior
desired.

The following section initializes the PDO environment from the PDO
configuration files. There may be opportunities for customization, but
so long as the PDO configuration is complete changes to this section
should be infrequent.

The final common section initializes the contract context. Where the
PDO initialization handles configuration of the PDO modules, this
section handles configuration of the specific contract object and its
relationship to other contract objects.

## Getting Started

The easiest way to get started is to use the Jupyter file browser to
open `index.ipynb`. Render all of the markdown cells.
