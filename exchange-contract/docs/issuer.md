<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Issuer Contract #

The issuer contract maintains a balance sheet that captures ownership
of assets. The issuer contract is granted authority to issue assets by
a [vetting organization](vetting.md). That authority is captured in
the contract and passed to assertions of asset ownership.

The issuer contract restricts participants to see only their own asset
balances. Further, the creator of the issuer contract may issue assets
to a participant, but the contract does not grant the right to see the
balances after the initial issuance.

## State Update Methods ##

*TBD*

## Immutable Methods ##

*TBD*

## More on Escrow ##

Typically, the owner of an asset can both check the balance of assets
owned and transfer some or all of that balance to another
party. However, when an asset is escrowed to an agent, the owner loses
some rights to perform operations on the asset. For example, the owner
may continue to check on the number of assets owned, but cannot
transfer ownership of the asset to another party. For an asset that
has been escrowed, the agent takes responsibility to ensure that
ownership of assets is done under controlled circumstances.

The escrow agent is simply a signing authority. It can be a person, a
service, or another contract object. For the purpose of building a
fair exchange protocol, the assets are escrowed to the fair exchange
contract object which then arbitrates the transfer of ownership for
both parties.

The issuer contract class defines two methods for processing requests
from an escrow agent. The `disburse` method cancels an escrow. That
is, the asset owner regains all rights to the asset. The `claim`
method transfers ownership of assets. In each case, the escrow agent
provides the invoking participant with a proof (in the form of a
signed statement), that the operation can be performed.

## Interface Specification ##

```json
{
    "$schema": "http://json-schema.org/schema#",
    "title": "Exchange Interface",
    "id": "http://tradenet.org/pdo/wawaka/exchange/issuer#",

    "description": [
        ""
    ],

    "interface": {
        "initialize": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "initialize the issuer with the authority granted to issue assets",
                "this operation must be invoked before any other operation",
                "it must be invoked by creator"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "asset_authority_chain": {
                    "description": "",
                    "type": {
                        "$ref": "#/pdo/wawaka/exchange/basetypes/issuer_authority_chain_type"
                    },
                    "required": true
                }
            }
        },

        "get_asset_type_identifier": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "returns the asset type id associated with the vetting organization"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/basetypes/contract-id",
            }
            "PositionalParameters": [],
            "KeywordParameters":  {},
        },

        "get_verifying_key": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "returns the asset type id associated with the vetting organization"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/basetypes/ecdsa-public-key",
            }
            "PositionalParameters": [],
            "KeywordParameters":  {},
        },

        "add_approved_issuer": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "register the verifying key of an issuer of assets of the type associated",
                "with the vetting organization",
                "the vetting organization attests that the verifying key may be used to sign",
                "asset issuances"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "issuer_verifying_key": {
                    "description": "the ECDSA verifying key associated with an issuer object",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                }
            }
        },

        "get_issuer_authority": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "return a verifiable authority object",
                "dependency will include the current state hash of the vetting organization object"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#pdo/wawaka/exchange/basetypes/issuer_authority_chain_type"
            },
            "PositionalParameters": [],
            "KeywordParameters":  {
                "issuer_verifying_key": {
                    "description": "the ECDSA verifying key associated with an issuer object, must be authorized",
                    "type": {
                        "$ref": "#/pod/basetypes/ecdsa-public-key"
                    },
                    "required": true
                }
            }
        },

        "get_authority": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "return a verifiable authority object",
                "this is the object that establishes this issuers authority"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#pdo/wawaka/exchange/basetypes/issuer_authority_chain_type"
            },
            "PositionalParameters": [],
            "KeywordParameters":  {
                "issuer_verifying_key": {
                    "description": "the ECDSA verifying key associated with an issuer object, must be authorized",
                    "type": {
                        "$ref": "#/pod/basetypes/ecdsa-public-key"
                    },
                    "required": true
                }
            }
        },

        "issue": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "issue assets to an identity",
                "assigns ownership of assets in the issuers ledger",
                "must be invoked by the creator of the issuer object"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "owner_identity": {
                    "description": "ECDSA key for the new owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },
                "count": {
                    "description": "number of assets to be assigned to the new owner",
                    "type": "integer",
                    "required": true
                }
            }
        },

        "get_balance": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "get the current number of assets assigned to the invoker",
                "if the identity is unknown to the issuer, then the balance is 0"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": "integer",
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "get_entry": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "dump all information about the ledger entry assigned to the invoker"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": "#/pdo/basetypes/ledger-entry",
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "transfer": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "transfer ownership of some number of assets from the invoker to",
                "the specified identity"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "new_owner_identity": {
                    "description": "ECDSA key for the new owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },
                "count": {
                    "description": "number of assets to be assigned to the new owner",
                    "type": "integer",
                    "required": true
                }
            }
        },

        "escrow": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "place the assets assigned to the invoker in escrow to a given identity;",
                "the asset balance will be marked inactive.",
                "note that this method changes the state of the asset balance, but does",
                "not return an escrow attestion since the state change in this function",
                "must be committed first."
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "escrow_agent_identity": {
                    "description": "ECDSA key for the new owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },
                "count": {
                    "description": "number of assets to be escrowed",
                    "type": "integer",
                    "required": true
                }
            }
        },

        "escrow_attestation": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "create an attestation that assets owned by the invoker",
                "have been escrowed to a particular escrow agent"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/wawaka/exchange/basetypes/authoritative_asset_type"
            },
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "release": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "release from escrow the assets owned by the invoker",
                "sets transaction dependencies based on the input"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "release_request": {
                    "description": "a cancel escrow attestaton from an escrow agent",
                    "type": {
                        "$ref": "#/pdo/wawaka/exchange/basetypes/escrow_release_type"
                    },
                    "required": true
                }
            }
        },

        "claim": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "claim ownership of assets based on the signature of an escrow agent",
                "sets transaction dependencies based on the input"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "escrow_claim": {
                    "description": "a claim of ownership change from an escrow agent",
                    "type": {
                        "$ref": "#/pdo/wawaka/exchange/basetypes/escrow_claim_type"
                    },
                    "required": true
                }
            }
        }
    }
}
```
