from coins.BTC import BTC


def printheader():
    print("")  # newline
    print("BTC price in USD: %d" % BTC.usdprc)
    print("BTC price in SGD: %d" % BTC.sgdprc)
    print("-" * 100)
    print("%5s | %13s | %16s | %13s | %10s | %10s | %10s" % (
        "Name", "Myhash   ", "Diff_Nethash  ", "Coin/Day  ", "CoinPrice ", "mBTC/Day ", "SGD/Day  "))


printheader()
