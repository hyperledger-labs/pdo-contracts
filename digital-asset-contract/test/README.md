<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->
# Digital Asset Test Scripts

This directory contains a number of pdo-shell scripts to test the
digital asset contract family. The scripts assume that a complete
installation of the PDO client is complete.

## Test Scripts

Test scripts take several parameters that can override the standard
PDO environment variables:

* `--host` <hostname> : Specify the host where the PDO services operate, override `PDO_HOSTNAME`
* `--ledger` <url> : Specify the URL for the PDO ledger, override `PDO_LEDGER_URL`
* `--loglevel` <level> : Specify logging verbosity
* `--logfile` <file> : Specify the logging output file

### `run_tests.sh`

This script sets up and runs the functional test suite for the digital asset
contract family. The actual tests will be found in the pdo-shell script
`functional_test.psh`

### `script_test.sh`

This script tests the `bash` entry points for digital asset plugins.

### `functional_test.psh`

This script provides a functional test of the various contract
types in the digital asset contract family. In general, this should
not be invoked directly but should be called through `run-tests.sh`.
