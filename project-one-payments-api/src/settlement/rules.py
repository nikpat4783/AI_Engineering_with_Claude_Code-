def settlement_window(region):
    if region == "IN":
        return "T+1"
    if region == "AE":
        return "T+1"
    return "T+2"