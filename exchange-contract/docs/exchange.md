<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Fair Exchange Contract #

The fair exchange contract handles the bi-lateral transfer of asset
ownership between ledgers. For example, Alice gives three blue marbles
to Bob in exchange for four red marbles. This transaction must
atomically transfer ownership of assets in the blue marble asset
ledger and the red marble asset ledger. There are several different
interactions that would be reasonable for a fair exchange; this is
just one implementation.

## State Update Methods ##

*TBD*

## Immutable Methods ##

*TBD*

## Interface Specification ##

```json
{
    "$schema": "http://json-schema.org/schema#",
    "title": "Exchange Interface",
    "id": "http://tradenet.org/pdo/contract/wawaka/exchange#",

    "description": [
        ""
    ],

    "interface": {
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

        "initialize": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "initialize the details of the requested exchange",
                "this operation must be invoked before any other operation",
                "it must be invoked by creator"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "asset_request": {
                    "description": "",
                    "type": {
                        "$ref": "#/pdo/wawaka/exchange/basetypes/asset_request_type"
                    },
                    "required": true
                },

                "offered_authoritative_asset": {
                    "description": "",
                    "type": {
                        "$ref": "#/pdo/wawaka/exchange/basetypes/authoritative_asset_type"
                    },
                    "required": true
                }
            }
        },

        "cancel": {
            "//": "-----------------------------------------------------------------",
            "description": [
                ""
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "cancel_attestation": {
            "//": "-----------------------------------------------------------------",
            "description": [
                ""
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/wawaka/exchange/basetypes/escrow_cancel_type"
            },
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "examine_offered_asset": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "return the offered authoritative asset"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/wawaka/exchange/basetypes/authoritative_asset_type"
            }
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "examine_requested_asset": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "return the asset request object"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/wawaka/exchange/basetypes/asset_request_type"
            },
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "exchange_asset": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "submit an asset in response to the asset request",
                "the submitted asset must be escrowed to the exchange object",
                "the submitted asset must match the request"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters":  {
                "exchanged_authoritative_asset": {
                    "description": "",
                    "type": {
                        "$ref": "#/pdo/wawaka/exchange/basetypes/authoritative_asset_type"
                    },
                    "required": true
                }
            }
        },

        "claim_exchanged_asset": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "create a claim object that can be used to redeem the exchange asset",
                "must be invoked by the creator"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/wawaka/exchange/basetypes/escrow_claim_type"
            }
            "PositionalParameters": [],
            "KeywordParameters":  {}
        },

        "claim_offered_asset": {
            "//": "-----------------------------------------------------------------",
            "description": [
                "create a claim object that can be used to redeem the offered asset",
                "must be invoked by the identity that submitted the exchange asset"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/wawaka/exchange/basetypes/escrow_claim_type"
            }
            "PositionalParameters": [],
            "KeywordParameters":  {}
        }
    }
}
```
