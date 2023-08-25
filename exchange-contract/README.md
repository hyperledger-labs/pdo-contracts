# README

This repository contains a prototype implementation of protocols that could be used for enabling Non Fungible Tokens (NFTs) for confidential assets. The protocols and software are for reference purposes only and not intended for production usage.

## Problem Statement

Today Non-fungible tokens (NFTs) are created and traded for artifacts such as images, artworks, etc. where the NFT owner typically gets full rights to view/use the “raw bytes” of the artifact (e.g., download the image/artwork as is). Popular NFT smart contracts currently used such as ERC729 or ERC1155 (in Ethereum) offer little support to enable trustworthy trading of “policy-based usage of the artifact” without revealing the asset itself to the NFT owner. In the context of high-value confidential assets such as machine learning models or datasets that could be used to build the model itself, what we would like to be able to do is use NFTs not just to trade “raw-bytes of at the asset” but use NFTs to trade “policy-based usage-rights” to the high-value asset. 

In order create an NFT today, the asset author carries out three steps (see figure below): 1. Upload the asset into an asset store. 2. Create/Deploy an NFT smart contract in Ethereum (Ethereum NFTs, n.d.), Solana (Solana NFTs, n.d.), etc. The NFT smart contract at its core contains the URI to the asset, as well as specifies who owns the NFT. 3.  List the NFT for sale in an NFT marketplace such as OpenSea (OpenSea, n.d.) or OceanMarketplace (Ocean Protocol, n.d.).  A prospective buyer of the NFT initiates the buy-process via the Marketplace, which behind the scenes interacts with the NFT smart contract to ensure that Bob pays Alice, and the NFT ownership (as recorded in the NFT smart contract) changes from Alice to Bob.

<p align="center">
  <img src=./doc/nft_current_arch.png width="700">
</p>

We note the following inefficiencies about the above architecture that limits its usability for creating NFTs for high-value confidential assets:

- There is only a very weak binding between the NFT smart contract and the asset.  This is because, ownership of the NFT does not imply ownership of the asset held in the asset store. In other words, what the NFT owner gets to do with the asset is completely dependent on the implementation of the asset store. The NFT owner is constantly under the threat of facing a DoS attack, where the asset gets removed from the asset-store despite owning the NFT. 

- The architecture does not have any provision for the NFT smart contract to specify a policy around how the asset should be used, while at the time be able to communicate with the asset-store to ensure that the policy gets enforced.

- The NFT smart contract, being public in nature, cannot be used to either store any confidential information (such as a decryption key to the asset), or execute a compute-logic that contains confidential information. 

In this repo, we propose systems and protocols that address the above inefficiencies so that description/enforcement of asset-usage policies can be implemented as part of the NFT smart contract itself, thereby widely enhancing the scope of what can be done with NFTs.

## Solution Overview

Instead of implementing the NFT smart contract in a public blockchain, we propose to implement it in a Trusted Execution Environment (TEE)-enabled blockchain. Specifically, we focus on Intel SGX as our choice of TEE. The NFT smart contract is used to only implement ownership, but also implement/evaluate policy to be followed while using the confidential asset. The smart contract after policy evaluation generates asset-usage capabilities that get processed by capability execution engines implemented inside asset stores. The NFT smart contract shares confidential information with the asset store only after verifying its trustworthiness (per policies implemented inside the smart contract). In this regard, we also permit the possibiliy where the asset use environment itself is safe-guarded by TEEs. In order to implement the idea above, the NFT blockchain architecture shall be split into two pieces: a public Layer 1 blockchain such as Ethereum/Solana to act as the payment Layer, and a TEE-anchored Layer 2 blockchain, bridged to Layer 1, within which the NFT smart contract as described above is implemented. Receipt of payment from layer 1 is used to initiate transfer of ownership in layer 2. A pictorial overview of the proposed architecture is shown below.

<p align="center">
  <img src=./doc/nft_proposed_arch.png width="700">
</p>

## Contibutions of this Repository

