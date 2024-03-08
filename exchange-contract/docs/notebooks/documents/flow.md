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

# Create an Issuer for Fungible Assets

The following examples assume that we want to support the exchange of red marbles and blue marbles. We assume the following identities:

* Blue Marbles Player Association (BMPA) -- an oversight organization that tracks blue marble banks
* Blue Marble Chapter (BMC) -- a local chapter of the BMPA with a large store of blue marbles
* Red Marbles Player Association (RMPA) -- an oversight organization that tracks red marble banks
* Red Marble Chapter (RMC) --a local chapter of the RMPA with a large store of red marbles
* Alice -- owns a number of blue marbles in in BMC
* Bob -- owners a number of red marbles in RMC

## Setup

The asset type and vetting organization contract objects allow for the establishment of a trust anchor to verify the integrity of exchange operations. That is, so long as we agree the type and vetting organization are trustworthy, then operations on assets derived from and approved by those organizations will be trustworthy as well. For each of the asset types, we need to set up the asset type, the vetting organization, and one or more issuers. We'll walk through the sequence of steps necessary for blue marbles; the same step is used to establish the trust anchors for the red marbles.

The BMPA creates an asset type contract object for the blue marbles. The asset type contract object defines a unique identifier (the current implementation uses the identity of the contract object itself). In addition, information about the type (e.g. name, description, or a scheme for data associated with assets of that type) can be provided.

The BMPA creates a vetting organization contract object where it can record record and report on authorizations for organizations that issue blue marbles. When initializing the contract object, the player association provides the type of asset that will be issued by authorized organizations.

Each local chapter that will issue blue marbles creates an issuer contract object. For now, we'll just create the issuer contract object for the BMC chapter. When it is created, the BMC contract object holds no authority to issue assets; that is, the issuer contract refuses to issue assets until the issuer has been authorized. It must receive that authority from the BMPA. Out of band, the BMPA verifies the integrity of BMP and records in the BMPA vetting organization contract object authorization for the BMP issuer contract object to issue blue marble assets. Once the authorization is complete, the BMC can retrieve a representation of the authorization from the BMPA contract object (the structure of the authorization will be described later). That authorization is then stored in the BMC issuer contract object.

Once the authority from the BMPA has been stored, the BMP may issue blue marble assets to its members. The current implementation of the issuer contract does not limit the amount of assets that can be issued; it would be a relatively straightforward extension for the BMPA authorization to include a maximum number of assets that could be issued; a constraint that would be enforced by the BMC issuer contract.

## Simple Fair Exchange

The fair exchange contract enables a simple, bi-lateral exchange of assets that are managed by different issuers. For example, Alice and Bob (out of band) decide to exchange 100 red marbles for 100 blue marbles. A fair exchange contract coordinates the exchange of ownership to guarantee that both sides receive their assets (or neither does).

![Figure 1. Simple Fair Exchange Transaction Flow](../images/exchange_flow.png)

Figure 1 shows the flow of transactions that take place in a fair exchange. Each of these steps is described below.

Alice creates an exchange contract object.

Alice initializes the exchange contract object with the requested number and type of asset (i.e. the identifier from the red marble asset type contract object). While it is not shown in the figure, Alice also provides the identity of a vetting organization that she trusts to authorize red marble issuers. In this case, Alice uses the verifying key for the RMPA object.

In preparation for offering her blue marbles for exchange, Alice escrows her holding in the BMC naming the exchange contract object as the escrow agent. Escrowing the blue marbles ensures that Alice will not use those marbles in another transaction until the exchange contract object allows it.

Alice records the blue marbles offered for exchange in the exchange contract object. To do this, she requests a proof of escrow from the BMC. The proof contains three things: details about the asset (i.e. 100 blue marbles), proof that a vetting organization authorized the issuer to issue blue marbles, and the escrow claim. The escrow proof is set in the context of a particular instance of the state of the BMC contract object. That is, the proof of escrow holds if and only if the current state of the BMC (which captures that Alice's holding has been escrowed) has been committed to the ledger. This requirement is captured by transaction dependencies that are enforced by the Coordination and Commit transaction processor in Sawtooth. Figure 2 shows the dependencies between state update transactions that must be enforced by the TP.

Once Alice finishes, Bob can examine the exchange object and see that Alice is offering 100 blue marbles in exchange for 100 red marbles. Further, Bob can look at the authorization for Alice's offer to convince himself that the Alice's issuer is appropriately vetted. Once satisfied, Bob goes through the same process as Alice: he escrows his holding of red marbles, naming the exchange contract object as the escrow agent.

Bob requests a proof of escrow from the RMC and submits it as the response to Alice's request. The contract in the exchange object verifies the type and quantity of the asset and also that Alice trusts Bob's issuer (that is, that the RMC was vetted by the RMPA). Assuming Bob's response is accepted, the exchange contract object enters a "completed" state where no further changes are accepted.

To complete the exchange, Bob and Alice independently request a claim from the exchange object that tells the issuers to transfer ownership of assets. The claim contains information about the old and new owners, and the identity of the exchange object (which must match the escrow state of the assets). As with the escrow proof, the claim is situated in the context of a particular state commit. That is, the claim is not valid unless the completed state of the exchange object is committed to the ledger.

 ![Figure 2. Fair Exchange Transaction Dependencies](../images/dependencies.png)
 

```python

```
