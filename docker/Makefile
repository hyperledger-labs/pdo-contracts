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

# Include local customizations if they are available
-include make.loc

# CONTRACTS_USER_UID, CONTRACTS_GROUP_UID --
#   The UID/GID for the user accounts that will be created in the container; this is
#   important especially when the containers are being used for development; note
#   that the user/group identifiers need to have write access to the xfer directory
CONTRACTS_USER_UID ?= $(shell id -u)
CONTRACTS_GROUP_UID ?= $(shell id -g)

# Turns out that setting the script directory from the Makefile's name
# does not work very well if the path contains spaces in the name; in
# fact lots of things break very badly; set this explicitly
DOCKER_DIR ?= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# CONTRACTS_REPO --
#   The URL or path to the git repository, the default uses the current repository
#   though it might be reasonable to build a particular branch from the primary
#   PDO contracts repository at https://github.com/hyperledger-labs/pdo-contracts.git
# CONTRACTS_BRANCH --
#   The branch that will be used for the containers, the default is the current
#   branch, a reasonable alternative would be to use the 'main' branch from the
#   public PDO contracts repository
CONTRACTS_REPO ?= $(abspath $(DOCKER_DIR)/..)
CONTRACTS_BRANCH ?= $$(git -C $(CONTRACTS_REPO) rev-parse --abbrev-ref HEAD)

CONTRACTS_VERSION ?= $$(					\
	if [ -d $(DOCKER_DIR)/contracts ]; then			\
		cd $(DOCKER_DIR)/contracts; bin/get_version;	\
	else							\
		echo "latest";					\
	fi )

PDO_VERSION ?= $$(									\
	if [ -d $(DOCKER_DIR)/contracts ]; then						\
		cd $(DOCKER_DIR)/contracts/private-data-objects; bin/get_version;	\
	else										\
		echo "latest";								\
	fi )

# DOCKER BUILD
DOCKER_USERNAME = $(LOGNAME)
DOCKER_BUILDARGS += --build-arg UID=$(CONTRACTS_USER_UID)
DOCKER_BUILDARGS += --build-arg GID=$(CONTRACTS_GROUP_UID)
DOCKER_BUILDARGS += --build-arg CONTRACTS_VERSION=$(CONTRACTS_VERSION)
DOCKER_BUILDARGS += --build-arg PDO_VERSION=$(PDO_VERSION)
DOCKER_ARGS = $(DOCKER_BUILDARGS)

IMAGES=contracts

# for the most part this is just used to force rebuild when the
# PDO contracts has changed
TIMESTAMP := $(shell /bin/date "+%Y%m%d%H%M%S")

all : $(addprefix build_,$(IMAGES))

rebuild_% : contracts
	@ docker build $(DOCKER_ARGS) \
		--build-arg REBUILD=$(TIMESTAMP) \
		--tag pdo_$*:$(CONTRACTS_VERSION) \
		--file $(DOCKER_DIR)/pdo_$*.dockerfile .

build_% : contracts
	@ docker build $(DOCKER_ARGS) \
		--tag pdo_$*:$(CONTRACTS_VERSION) \
		--file $(DOCKER_DIR)/pdo_$*.dockerfile .

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# For the purposes of testing, we just use the resnet model for
# classifying images. To use a different model, you should be able
# to override these variables in mkae.loc
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
OPENVINO_RUN_ARGS += -p 127.0.0.1:9000:9000
OPENVINO_RUN_COMMAND ?= --model_path /models/ --model_name resnet --port 9000 --shape auto

run_openvino : models
	docker run $(OPENVINO_RUN_ARGS) -d --name openvino_container $(OPENVINO_CONTAINER) \
		$(OPENVINO_RUN_COMMAND)

stop_openvino :
	- docker rm -f openvino_container

# -----------------------------------------------------------------
# -----------------------------------------------------------------
clean_% :
	@ docker rmi -f pdo_$*

