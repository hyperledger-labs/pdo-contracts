<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# PDO Contracts for tokenization and policy based access of Hugging Face models #

This directory contains a Private Data Objects contract family for
creating a confidentiality preserving policy-wrapper around the usage
of (possibly private) machine learning (ML) models hosted on Hugging Face.
(`https://huggingface.co/models`). 


## Problem Statement and Solution Overview
The majority of models shared via Hugging Face today are open-source. 
For models that are private, or whose access need to be controlled, Hugging Face 
provides the following options: 

1. The model repository and its deployment could be kept entirely private 
(`https://huggingface.co/docs/hub/en/repositories-getting-started#creating-a-repository`)
in which case only the model owner (personal model) or members of the organization 
(organization model) can see and access the deployment. 

2. `Gated Models` (`https://huggingface.co/docs/hub/models-gated`). Under gated models, prospective
users must provide basic information about themselves, and in addition should provide additional 
information set by the model owner. Once approved by the model owner, the approved user gets access
to the model including the repository. 

However the above currently available solutions do not permit a model owner to set fine-grained polices
for access control of models; whose raw-bytes must otherwise be kept confidential. In this PoC, we provide
a solution for how policy-controlled access to "private" models hosted on Hugging Face can be provided 
to any third-party whose use-case suffices to the use the model under the terms of the policy. At a high-level, 
the solution works as follows:

1. The model owner deploys the model as a private/gated model on Hugging Face. It is assumed that the model is available
for inference via Serverless API (`https://huggingface.co/docs/api-inference/index`) given the model owner's authentication tokens. (We haven't evaluated the PoC for Hugging Face managed inference endpoints (`https://huggingface.co/docs/inference-endpoints/index`) )

2. The model owner deploys PDO Token Object smart contract that encodes policies for usage of the model via Serverless Inference APIs. Currently, the PoC builds a generic token object which can be configured with the following information a. model owner authentication token b. REST API URL. Both of these are considered confidential information, and never exposed outside the PDO contract. The rest of the information is available for a prospective user of the asset c. Fixed Model parameters d. User input schema e. model/usage description f. max use count, referring to the maximum number of times model use capability packages can be obtained from the token object. 

3. The model owner transfers ownership of the PDO token object to a new user. New user submits model use requests to the token 
object, obtains capability packages, and submits to the guardian web-server that acts as a bridge between the PDO token object, and the Hugging Face serverless API endpoint. Like the token object, the guardian web-server is generic. 
We have programmed the guardian to check the schema of the user inputs against the schema set by the model owner as part of the the token object params; otherwise the guardian functionality is model agnostic. One limitation of this approach is that
if privacy preserving input pre-processing or output postprocessing needs to be carried out (which might be natural to expect
given that the problem assumes the model itself is private), the current PoC needs additional enhancements.

4. The guardian invokes the REST API call to the serverless inference endpoint, obtains the result and returns back to the token owner. We have tested the PoC using some of the examples provided at `https://huggingface.co/docs/api-inference/detailed_parameters`. 

## Additional Details about the Solution

At its core, the solution leverages the token-guardian protocol and its implementation contained within the [Exchange Contracts](../exchange-contract/README.md) family for policy-based use of high-value, possibly confidential assets. The current PoC does not employ TEEs for the guardian, however; for a more secure PoC, the token-guardian protocol permits usage of TEEs for the guardian web-server, and bi-directional attestation between the PDO token object and the guardian server. 

Additionally, this PoC conceptually is similar to the [inference-contract](../inference-contract/README.md) PoC, where we showed how to create PDO token objects/guardians for policy-based usage of high-value ML model deployed for inferencing via the OpenVINO model server. The major difference is that OpenVINO currently does not provide a hosted inferencing solution; so it is up to the model owner to deploy the OpenVINO model server that hosts the model; and also prove that the hosted solution respects usage of the inferencing data. In the current Hugging Face use-case, the model owner does not manage the inferncing infrastrture; rather simply relies on solutions provided by HuggingFace. A detailed comparison of privacy-preserving properties of the two PoCs for both the model owner; and the inferencing user is doable based on interest from the community.


## Testing the PoC

The [test script](./test/script_test.sh) uses the open source `https://api-inference.huggingface.co/models/openai-community/gpt2` model available on Hugging Face via serverless APIs. In order to run the test script, please obtain a user access token 
`https://huggingface.co/settings/tokens` that is necessary to make REST API calls to serverless API endpoints. Set the environment variable `HF_AUTH_TOKEN` with the token value. For the test, the assumption is that person who executes the test script owns the model; the token object will be configured with the person's token. The test will transfer token ownership to a fictitious `token_holder` and let the token_holder use the model subject to policies in the token object.

We note that the test has not been integrated with the automated test suite for the contracts repo due to the dependency on the HF access token to run the test for this PoC.

