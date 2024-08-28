## Workflow

```mermaid
sequenceDiagram 
    participant E as Experiment Committee
    participant PDO as PDO Contract (SGX)
    participant G as Digital Guardian Service
    participant D as Data Owner 
    participant M as MedPerf Server
    %% participant MO as Model Owner
    note over G, M: experiment-data association (assume finished)
    note over G, M: model-data association (assume finished)
    note over M, PDO: assume the states data are synchronized
    loop Attestation
      PDO -> G: 
    end
    D ->> PDO: create token_issuer and call cmd_mint_token
    PDO ->> PDO: generate new identity token_issuer and new contract token.token_object
    D ->> PDO: transfer token.token_object to new owner token_experitment1
    PDO ->> PDO: generate new identity token_expertiment1 and new contract token.token_experiment1
    note over E, PDO: owership transferred to Experiment committee
    note over M: notification about token/dataset availiability
    box Assume Trusted
      participant M
    end
    box SGX Enclave
      participant G
    end
    E ->> PDO: request the inference on specific model model_id, experiment_id (cmd_use_dataset)
    activate PDO
    PDO ->> PDO: policy evaluation
    note right of PDO: policy: <br> experiment_id = experiment_id' <br> model_id in {model_id}
    PDO ->> E: return capabilities, encoded with urls for dockerfile and weights of the granted model.identity of 
    deactivate PDO
    E ->> G: request access to service with capability (storage )
    E ->> D: 
    activate G
    note over G: pull/download/deploy mlcube (the model) 
    G ->> G: run inference over the dataset
    G ->> D: return result (basic verification with hash)
    D ->> E: return results
    deactivate G
```


## Protocols

From the dataset owner side:
+ The dataset is identified by its hash.
+ Tokens are minted based on hash-based binding.
+ Guardian service of the token exposes an api to the callers 


## Core functions 

+ Allow data owner to tokenize a dataset (into a PDO contract)
  + with default policy checking the registration information from MedPerf
  + ownership transfer to experiment committee
  + generate capability to grant access to the guardian service

+ Allow experiment committee to initilize the use of data by interacting with PDO
  + capabilities are published on MedPerf server (or PDO states/ledger?) for downloading

+ Allow data owner to host a guardian service, which exposes interface (local) to initilize the test
  + data owner downloads the capability from the server (or ledger)
  + data owner feeds the capability to guardian service to initialize the experiment
  + guardian service publish experiment results to the server (or ledger)
    + allows access control?



### Guardian service 

Datasets are hosted behind the service.
<!-- The service can be called from the  -->
<!-- + called from the model owner -- one model inference over the dataset -->
<!-- + called from the experiment committee (TBA) -->

The guardian service is co-located with the dataset. guadian service provides a wsgi api to process the capability. Capability encodes `{model_id, dataset_id, url_to_docker, url_to_weights}`. After receiving capability, the guardian service:
1. pull/build docker images from `url_to_docker`
2. download weights from `url_to_weights`
3. model up and run over `dataset_id` 

no execution integrity for now.
<!-- dataset encryption -->



### Contract methods

new contract methods under the class `ww::medperf::token_object`

`initialize`: public methode, mint token for the dataset, actual method behind `cmd_mint_token`
  1. kvs of the experiment/model/dataset info
  2. Store the registered metadata from medperf service (synthetic for PoC).
  3. set a `max_evaluation`
 
| Keys | Values |
| ---- | ---- |
| experiment_id | identifier for the experimetn |
| model_id | identifier for the model |
| {urls} | url to model assets |
| dataset_id | hash of the dataset |
| max_evaluation | most models that allowed to evaluate  |
| cur_evaluation | 0 |
| approved_capability| {} |
| TBA |

`get_datasetinfo`: public method, get the non-secret kvs info of dataset token
return the information associated with the dataset.

capability -links to- identity // invoked by the dataowner only

<!-- `get_capability`:
  1. called by model owner -->

`use_dataset(model_id, dataset_id, experiment_id)`: only invoked by TO
  1. check if model_id, dataset_id, experiment_id are in the kv storage
  2. cur_evaluation + 1, if cur_evaluation = max_evaluation, fail
  3. invoke `get_capability` and return secretly encoded {urls}.

allows multiple models in one call

`get_capability`: only invoked by TO, parse capability kv