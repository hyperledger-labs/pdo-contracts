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

# PDO Contracts Launch Page #


[Hyperledger Private Data Objects](https://github.com/hyperledger-labs/private-data-objects) operates as a Hyperledger Labs project. This code is provided solely to demonstrate basic PDO mechanisms and to facilitate
collaboration to refine PDO architecture and define minimum viable product requirements.

**The PDO contracts code provided here is prototype code and not intended for production use.**


## Getting Started


There are a number of configuration options for interacting with PDO contracts. More information can be found in the [Getting Started](documents/getting_started.ipynb) notebook.




## Contract Families


### Exchange


The Exchange contract family is a suite of contracts that demonstrate many of the capabilities of the private data objects technologies. Three basic contracts define the elements of the Exchange contract family: the asset type contract, the vetting organization contract, and the issuer contract. Three additional contracts extend the Exchange contract family for trading potentially confidential assets using non-fungible tokens.

To experiment with these contracts, explore the [Exchange Contract Family notebook](exchange/index.ipynb)



### Digital Assets


The Digital Assets contract family implements a basic digital asset for bitmap images. The contracts extend the asset and token contracts in the Exchange contract family for sharing images with well-defined policies.



### Inference


The Inference contract family provides contracts for creating a confidentiality
preserving policy-wrapper around the usage of a machine learning (ML) model.
At its core, the implementation uses a token contract to  specify and enforce
policies to be followed while using the ML model for inferecing operations.

To experiment with inference contracts, explore the
[Inference Contract Family notebook](inference/index.ipynb)
