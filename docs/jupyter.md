<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Using Jupyter Labs for PDO Contracts #

This directory contains several sample Jupyter notebooks that can be
used to create and interact with contract objects (or collections of
objects).

## Installation ##

There are many places to find information about [installation of
Jupyter](https://jupyter.org/install). Please consult one of the very
good guides for a complete installation and configuration.

A basic installation of Jupyter Labs is relatively easy assuming
that you have successfully installed the PDO client in a Python
virutal environment and that the PDO contracts have been installed.

* Activate the virtual environment: `source $PDO_INSTALL_ROOT/bin/activate`
* Install the Jupyter Labs package: `pip install jupyterlab`
* Install [Papermill](https://papermill.readthedocs.io/en/latest/): `pip install papermill`
* Install [Jupytext](https://jupytext.readthedocs.io/en/latest/): `pip install jupytext`
* Install [IPYWidgets](https://ipywidgets.readthedocs.io/en/stable/): `pip install ipywidgets`

Note that you will need to reinstall these packages anytime
you rebuild the Python virtual environment.

## Running Jupyter Labs Server ##

Please consult the Jupyter documentation for information about
configuration of the Jupyter Labs server.

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

## Getting Started

The easiest way to get started is to use the Jupyter file browser to
open `index.ipynb`. Render all of the markdown cells.
