<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Common Protocol Objects #

## Common Object Specification ##

```json
{
    "$schema": "http://json-schema.org/schema#",
    "title": "Exchange Interface",
    "id": "http://tradenet.org/pdo/wawaka/exchange/basetypes#",

    "definitions": {
        "issuer_authority_type": {
            "id": "#authority_type",
            "description": [
                "attestation of the authority given to an issuer by an organization authorized",
                "to vet issuers of a specific asset type, this may be a vetting organization",
                "or an authorized issuer of the the asset type",
                "the holder of the issuer_signing_key associated with the issuer_verifying_key is",
                "authorized to issue assets of a particular asset type"
            ],
            "type": "object",
            "properties": {
                "authorized_issuer_verifying_key": {
                    "description": [
                        "public key for the issuer"
                    ],
                    "$ref": "#/pdo/basetypes/ecdsa-public-key",
                    "required": true
                },

                "authorizing_issuer_state_reference": {
                    "description": [
                        "state reference for the authorized issuer object",
                        "ensures that the issuer object state is committed on the ledger"
                    ],
                    "$ref": "#/pdo/basetypes/state-reference",
                    "required": true
                },

                "authorizing_signature": {
                    "description": [
                        "signature of the entity that authorizes the use of the verifying key",
                        "signature is computed over the asset type identifier, authorized_issuer_verifying_key,"
                        "and the authorizing_issuer_state_reference"

                    ],
                    "$ref": "#/pdo/basetypes/escda-signature",
                    "required": true
                }
            }
        },

        "issuer_authority_chain_type": {
            "id": "#authority_chain_type",
            "description": [
                "authority chain that captures the authorization chain from a vetting organization",
                "to the verifying key of an asset issuer"
            ],
            "type": "object",
            "properties": {
                "asset_type_identifier": {
                    "description": [
                        "the asset type identifier"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/contract-id"
                    },
                    "required": true
                },

                "vetting_organization_verifying_key": {
                    "description": [
                        "verifying key associated with the vetting organization",
                        "this is the root of trust for issuance"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },

                "authority_chain": {
                    "description": [],
                    "type": "array",
                    "items": {
                        "$ref": "#issuer_authority_type",
                        "minItems" : 1,
                        "uniqueItems": true
                    },
                    "required": true
                }
            }
        },

        "asset_type": {
            "id": "#asset_type",
            "description": [
                ""
            ],
            "type": "object",
            "properties": {
                "asset_type_identifier": {
                    "description": [
                        "the asset type identifier"
                    ],
                    "$ref": "#/pdo/basetypes/contract-id",
                    "required": true
                },

                "count": {
                    "description": "number of assets to be assigned to the new owner",
                    "type": "integer",
                    "required": true
                },

                "owner_identity": {
                    "description": "ECDSA key for the new owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },

                "escrow_agent_identity": {
                    "description": "ECDSA key for the escrow agent",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": false
                },

                "escrow_identifier": {
                    "description": [
                        "unique random identifier for an escrow transaction",
                        "the identifier ensures that stale disburse claims do not apply",
                        "to the current escrow transaction"
                    ],
                    "type": "string",
                    "required": false
                }
            }
        },

        "authoritative_asset_type": {
            "id": "#authoritative_asset_type",
            "description": [
                ""
            ],
            "type": "object",
            "properties": {
                "asset": {
                    "description": "the asset",
                    "type": {
                        "$ref": "#asset_type"
                    },
                    "required": true
                },

                "issuer_state_reference": {
                    "description": [
                        "state reference for the issuer object",
                        "that is, the state of the asset is valid at this state reference"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/state-reference"
                    },
                    "required": true
                },

                "issuer_signature": {
                    "description": [
                        "signature of the issuer that verifies the state of the asset",
                        "signature is computed over the serialized asset and state reference of the issuer,"
                        "and the authorizing_issuer_state_reference"

                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/escda-signature"
                    },
                    "required": true
                },

                "issuer_authority_chain": {
                    "description": [
                        "the authority chain that attests to the the validity of the issuer"
                    ],
                    "type": {
                        "$ref": "#authority_chain_type"
                    },
                    "required": true
                }
            }
        },

        "escrow_release_type": {
            "id": "#escrow_release_type",
            "description": [
                "information necessary to release the escrow on an asset"
            ],
            "type": "object",
            "properties": {
                "count": {
                    "description": "number of assets to be escrowed",
                    "type": "integer",
                    "required": true
                },
                "escrow_agent_state_reference": {
                    "description": [
                        "state reference for the escrow object",
                        "release from escrow is only valid if this state is committed to the ledger"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/state-reference"
                    },
                    "required": true
                },
                "escrow_agent_identity": {
                    "description": "ECDSA key for the new owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },
                "escrow_agent_signature": {
                    "description": [
                        "signature of the escrow that verifies that the asset should be release from escrow",
                        "signature is computed over the serialized asset and state reference of the escrow agent"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/escda-signature"
                    },
                    "required": true
                }
            }

        },

        "escrow_authority_transfer_type": {
            "id": "#escrow_authority_transfer_type",
            "description": [
                "information necessary to establish the authority to transfer",
                "ownership of an escrowed asset"
            ],
            "type": "object",
            "properties": {
                "new_owner_identity": {
                    "description": [
                        "ECDSA key of the new owner or escrow agent",
                        "if unspecified, defaults to the requestor identity"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": false
                },

                "escrow_agent_state_reference": {
                    "description": [
                        "state reference for the escrow object",
                        "release from escrow is only valid if this state is committed to the ledger"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/state-reference"
                    },
                    "required": true
                },

                "count": {
                    "description": [
                        "portion of the escrow that can be claimed",
                        "if unspecified, the count will default to all escrowed assets"
                    ],
                    "type": "integer",
                    "required": false
                }

                "escrow_agent_signature": {
                    "description": [
                        "signature of the escrow that verifies that the asset should be release from escrow",
                        "signature is computed over the serialized asset, state reference of the escrow agent,",
                        "and the invokers identity"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/escda-signature"
                    },
                    "required": true
                }

        "escrow_claim_type": {
            "id": "#escrow_claim_type",
            "description": [
                "information necessary to claim an asset from escrow and change ownership"
            ],
            "type": "object",
            "properties": {
                "count": {
                    "description": "number of assets to be escrowed",
                    "type": "integer",
                    "required": true
                },
                "original_owner_identity": {
                    "description": "ECDSA key for the original owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                },

                "transfer_authority" : {
                    "description": [
                        "list of escrow transfers for the asset"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/escrow_authority_transfer_type"
                    }
            }
        },

        "asset_request_type": {
            "id": "#asset_request_type",
            "description": [
                "request for exchange that specifies type, count or owner that will be accepted",
                "in exchange for the offered asset"
            ],
            "type": "object",
            "properties": {
                "asset_type_identifier": {
                    "description": [
                        "the asset type identifier"
                    ],
                    "$ref": "#/pdo/basetypes/contract-id",
                    "required": true
                },
                "count": {
                    "description": "number of assets to be assigned to the new owner",
                    "type": "integer",
                    "required": true
                },
                "owner_identity": {
                    "description": "ECDSA key for the new owner of the assets",
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": false
                },
                "root_authority_verifying_key": {
                    "description": [
                        "verifying key associated with a vetting organization or issuer",
                        "this is the root of trust for issuance, exchanged assets must be",
                        "authorized by the specified key"
                    ],
                    "type": {
                        "$ref": "#/pdo/basetypes/ecdsa-public-key"
                    },
                    "required": true
                }
            }
        }
    }
}
```
