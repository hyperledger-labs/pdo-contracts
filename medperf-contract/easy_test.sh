source ${PDO_SOURCE_ROOT}/build/common-config.sh
source ${PDO_INSTALL_ROOT}'/bin/activate'
make -C ${PDO_CONTRACTS_ROOT}
make -C ${PDO_CONTRACTS_ROOT} install
$PDO_CONTRACTS_ROOT/medperf-contract/test/mp_test.sh --host $PDO_HOSTNAME --ledger $PDO_LEDGER_URL
deactivate
