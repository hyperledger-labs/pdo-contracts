---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Getting Started with PDO Contracts (Host Install) #

This document provides an overview for preparing to work with PDO
contracts. These instructions focus on host installation. You may also
use the Docker-based services available in the `docker` subdirectory.

Assumptions:
* PDO client virtual environment has been installed in `${PDO_INSTALL_ROOT}`
* PDO Contracts packages have been built and installed in the client virtual environment
* PDO services are running

1. Create a personal configuration file
2. Create a services database
3. Create a service group configuration


## Site configuration

In order to access services, you must add information about the
services to the services database (see the script
`pdo-service-db`). Further, to create new contracts it is necessary to
create one or more groups of services that can be bound to the
contract (see the script `pdo-groups-db`, `pdo-eservice`,
`pdo-pservice`, and `pdo-sservice`).

To simplify testing, a simple configuration for local services is
created during docker container startup.

### Create a personal configuration file

The default PDO client configuration file is in
`${PDO_INSTALL_ROOT}/opt/pdo/etc/pcontract.toml`. This file contains a
basic configuration that should suffice for testing on a single host.

### Create a services database

The PDO client requires information about the enclave services that
will be used for contracts. Typically, a service provider will create
a site description file. For example, if the site description file is
called `site.toml` (the default), then the following command will add
all of the services to the database:

```
$ ${PDO_INSTALL_ROOT}/bin/pdo-service-db import --file site.toml
```

### Create a service group configuration

Service groups are a shortcut for configuration of collections of
enclave, storage, and provisioning services used to create and
provision a PDO contract object.
