<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->

# PDO-enhanced MedPerf Workflow
This document includes an enhanced workflow for Federated Evaluation (FE) in machine learning, aiming in providing a policy-enforced digital asset usage framwork with tokenization. The framework is built upon the FE workflow from [MedPerf](https://github.com/mlcommons/medperf).

## Note

The initial version of this project only covers the protection of dataset. Other digital assets, including the model (weights)and experiment results are not included for now.


## Test with the MedPerf tutorial 
The existing test simulates the pdo-enhanced workflow by running both components simultaneously. The pdo command hacks into the medperf database directly to simulate the information updates. 

Set up PDO test environment and have the [MedPerf](https://github.com/mlcommons/medperf) installed and built. Then set up environment variables `MEDPERF_SQLITE_PATH`, `MEDPERF_VENV_PATH` and `MEDPERF_HOME`.

Simply run [easy_test.sh](./easy_test.sh) to start the test.




<!-- ```c++
ww::medperf::token_object::initilization()
ww::medperf::token_object::use_dataset()
ww::medperf::token_object::get
``` -->


## Testing workflow
+ create token issuer and mint the token for the dataset.
+ token issuer transfers token to model_owner1
+ model_owner1 invoke `cmd_use_dataset` with specific `model_id` and `dataset_id`
  + get capability for one model, increase the count
  + call service to run inference
+ model_owner1 invoke `cmd_use_dataset` with specific `model_id` and `dataset_id`
  + max_evaluation exceeds, fail

For detailed description of the whole protocol, check [here](./PROTOCOL.md).