We make the following contributions via this repository with regards to the problem statment and solution overview presented above.

### 1. Token-Guardian Protocol:

We describe protocols that could be used to implement the layer 2 NFT token object (see picture above) as well its interactions with the guardian service. The protocol is not restricted to a specific use-case, meaning we do not specify the nature of the confidential asset, and the nature of the capability execution engine located within the Guardian Service. This protocol does not make specific assumptions on Layer 1, the L1/L2 bridge and the marketplace. In other words, the protocol focuses on the following sub-system of the picture above, and consists only the Layer 2 and the Guardian service. Note that in the picture below, in addition to the NFT token object smart contract, we also have a Token Issuer Smart Contract which acts as a pont of entry for a prospective end-points (Alice in above picture) that wants to deploy a NFT smart contract. The protocol describes the steps for system initialization, creating (minting) the NFT token object, transfering token ownership and finally, invoking operations on the confidential asset subject to policies specified via the NFT token object. Please see [Token Guardian Protocol](./doc/Token_Guardian_Protocol_Description.pdf) for a more detailed description of the various steps involved in the protocol. 

<p align="center">
  <img src=./doc/token_guardian_arch.png width="700">
</p>

### 2. Protoype Implementation of the Token-Guardian Protocol:

We provide a prototype implementations for the token issuer and token object smart contracts necessary for the token guardian protocol. We chose [Hyperledger labs Private Data Objects](https://github.com/hyperledger-labs/private-data-objects) as our choice of Layer 2 TEE-anchored smart contract framework. PDO smart contracts written in C++, compiled into WASM byte-code and executed within the PDO Wawaka interpreter, where the interpreter itself is loaded and run within an Intel-SGX enclave. Please see [Hyperledger labs Private Data Objects](https://github.com/hyperledger-labs/private-data-objects) for details about deployment and security guarantees for Intel-SGX protected PDO smart contracts. 

For prototyping purposes, the interaction between token creator (Alice) and token purchaser (Bob) for ownership exchange is modeled via a fair-exchange protocol in which Alice exchanges ownerships of the token object for an asset of Bob that is tracked via an issuer (PDO) contract. The fair-exchange protocol has been orignally described at [Fair exchange Protocol](https://github.com/hyperledger-labs/private-data-objects/blob/v0.1.0/contracts/exchange/docs/exchange.md). This repo contains an implementation of the fair-exchange protocol that could be deployed using the wawaka PDO-interpreter, and acts as a foundation for creating the token object and token issuer smart contracts. 
 
### 3. Protoype Use Cases:

We provide implementation of two use cases to illustrate the token guardian protocol:

- In the first use case, the guardian service is also a PDO smart contracts, the asset is a confidential image and the token owner gets the right to perform certain operations (and get results) on the confidential image. The SW for this use case can be found at [Digital Asset](https://github.com/intel-sandbox/mbowman.pdo_da_contracts)

- In the second use case, the guardian service is implemented as a web server, the aset is an bird classification machine leanring model, and the token owner gets the right to perform inference using the machine learning model. The SW for this use case can be found at [Bird Classification](https://github.com/intel-sandbox/mbowman.pdo_classification_contracts)

# Installation Instructions

Please follow the instructions below to install the SW in bare metal on a single-node Ubuntu 20.04 system .

## Install PDO

Please follow instructions at https://github.com/hyperledger-labs/private-data-objects/blob/main/docs/host_install.md 
to install PDO, and deploy PDO TP on the host node. We assume SGX_MODE= SIM, PDO_INTERPRETER=wawaka and PDO_LEDGER_TYPE=ccf.

## Install Exchange Contracts

```bash
source $PDO_SOURCE_ROOT/build/_dev/bin/activate
git clone git@github.com:intel-sandbox/mbowman.pdo_exchange_contracts.git
cd mbowman.pdo_exchange_contracts/
make
make install
```

Set the env variable `EXCHANGE_SOURCE_ROOT` to point to the `mbowman.pdo_exchange_contracts` folder cloned above.

