<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

**The protocols and software are for reference purposes only and not intended for production usage.**

# Example Contract Family #

This directory contains an example contract family that can be used as
the basis for implementing your own contract families. This contract
family defines a single contract called `counter` that implements a
confidential integer counter. The family includes shell plugins, test
scripts, and a simple Jupyter notebook interface for creating and
interacting with counters.

## Starting the Tutorial ##

The `docs/notebooks/documents` directory contains a
[tutorial](docs/notebooks/documents/index.md) for creating a new
contract family. While the material may be used through an IDE, the
tutorial is intended to be viewed through the PDO Contracts Jupyter
server. The following steps will guide you through the process of
creating a development environment and starting a Jupyter server using
the [PDO contracts docker images](../docker/README.md).

The following commands should be executed from the PDO contracts root
directory.

1. Build the PDO docker images

```bash
make -C docker build_pdo_images
```

2. Build the PDO contracts images and start the containers

The `developer` target in the `docker` directory will create a
`pdo_contracts` image and will start local instances of all of the
necessary containers to create a complete PDO environment.

*NOTE*: The `developer` target mounts the current PDO contracts source
directory into the `pdo_contracts` container in the directory
`/project/pdo/dev`. Any changes that you make to the source in the
container will be reflected in the source on the host. Likewise, any
changes you make to the host source will be reflected in the
container.

```bash
make -C docker developer
```

3. Connect to the Jupyter server

The `pdo_contracts` container created in the previous step starts a
Jupyter Lab server on port 8888. In the console for the container, you
should see instructions for how to connect to the server. It will look
something like:

```
contracts_container  |     To access the server, open this file in a browser:
contracts_container  |         file:///project/pdo/.local/share/jupyter/runtime/jpserver-43-open.html
contracts_container  |     Or copy and paste one of these URLs:
contracts_container  |         http://localhost:8888/lab?token=<hexnumber>
contracts_container  |         http://127.0.0.1:8888/lab?token=<hexnumber>
```

Open one of the `http` URLs (including the token) in your browser.

4. Build and install the example contract family

When you connect to the Jupyter Lab server, you will start on the
Launcher window. In the `Other` section of the launcher, click on
`Terminal` to open an interactive shell on the `pdo_contracts`
container.

The `developer` docker target does not pre-build any of the PDO
contract families. The first thing to do is build the exchange and
example contract families.

A brief comment about `Local.cmake`: this file allows for personalized
configuration of the PDO contracts build process. It is most often
used to specify the contract families that will be built by default
(the `CONTRACT_FAMILIES` list). The statement below will overwrite
any existing `Local.cmake`.


```bash
cd /project/pdo/dev
echo 'SET(CONTRACT_FAMILIES exchange-contract example-contract)' >| Local.cmake
make install
```


5. Open the tutorial

From the Jupyter launcher, navigate to `example/documents/index.ipynb`.
