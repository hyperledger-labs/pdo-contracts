# ------------------------------------------------------------------------------
# Copyright 2023 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

# PURPOSE: run test suite

# For a complete, automated test environment we need PDO ledger, PDO services, a
# PDO client that is extended with the contract source. For complete testing we
# need an OpenVINO model server and the associated guardian service. We can
# assume that all components are running on localhost. PDO provides the docker
# and docker compose files that are necessary for running the PDO services.
# The contracts code must be built from a client image that has the same version
# as the pdo code in the contracts repository.

# One possibility is to build our own images for PDO ledger, PDO services and
# PDO client using the pdo submodule in the contracts repo. The advantage of
# this is that we know the versions will match. THe disadvantage is that it
# might be a lot of work. Although we might trust docker to "get it right" if we
# rebuild layers that have already been built. This seems like the best approach.

# When building the client one

# PURPOSE: develop and test contracts with clean

ARG PDO_REGISTRY
ARG PDO_VERSION
FROM ${PDO_REGISTRY}pdo_client:${PDO_VERSION}

# -----------------------------------------------------------------
# Install the necessary dependencies
# -----------------------------------------------------------------
USER 0:0
ENV DEBIAN_FRONTEND "noninteractive"
RUN apt-get update \
    && apt-get install -y -q \
    libgl1

# Many of the dependencies should be addressed with the installation
# of the PDO client including the common contracts, the wasi toolkit
# and all of the WAMR toolchain

# This should set up all we need for the jupyter server
ARG UID=1000
ARG GID=${UID}
USER ${UID}:${GID}
RUN --mount=type=cache,uid=${UID},gid=${GID},target=/project/pdo/.cache/pip \
    /project/pdo/run/bin/pip install notebook papermill ipywidgets jupytext bash_kernel
RUN /project/pdo/run/bin/python -m bash_kernel.install

# -----------------------------------------------------------------
# Set up the contract source and configure for specified tests
# -----------------------------------------------------------------

# this code assumes that the Makefile creates a directory with the
# contract source and mounts that directory

# copy the source files into the image
WORKDIR /project/pdo
COPY --chown=${UNAME}:${UNAME} repository /project/pdo/contracts

# Local.cmake allows for custom overrides of the contracts to be
# tested, the CONTRACT_FAMILIES variable in the cmake files specifies
# which families should be built.
ARG CONTRACT_FAMILIES="exchange-contract digital-asset-contract inference-contract"
RUN echo "SET(CONTRACT_FAMILIES ${CONTRACT_FAMILIES})" > /project/pdo/contracts/Local.cmake

# copy the tools because we want to be able to use them even without a
# mount point after the container is created
WORKDIR /project/pdo/tools
COPY --chown=${UNAME}:${UNAME} tools/*.sh ./

# build it!!!
ARG UID=1000
ARG GID=${UID}
RUN --mount=type=cache,uid=${UID},gid=${GID},target=/project/pdo/.cache/pip \
    /project/pdo/tools/build_contracts.sh

ENTRYPOINT [ "/bin/bash" ]
