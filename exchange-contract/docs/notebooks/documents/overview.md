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

# Exchange Contract Family Overview

The Exchange contract family is a suite of contracts that demonstrate many of the capabilities of the private data objects technologies.Three basic contracts define the elements of the Exchange contract family: the
asset type contract, the vetting organization contract, and the issuer contract. Three additional contracts extend the Exchange contract family for trading potentially confidential assets using non-fungible tokens.

## Contracts for Traditional Assets

An *asset type* contract object defines a unique, shared identifier for a type
of digital asset and a schema for the representation for assets of that
type. For example, we might define an asset type contract object for blue
marbles. Since the identifier for the contract object is unique, it provides a
shared, unique identifier that can be used to refer to assets that are blue
marbles.

A *vetting organization* contract object manages a list of contract objects
authorized to issue assets of a particular type. While actual vetting of an
issuer occurs outside the contract object, the object provides a means of
recording the decision to authorize an issuer. In this way, the vetting
organization contract object provides a root of trust for issuers of a
particular asset type. Continuing the blue marble example, the Blue Marble
Players Association might create a vetting organization object to record the
identities of local chapters that may issue blue marble holdings to their
members.

The *issuer* contract object maintains a balance sheet that captures ownership
of assets of a particular type. The issuer contract allows the creator of the
contract object to issue assets (that is, assign ownership of assets to a
particular individual). However, once the initial issuance occurs,
confidentiality of transactions and balances is maintained; in this case, even
the creator of the issuer contract object is not granted the right to examine
the quantity of assets owned by an individual after the initial issuance. Local
chapters of the Blue Marble Players Association each create an issuer contract
object to assign ownership of marbles to their members. Once the initial
issuance is complppete, members can trade marbles, transfer ownership, or
exchange different kinds of marbles in complete confidentiality. And, for those
who trust the Blue Marble Players Association, those transactions can span local
chapters.

While the issuer contract object supports simple ownership transfer, more
complex multi-party exchanges are managed through additional contracts. For
example, an exchange contract mediates a fair exchange of different kinds of
marbles (e.g. Alice trades her red marbles for Bob's blue marbles). More complex
exchanges like a blind auction can be implemented as well.

A [detailed walk through](flow.ipynb) of the process is availble.

## Contracts for Confidential, Non-Fungible Assets

One blue marble is generally indistinguishable from another; that is, blue
marbles are considered "fungible". In contrast, each red sports car is a unique
thing with a distinct title of ownership; that is, red sports cards are
considered "non-fungible". In order to represent non-fungible assets like a red
sports car, the Exchange contract family defines a special kind of issuer,
called a *token issuer*. Like the issuers for fungible tokens, the token issuer
has an asset type and vetting organization. A token issuer contract object
"mints" a fixed number of *tokens* (another kind of contract object) that
correspond to unique instances of the asset type. To make this more concrete,
the asset type might refer to red sports cars (a generic kind of car), the token
issuer is like a manufacturer that creates specific instances (tokens) of the
red sports car. Each token represents a specific red sports car.

The red sports car analogy works well for traditional sense of ownership (where
ownership implies "possession"). However, the Exchange contract family extends
the notion of ownership to imply a right to use an asset for a specific
purpose. In this case, the asset itself (the red sports car), is wrapped by a
*guardian* contract and the token issuer mints tokens that grant the right to
use the guarded asset. Pushing the analogy well beyond reason, we might think of
the token, in this case, as the right to drive the car for a specific time
period.

While the implementation of the token issuer, token, and guardian contract are
relatively simplistic, they provide a basis for defining and enforcing a rich
set of policies. Other contract families can use these basic building blocks for
many applications like the right to use digital images for specific purposes or
the right to query a classification model.

```python

```