# -----------------------------------------------------------------
# -----------------------------------------------------------------
DOCKER_RUN_ARGS += -v $(DOCKER_DIR)/xfer/:/project/pdo/xfer
DOCKER_RUN_ARGS += --network host
DOCKER_RUN_COMMAND ?= "stty cols $$(tput cols) rows $$(tput lines) && bash"

stop_contracts :
	- docker rm -f contracts_container

run_contracts : build_contracts stop_contracts
	docker run $(DOCKER_RUN_ARGS) -it --name contracts_container pdo_contracts:${CONTRACTS_VERSION} \
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
	- docker rm -f jupyter_container

run_jupyter : build_contracts stop_jupyter
	docker run $(DOCKER_RUN_ARGS) -it --name jupyter_container pdo_contracts:${CONTRACTS_VERSION} \
		$(DOCKER_JUPYTER_COMMAND)

# -----------------------------------------------------------------
# We need a repository with the source for the branch we are going
# to build. In theory this could just be a copy of the local source
# tree but it might contain other artifacts. So instead we clone
# the contracts with just a single branch in it. The storage and
# performance requirements are relatively low.
# -----------------------------------------------------------------
contracts :
	git clone --single-branch --branch $(CONTRACTS_BRANCH) --recurse-submodules $(CONTRACTS_REPO) contracts

clean_contracts :
	rm -rf contracts

# -----------------------------------------------------------------
# Testing uses docker-compose to build a set of images that will be configured
# to run with localhost as the interface. in order to get a clean shutdown we
# don't use a docker-compose specification for the base, ccf_base and services_base
# containers. since we are rebuilding the contracts, we force recompilation of these
# images from the rebuilt contracts. the corresponding images are built using docker
# build instead of being included in the docker-compose.
# -----------------------------------------------------------------

# TEST_ARGS provides additional parameters for the compose
# operations for running the test environment; generally
# this would set in a make.loc
TEST_COMPOSE_ARGS += -f test.yaml

build_test : contracts models build_contracts

test : clean_config clean_contracts build_test
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
	 	docker-compose $(TEST_COMPOSE_ARGS) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
	 	docker-compose $(TEST_COMPOSE_ARGS) down

JUPYTER_COMPOSE_ARGS += -f test_jupyter.yaml

test_jupyter : clean_config clean_contracts build_test
	- PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		docker-compose $(JUPYTER_COMPOSE_ARGS) up --abort-on-container-exit
	PDO_VERSION=$(PDO_VERSION) CONTRACTS_VERSION=$(CONTRACTS_VERSION) \
		docker-compose $(JUPYTER_COMPOSE_ARGS) down

# -----------------------------------------------------------------
# Cleaning is a bit interesting because the containers don't go away
# unless they are told to very nicely. Until they go away they hold onto
# referenced images. Clean make sure that everything is cleaned up
# across the board.
# -----------------------------------------------------------------
_IMAGES_=$(shell docker images -a --filter=dangling=true -q)
_CONTAINERS_=$(shell docker ps --filter=status=exited --filter=status=created -q)
clean_images : $(addprefix stop_,$(IMAGES))
	@ if [ ! -z "$(_CONTAINERS_)" ]; then docker rm -f $(_CONTAINERS_); fi
	@ if [ ! -z "$(_IMAGES_)" ]; then docker rmi -f $(_IMAGES_); fi

clean_config :
	@ rm -f $(DOCKER_DIR)/xfer/ccf/keys/*.pem $(DOCKER_DIR)/xfer/ccf/etc/*.toml
	@ rm -f $(DOCKER_DIR)/xfer/services/keys/*.pem $(DOCKER_DIR)/xfer/services/etc/*.toml
	@ rm -f $(DOCKER_DIR)/xfer/services/etc/site.psh

clean : clean_images clean_config clean_contracts clean_models

.PHONY: clean clean_images clean_config clean_contracts
.PHONY: build_test test
.PHONY: run_ccf run_client run_services
