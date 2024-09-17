
// -----------------------------------------------------------------
// NAME: dec_value
// -----------------------------------------------------------------
bool ww::myfirst_contract::counter::dec_value(const Message& msg, const Environment& env, Response& rsp)
{
    //
    ASSERT_SENDER_IS_CREATOR(env, rsp);

    // get the current value of the counter from the contract state
    uint32_t value;
    if (! value_store.get(counter_key, value))
        return rsp.error("no such key");

    // decrement the value
    value -= 1;

    // store the new value in the contract state
    if (! value_store.set(counter_key, value))
        return rsp.error("failed to save the new value");

    // and return the new value
    ww::value::Number v((double)value);
    return rsp.value(v, true);
}
