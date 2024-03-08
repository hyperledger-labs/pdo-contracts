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

# Getting Started with PDO Contracts #


Assumptions: 
* PDO client virtual environment has been installed in `${PDO_INSTALL_ROOT}`
* PDO Contracts packages have been built and installed in the client virtual environment
* PDO services are running 

1. Create a personal configuration file
2. Create a services database
3. Create a service group configuration


## Simplified configuration

If you are running the PDO services in the common test configuration (e.g. with 5 provisioning services, 5 enclave service, and 5 storage services all running on the same host, you can create all of the necessary configuration files with the command:
    
```
    $ export service_host=<service hostname>
    $ ${PDO_INSTALL_ROOT}/opt/pdo/bin/pdo-create-service-groups.psh --service_host ${service_host}
```

Use `service_host` in the notebooks that you create.



### Create a personal configuration file

The default PDO client configuration file is in `${PDO_INSTALL_ROOT}/opt/pdo/etc/pcontract.toml`. This file contains a basic configuration that should suffice for testing on a single host. 

*TODO: add a notebook that creates a configuration file.*



### Create a services database

The PDO client requires information about the enclave services that will be used for contracts. Typically, a service provider will create a site description file. For example, if the site description file is called `site.toml` (the default), then the following command will add all of the services to the database:

```
$ ${PDO_INSTALL_ROOT}/bin/pdo-service-db import --file site.toml
```


### Create a service group configuration

Service groups are a shortcut for configuration of collections of enclave, storage, and provisioning services used to create and provision a PDO contract object. 

*TODO: add a notebook that creates a groups file.*
