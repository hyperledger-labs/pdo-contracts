## -----------------------------------------------------------------
class op_dec_value(pcontract.contract_op_base) :
    name = "dec_value"
    help = "Decrement the value of the counter by 1"

    @classmethod
    def invoke(cls, state, session_params, **kwargs) :
        message = invocation_request('dec_value')
        result = pcontract_cmd.send_to_contract(state, message, **session_params)
        return result
