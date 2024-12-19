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

# Ensure that the default target builds the contracts
all : build_contracts

# Include local customizations if they are available
-include make.loc

# CONTRACTS_USER_UID, CONTRACTS_GROUP_UID --
#   The UID/GID for the user accounts that will be created in the container; this is
#   important especially when the containers are being used for development; note
#   that the user/group identifiers need to have write access to the xfer directory
CONTRACTS_USER_UID ?= $(shell id -u)
CONTRACTS_GROUP_UID ?= $(shell id -g)

DOCKER_COMMAND ?= docker

ifndef DOCKER_COMPOSE_COMMAND
  DOCKER_COMPOSE_COMMAND := $(shell command -v docker-compose 2> /dev/null)
  ifndef DOCKER_COMPOSE_COMMAND
    $(warning "docker-compose command is not available, using docker compose")
    DOCKER_COMPOSE_COMMAND := $(DOCKER_COMMAND) compose
  endif
endif

# Turns out that setting the script directory from the Makefile's name
# does not work very well if the path contains spaces in the name; in
# fact lots of things break very badly; set this explicitly
DOCKER_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
CONTRACTS_SOURCE_ROOT = $(abspath $(DOCKER_DIR)/..)

# CONTRACTS_REPO --
#   The URL or path to the git repository, the default uses the current repository
#   though it might be reasonable to build a particular branch from the primary
#   PDO contracts repository at https://github.com/hyperledger-labs/pdo-contracts.git
# CONTRACTS_BRANCH --
#   The branch that will be used for the containers, the default is the current
#   branch, a reasonable alternative would be to use the 'main' branch from the
#   public PDO contracts repository
CONTRACTS_REPO ?= $(CONTRACTS_SOURCE_ROOT)
CONTRACTS_BRANCH ?= $$(git -C $(CONTRACTS_REPO) rev-parse --abbrev-ref HEAD)

CONTRACTS_VERSION ?= $$(					\
	if [ -d $(DOCKER_DIR)/repository ]; then		\
		cd $(DOCKER_DIR)/repository; bin/get_version;	\
	else							\
		echo "latest";					\
	fi )

PDO_VERSION ?= $$(									\
	if [ -d $(DOCKER_DIR)/repository ]; then					\
		cd $(DOCKER_DIR)/repository/private-data-objects; bin/get_version;	\
	else										\
		echo "latest";								\
	fi )

PDO_REGISTRY ?= ''

# DOCKER BUILD
DOCKER_USERNAME = $(LOGNAME)
DOCKER_BUILDARGS += --build-arg UID=$(CONTRACTS_USER_UID)
DOCKER_BUILDARGS += --build-arg GID=$(CONTRACTS_GROUP_UID)
DOCKER_BUILDARGS += --build-arg CONTRACTS_VERSION=$(CONTRACTS_VERSION)
DOCKER_BUILDARGS += --build-arg PDO_VERSION=$(PDO_VERSION)
DOCKER_BUILDARGS += --build-arg PDO_REGISTRY=$(PDO_REGISTRY)
DOCKER_ARGS = $(DOCKER_BUILDARGS)

