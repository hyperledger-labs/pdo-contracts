<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Docker Tools and Usages #

This directory contains scripts useful for building and running a
container with the PDO contracts. For the most part, this directory
could be copied to any host (even without PDO otherwise installed) to
build, configure, and execute PDO contracts code.  Also note that the
makefile assumes you have already built all containers from the
`private-data-objects` repository. You can use the `build_pdo_images`
target to build those from the current `private-data-objects` version.

For clarity the scripts in the directory are intended to serve two
purposes. The first is to provide the basic instructions for building
images for running the various contract families in the PDO contracts
repository. The images may be used for a variety of uses including
demonstration, testing and interacting with PDO contracts.

The second purpose is to provide a means for clean, reproducible
testing of the contracts and the Jupyter notebooks. Fully automated
testing (e.g. automated execution of all contract family tests) is
provided through the `test` target in the `Makefile` (e.g. run `make
test` to perform the automated tests). Interactive testing of the
Jupyter notebooks is provided through the `test_jupyter` target. That
target will create and run a container with a Jupyter server running
inside.  Note that this jupyter services is also a good place to get
some some hands-on experience with the mechanics of PDO contrarts:
after running `make test_jupyter`, peruse the
[documentation](../exchange-contract/docs/notebooks/README.md) and
point your browser to `http://localhost:8888`. Note Jupyter listens
only on the `localhost` interface. If you are running this on a
headless remote server accessed via ssh, just forward the port from
your local machine. For example:
```bash
> ssh $YOUR_TEST_MACHINE -L8888:localhost:8888
```

## Makefile Targets ##

The `Makefile` contains several targets that should simplify building
images and running containers.

Four configuration variables should be set as necessary:

* `CONTRACTS_REPO` -- the URL or file path of the PDO source git
  repository; this defaults to the repository stored on the local file
  system in which the docker directory is located.
* `CONTRACTS_BRANCH` -- the branch to use in from the source repository;
  this defaults to the branch where the source is currently stored.
* `CONTRACTS_USER_UID` -- the UID for the user that is created in the
  container to run the services; this defaults to the current users
  UID. Note that the `xfer` directory must be writable by the account
  associated with the UID.
* `CONTRACTS_GROUP_UID` -- the GID for the group assigned to the user
  created in the container; the default is the GID for the current
  user.
* `PDO_VERSION` -- the version identifier for PDO images; this
  defaults to `latest`.
* `PDO_REGISTRY` -- the docker repository from which PDO docker images
  may be retrieved; this defaults to `""` so that local images will be
  used by default.
* `CONTRACTS_VERSION` -- the version that will be used to tag the PDO
  contracts images that are create; this defaults to the current version
  number for the PDO contracts source.

The test targets in the `Makefile` pre-configure all network services
to run on `localhost` interface.

### Automated PDO Contract Tests  ###

The `Makefile` in the directory is set up so that `make test` should
build and execute the automated tests with the CCF ledger, PDO
services, and PDO contracts client (plus supporting containers such as
the OpenVINO container for the inference contract family) all
executing in separate containers. This action is performed using the
`docker-compose` configuration files in the source directory and the
`run_contracts_tests.sh` script in the `tools` directory.

### Interactive Testing of Jupyter Notebooks ###

The `test_jupyter` target in the `Makefile` enables interactive
testing of Jupyter notebooks. `make test_jupyter` will create a clean
environment for testing the various Jupyter notebooks provided by the
contract families. Rather than run a suite of automated tests, a
Jupyter server will be run in the container. The server will display a
URL that can be used for accessing the notebooks in the server.

### Build and Rebuild Targets ###

There are targets for the initial build of each image. In addition, if
changes are made to artifacts that are not part of the docker build
specification, a rebuild target can be used to force recompilation of
the PDO contracts artifacts.

```bash
    make build_contracts
    make rebuild_contracts
```

Similar targets will start the containers with different entry points:
`run_contracts`, and `run_jupyter`. The first will run the contracts
container with an interactive shell. The second will start a Jupyter
server in the container.

### Extending the Makefile ###

The behavior of the `Makefile` actions may be customized by placing
variable assignments or additional targets in the file
`make.loc`. This can be useful to, for example, configure the
contracts container to use services running on other servers:

```
JUPYTER_SERVICE_HOST=eservices.test.com
JUPYTER_LEDGER=http://55.55.55.55:6600
```

## Basic Layout ##

There are three subdirectories that are employed in building,
configuring and running a container. In general, to run the tests none
of these directories need to be modified.

* `xfer` -- this directory is used to pass configuration information
  and keys between the container and the host; for example, to push a
  previously built configuration into the container, put the files in
  the appropriate subdirectory in xfer.
* `tools` -- this directory contains a number of scripts that will be
  installed in the container to simplify building, configuring and
  running the services in the container.
* `repository` -- this directory is created during the build process
  and contains the PDO contracts source code that will be copied into
  the container; the build variables `CONTRACTS_REPO` and
  `CONTRACTS_BRANCH` control what is put into the directory.
