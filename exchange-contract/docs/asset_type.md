<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# Asset Type Contract #

The asset type contract provides an identity for asset types that is anchored in the
blockchain. In the current design, there is no particular meaning intrinsically ascribed to the
identity; it simply provides a means to say two things are the same or two things are different.
That being said, this could be extended in the future into a more robust asset class
representation or even use this as a means of certifying issuers of a particular asset class.

## State Update Methods ##

*TBD*

## Immutable Methods ##

*TBD*

## Interface Specification ##

```json
{
    "$schema": "http://json-schema.org/schema#",
    "title": "interface for asset type contract object",
    "id": "http://tradenet.org/pdo/wawaka/exchange/asset_type#",

    "description": [
        "an object that serves as a common reference for assets of a particular type",
        "the object must be initialized by invoking the initialize method"
    ],

    "interface": {
        "initialize": {
            "description": [
                "sets the basic information associated with the asset type",
                "must be invoked by the creator",
                "may only be invoked one time and must be invoked before any other operation"
            ],
            "type": "method",
            "modifies_state": true,
            "returns": "boolean",
            "PositionalParameters": [],
            "KeywordParameters": {
                "description": {
                    "description": "textual description of the asset type"
                    "type": "string",
                    "required": true
                },
                "link": {
                    "description": "URL for further information about the asset type",
                    "type": "string",
                    "required": true
                },
                "name": {
                    "description": "human understandable name of the asset type",
                    "type": "string",
                    "required": true
                }
            }
        },

        "get_asset_type_identifier": {
            "description": [
                "returns the unique identifier for the asset type",
                "the unique identifier is the contract id for the object"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": {
                "$ref": "#/pdo/basetypes/contract-id"
            },
            "PositionalParameters": [],
            "KeywordParameters": {}
        },

        "get_description": {
            "description": [
                "returns the description associated with the asset type"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": "string",
            "PositionalParameters": [],
            "KeywordParameters": {}
        },

        "get_link": {
            "description": [
                "returns the link associated with the asset type"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": "string",
            "PositionalParameters": [],
            "KeywordParameters": {}
        },

        "get_name": {
            "description": [
                "returns the name associated with the asset type"
            ],
            "type": "method",
            "modifies_state": false,
            "returns": "string",
            "PositionalParameters": [],
            "KeywordParameters": {}
        }
    }
}
```