# The CONTRACT_FAMILIES variable contains a list of contract families
# to build into the container. Note that there is no versioning of
# containers for the contract families they contain. This can be
# overridden in make.loc
CONTRACT_FAMILIES ?= $(notdir $(wildcard $(CONTRACTS_SOURCE_ROOT)/*-contract))

# for the most part this is just used to force rebuild when the
# PDO contracts has changed
TIMESTAMP := $(shell /bin/date "+%Y%m%d%H%M%S")

rebuild_contracts : repository models
	$(DOCKER_COMMAND) build $(DOCKER_ARGS) \
		--build-arg REBUILD=$(TIMESTAMP) \
		--tag pdo_contracts:$(CONTRACTS_VERSION) \
		--file $(DOCKER_DIR)/pdo_contracts.dockerfile .

build_contracts : DOCKER_BUILDARGS+=--build-arg CONTRACT_FAMILIES="$(CONTRACT_FAMILIES)"
build_contracts : repository models
	- echo "Build contract families: $(CONTRACT_FAMILIES)"
	$(DOCKER_COMMAND) build $(DOCKER_ARGS) \
		--tag pdo_contracts:$(CONTRACTS_VERSION) \
		--file $(DOCKER_DIR)/pdo_contracts.dockerfile .

clean_contracts :
	- $(DOCKER_COMMAND) rmi -f pdo_contracts:$(CONTRACTS_VERSION)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# this target requires a little explanation... when the private-data-objects
# submodule is updated, it will generally lack a branch name (git checkout
# results in a detached HEAD state). in order to build from the submodule
# we need the submodule to belong to a branch; in this case we are just going
# to create a branch that is named by the current pdo-contracts version.
# PDO_SOURCE_ROOT must be set to the submodule directory to build correctly.

build_pdo_images : repository
	PDO_SOURCE_ROOT=$(DOCKER_DIR)/repository/private-data-objects \
		cd $(DOCKER_DIR)/repository/private-data-objects && git checkout -B pdo-contracts-${CONTRACTS_VERSION}
	PDO_SOURCE_ROOT=$(DOCKER_DIR)/repository/private-data-objects \
		make -C $(DOCKER_DIR)/repository/private-data-objects/docker all
	PDO_SOURCE_ROOT=$(DOCKER_DIR)/repository/private-data-objects \
		make -C $(DOCKER_DIR)/repository/private-data-objects/docker clean_repository

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# For the purposes of testing, we just use the resnet model for
# classifying images. To use a different model, you should be able
# to override these variables in make.loc
OPENVINO_MODEL_BASE_URL ?= https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2
OPENVINO_MODEL ?= resnet50-binary-0001

models :
	mkdir -p $(DOCKER_DIR)/models/1
	wget -P $(DOCKER_DIR)/models/1 ${OPENVINO_MODEL_BASE_URL}/${OPENVINO_MODEL}/FP32-INT1/${OPENVINO_MODEL}.bin
	wget -P $(DOCKER_DIR)/models/1 ${OPENVINO_MODEL_BASE_URL}/${OPENVINO_MODEL}/FP32-INT1/${OPENVINO_MODEL}.xml

clean_models :
	rm -rf $(DOCKER_DIR)/models

OPENVINO_CONTAINER=openvino/model_server:latest
OPENVINO_RUN_ARGS += -u $(CONTRACTS_USER_ID):$(CONTRACTS_GROUP_ID)
OPENVINO_RUN_ARGS += -v $(DOCKER_DIR)/models/:/models/
OPENVINO_RUN_ARGS += --rm
OPENVINO_RUN_COMMAND ?= --model_path /models/ --model_name resnet --port 9000 --shape auto --grpc_bind_address 127.0.0.1

run_openvino : models
	$(DOCKER_COMMAND) run $(OPENVINO_RUN_ARGS) -d --name openvino_container $(OPENVINO_CONTAINER) \
		$(OPENVINO_RUN_COMMAND)

stop_openvino :
	- $(DOCKER_COMMAND) rm -f openvino_container

# -----------------------------------------------------------------
# -----------------------------------------------------------------
DOCKER_RUN_ARGS += -v $(DOCKER_DIR)/xfer/:/project/pdo/xfer
DOCKER_RUN_ARGS += --network host
DOCKER_RUN_ARGS += --rm
DOCKER_RUN_COMMAND ?= "stty cols $$(tput cols) rows $$(tput lines) && bash"

stop_contracts :
	- $(DOCKER_COMMAND) rm -f contracts_container

run_contracts : build_contracts stop_contracts
	$(DOCKER_COMMAND) run $(DOCKER_RUN_ARGS) -it --name contracts_container pdo_contracts:${CONTRACTS_VERSION} \
		-c $(DOCKER_RUN_COMMAND)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
JUPYTER_SERVICE_HOST ?= $(PDO_HOSTNAME)
JUPYTER_LEDGER ?= $(PDO_LEDGER_URL)
JUPYTER_MODE ?= build

DOCKER_JUPYTER_COMMAND = "/project/pdo/tools/start_jupyter.sh"
DOCKER_JUPYTER_COMMAND += -l $(JUPYTER_LEDGER)
DOCKER_JUPYTER_COMMAND += --service-host $(JUPYTER_SERVICE_HOST)
DOCKER_JUPYTER_COMMAND += -m $(JUPYTER_MODE)

stop_jupyter :
	- $(DOCKER_COMMAND) rm -f jupyter_container

run_jupyter : build_contracts stop_jupyter
	$(DOCKER_COMMAND) run $(DOCKER_RUN_ARGS) -it --name jupyter_container pdo_contracts:${CONTRACTS_VERSION} \
		$(DOCKER_JUPYTER_COMMAND)

# -----------------------------------------------------------------
# We need a repository with the source for the branch we are going
# to build. In theory this could just be a copy of the local source
# tree but it might contain other artifacts. So instead we clone
# the contracts with just a single branch in it. The storage and
# performance requirements are relatively low.
# -----------------------------------------------------------------
repository :
	git clone --single-branch --branch $(CONTRACTS_BRANCH) --recurse-submodules $(CONTRACTS_REPO) repository

clean_repository :
	rm -rf $(DOCKER_DIR)/repository

# -----------------------------------------------------------------
# Testing uses docker-compose to build a set of images that will be configured
# to run with localhost as the interface. in order to get a clean shutdown we
# don't use a docker-compose specification for the base, ccf_base and services_base
# containers. since we are rebuilding the contracts, we force recompilation of these
# images from the rebuilt contracts. the corresponding images are built using docker
# build instead of being included in the docker-compose.
# -----------------------------------------------------------------

# The docker compose files use a special profile to run the openvino and
# guardian services. If the inference contract family is to be built
# and tested, then add the profile to run the two extra containers.
COMPOSE_PROFILES ?=
ifeq ($(findstring inference-contract,$(CONTRACT_FAMILIES)),inference-contract)
	COMPOSE_PROFILES += --profile inference
endif

# TEST_ARGS provides additional parameters for the compose
# operations for running the test environment; generally
# this would set in a make.loc
TEST_COMPOSE_ARGS += -f test.yaml

test : clean_config clean_repository build_contracts
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(TEST_COMPOSE_ARGS) $(COMPOSE_PROFILES) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
	 	$(DOCKER_COMPOSE_COMMAND) $(TEST_COMPOSE_ARGS) down

JUPYTER_COMPOSE_ARGS += -f test_jupyter.yaml

test_jupyter : clean_config clean_repository build_contracts
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_COMPOSE_ARGS) $(COMPOSE_PROFILES) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_COMPOSE_ARGS) down

JUPYTER_MULTIUSER_COMPOSE_ARGS += -f test_multiuser_jupyter.yaml

test_multiuser_jupyter : clean_config clean_repository build_contracts
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_MULTIUSER_COMPOSE_ARGS) $(COMPOSE_PROFILES) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_MULTIUSER_COMPOSE_ARGS) down

# The example target builds and runs only the example contract family. This
# is intended to be a very simple way to test drive PDO contracts as a user
# and as a contract developer.

example : CONTRACT_FAMILIES=example-contract
example : clean_config clean_repository build_contracts
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		CONTRACTS_SOURCE_ROOT=$(CONTRACTS_SOURCE_ROOT) \
		$(DOCKER_COMPOSE_COMMAND) $(TEST_COMPOSE_ARGS) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(TEST_COMPOSE_ARGS) down

example_jupyter : CONTRACT_FAMILIES=exchange-contract example-contract
example_jupyter : clean_config clean_repository build_contracts
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		CONTRACTS_SOURCE_ROOT=$(CONTRACTS_SOURCE_ROOT) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_COMPOSE_ARGS) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_COMPOSE_ARGS) down

# The developer target creates a container with no contracts built or
# installed. When the container starts, the current contract source
# root is mounted at /project/pdo/dev.  In addition, a Jupyter server
# is started. The Jupyter launcher provides a shell window that can be
# used to interact with the PDO installation to build and install
# contracts.
DEVELOP_COMPOSE_ARGS += -f test_dev.yaml
developer : CONTRACT_FAMILIES=
developer : clean_config build_contracts
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		CONTRACTS_SOURCE_ROOT=$(CONTRACTS_SOURCE_ROOT) \
		$(DOCKER_COMPOSE_COMMAND) $(DEVELOP_COMPOSE_ARGS) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		$(DOCKER_COMPOSE_COMMAND) $(JUPYTER_COMPOSE_ARGS) down

# -----------------------------------------------------------------
# Cleaning is a bit interesting because the containers don't go away
# unless they are told to very nicely. Until they go away they hold onto
# referenced images. Clean make sure that everything is cleaned up
# across the board.
# -----------------------------------------------------------------
_IMAGES_=$(shell $(DOCKER_COMMAND) images -a --filter=dangling=true -q)
_CONTAINERS_=$(shell $(DOCKER_COMMAND) ps --filter=status=exited --filter=status=created -q)
clean_images : clean_contracts
	@ if [ ! -z "$(_CONTAINERS_)" ]; then $(DOCKER_COMMAND) rm -f $(_CONTAINERS_); fi
	@ if [ ! -z "$(_IMAGES_)" ]; then $(DOCKER_COMMAND) rmi -f $(_IMAGES_); fi

clean_config :
	@ rm -f $(DOCKER_DIR)/xfer/ccf/keys/*.pem $(DOCKER_DIR)/xfer/ccf/etc/*.toml
	@ rm -f $(DOCKER_DIR)/xfer/services/keys/*.pem $(DOCKER_DIR)/xfer/services/etc/*.toml
	@ rm -f $(DOCKER_DIR)/xfer/services/etc/site.psh

clean : clean_images clean_config clean_repository

.PHONY: clean clean_images clean_config clean_repository clean_models
.PHONY: test
.PHONY: run_openvino run_contracts run_jupyter
.PHONY: stop_openvino stop_contracts stop_jupyter
.PHONY: build_openvino build_contracts rebuild_contracts
