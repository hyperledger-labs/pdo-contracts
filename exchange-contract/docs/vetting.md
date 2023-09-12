<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Vetting Organization Contract #

The vetting organization contract is a relatively simple contract that
provides a root for building trust chains of issuers for a particular
asset type. The expectation is that the actual vetting of asset issuers
happens interactively. The vetting organization contract provides a
means of recording decisions to grant authority to asset issuers.

## State Update Methods ##

*TBD*

## Immutable Methods ##

*TBD*

## Interface Specification ##

```json
{
    "$schema": "http://json-schema.org/schema#",
    "title": "interface for vetting organization contract object",
    "id": "http://tradenet.org/pdo/wawaka/exchange/vetting_organization#",

    "description": [
        "an object that serves as the signing authority for an organization",
        "that vets issuers of a specific asset type",
        "the vetting organization object represents a root of trust for issuers"
    ],

    "interface": {

        "initialize": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "set the basic information associated with the vetting organization",
                "must be invoked before any other operations"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "asset_type_identifier": {
                    "description": "the identity of the asset type that may be issued",
                    "type": {
                        "$ref": "#/pdo/basetypes/contract-id"
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
        }
    }
}
```
