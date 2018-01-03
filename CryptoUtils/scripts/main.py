#!/usr/bin/env python3

# Note: Please avoid running this script more than once every 10 sec to avoid spamming the servers with API calls.
from __future__ import division  # Python2 mixed float/int operations may return truncated ints, this fixes that

import json
import sys
# Crude hacks for interoperability between Python3 and Python2
import urllib.request as request
from urllib.error import URLError, HTTPError

import hashrates


# request.urlopen returns this if it can't get the proper data
# Effectively a dict that can be accessed using any key to any depth
# And behaves as zero or equivalent otherwise
# Used to allow the rest of the code to run but indicates a zero
class InfZeroDict(dict):
    def __getitem__(self, key):
        return self

    def __mul__(self, key):
        return 0

    def __div__(self, key):
        return sys.maxsize  # largest possible number

    def __float__(self):
        return 0.0

    def __str__(self):
        return '0'


def web2var(url):
    # pulls data from different website APIs in JSON format
    # a Firefox User Agent was used to bypass a 403 Forbidden error.
    # The majority of the program's running time is spent here on waiting for the async callback
    # Currently ignored for simplicity, but eventually may be a concern if more coins are listed here

    try:
        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = request.urlopen(req).read()

        import string  # filter out unprintable chars
        html = ''.join(chr(s) for s in html if chr(s) in string.printable)
        result = json.loads(html)
        return result
    except HTTPError:
        retval = InfZeroDict()
        return retval
    except URLError:
        retval = InfZeroDict()
        return retval


def println(name, hashrate, hashunit, diff, diffunit, coinperday, coinprice, mbtcperday, sgdperday):
    print("%5s | %6.6s %-6.6s | %9.9s %-6.6s | %13.8f | %.8f | %.8f | %.8f" % (
        name, str(hashrate), hashunit, str(diff), str(diffunit), coinperday, coinprice, mbtcperday, sgdperday))
    return


# =====================================Common Data ============================================================

btc_prc = web2var("https://blockchain.info/ticker")
btc_usd = btc_prc["USD"]["15m"]
btc_sgd = btc_prc["SGD"]["15m"]

print("")  # newline
print("BTC price in USD: %d" % btc_usd)
print("BTC price in SGD: %d" % btc_sgd)
print("-" * 100)
print("%5s | %13s | %16s | %13s | %10s | %10s | %10s" % (
    "Name", "Myhash   ", "Diff_Nethash  ", "Coin/Day  ", "CoinPrice ", "mBTC/Day ", "SGD/Day  "))

# =====================================BTG (Bitcoin Gold) ======================================================

# 10 min block time
# digishield diff algo (constantly changing difficulty)

# BTG hashrate given instead of difficulty as difficulty may swing wildly

btgblk = float(web2var("https://btgblocks.com/api/getnetworkhashps"))

btg_price = float(web2var("https://api.hitbtc.com/api/2/public/ticker/BTGBTC")["last"])

# btgblk hashrate given in MSol/s, though expressed in MH/s in the website
btg_per_day = hashrates.EQUIHASH * 1000 / btgblk / 10 * 60 * 24 * 12.5

println("BTG", str(hashrates.EQUIHASH), "kSol/s", str(btgblk / 1000 / 1000), "MSol/s", btg_per_day, btg_price,
        btg_price * btg_per_day * 1000, btg_price * btg_per_day * btc_sgd)

# =====================================ETN (Electroneum) ======================================================

# Removed as there is no publicly available and working network hash rate JSON API

etncom = web2var("https://blockexplorer.electroneum.com/api/networkinfo")

etn_price = web2var("https://www.cryptopia.co.nz/api/GetMarket/ETN_BTC")["Data"]["LastPrice"]

# assumes that reward (block reward + mining fees) is approximately constant
# assumes that network gets 7500 ETN per min
# etn_per_day = my_hashrates.CRYPTONIGHT / int(etncom["data"]["hash_rate"]) * 7500 * 60 * 24

# ETN hashrate given instead of difficulty as difficulty may swing wildly println("ETN",
# str(my_hashrates.CRYPTONIGHT), "H/s", str(etncom["data"]["hash_rate"] / 1000 / 1000), "MH/s", etn_per_day,
# etn_price, etn_price * etn_per_day * 1000, etn_price * etn_per_day * btc_sgd)

# =====================================BTX (Bitcore) ==========================================================

chains = web2var("https://chainz.cryptoid.info/explorer/api.dws?q=summary")

btx_price = web2var("http://www.cryptopia.co.nz/api/GetMarket/BTX_BTC")["Data"]["LastPrice"]

# output per day = diff_constant * hashrate / difficulty
btx_diff_constant = 62.703
btx_per_day = btx_diff_constant * hashrates.TIMETRAVEL / chains["btx"]["diff"]

# BTX difficulty given instead of hashrate as it tends to move in steps
println("BTX", str(hashrates.TIMETRAVEL), "MH/s", str(chains["btx"]["diff"]), "units", btx_per_day, btx_price,
        btx_per_day * btx_price * 1000, btx_per_day * btx_price * btc_sgd)

# ====================================LBC (LBRY Credits) ==================================================

lbryio = web2var("https://explorer.lbry.io/api/v1/status")

lbc_price = web2var("https://bittrex.com/api/v1.1/public/getticker?market=BTC-LBC")["result"]["Last"]

lbc_hashrate = lbryio["status"]["hashrate"].split(" ")[0]
lbc_per_day = hashrates.LBRY / 1000 / float(lbc_hashrate) * 394 / 2.5 * 24 * 60

# LBC hashrate given instead of difficulty as hashrate may swing wildly
println("LBC", str(hashrates.LBRY), "MH/s", lbc_hashrate, "GH/s", lbc_per_day, lbc_price,
        lbc_price * lbc_per_day * 1000, lbc_price * lbc_per_day * btc_sgd)

# ====================================ZEN (Zencash) ========================================================

zen = web2var("https://whattomine.com/coins/185.json")

zen_price = web2var("https://bittrex.com/api/v1.1/public/getticker?market=BTC-ZEN")["result"]["Last"]

zen_per_day = hashrates.EQUIHASH * 1000 / zen["nethash"] * 11 / 2.5 * 60 * 24  # hashrate same as zcash

# ZEN hashrate given instead of difficulty as difficulty may swing wildly
println("ZEN", str(hashrates.EQUIHASH), "kSol/s", str(zen["nethash"] / 1000 / 1000), "GSol/s", zen_per_day,
        zen_price, zen_price * zen_per_day * 1000, zen_price * zen_per_day * btc_sgd)

# ====================================ZEC (Zcash) ==========================================================

zchain = web2var("https://api.zcha.in/v2/mainnet/network")

zec_price = web2var("https://bittrex.com/api/v1.1/public/getticker?market=BTC-ZEC")["result"]["Last"]

zec_per_day = hashrates.EQUIHASH * 1000 / zchain["hashrate"] * 10 / 2.5 * 60 * 24

# ZEC hashrate given instead of difficulty as difficulty may swing wildly
println("ZEC", str(hashrates.EQUIHASH), "kSol/s", str(zchain["hashrate"] / 1000 / 1000), "GSol/s", zec_per_day,
        zec_price, zec_price * zec_per_day * 1000, zec_price * zec_per_day * btc_sgd)

# =====================================ETH (Ethereum) ========================================================

ethchain = web2var("https://etherchain.org/api/miningEstimator")
eth_price = web2var("https://bittrex.com/api/v1.1/public/getticker?market=btc-eth")["result"]["Last"]

eth_diff = int(float(ethchain["difficulty"]))

# assumes that reward (block reward) is constant at 3, ignores mining fees
eth_per_day = 3 * hashrates.ETHASH / eth_diff * 1000 * 1000 * 60 * 60 * 24

# ETH difficulty given instead of hashrate as difficulty moves in steps
println("ETH", str(hashrates.ETHASH), "MH/s", str(eth_diff / 1000 / 1000 / 1000 / 1000), "TH", eth_per_day,
        eth_price, eth_price * eth_per_day * 1000, eth_price * eth_per_day * btc_sgd)

# =====================================XMR (Monero) ========================================================

mb = web2var("http://moneroblocks.info/api/get_stats/")
xmr_price = web2var("https://bittrex.com/api/v1.1/public/getticker?market=BTC-XMR")["result"]["Last"]

# assumes that reward (block reward + mining fees) is approximately constant
xmr_per_day = hashrates.CRYPTONIGHT / float(mb["hashrate"]) * float(mb["last_reward"]) / 1000000000000 / 2 * 60 * 24

# XMR hashrate given instead of difficulty as hashrate may swing wildly
println("XMR", str(hashrates.CRYPTONIGHT), "H/s", str(mb["hashrate"] / 1000 / 1000), "MH/s", xmr_per_day, xmr_price,
        xmr_price * xmr_per_day * 1000, xmr_price * xmr_per_day * btc_sgd)

# =====================================SC (Siacoin) ========================================================

siamine = web2var("https://siamining.com/api/v1/network")
sc_price = web2var("https://bittrex.com/api/v1.1/public/getticker?market=btc-sc")["result"]["Last"]

# assumes that reward (block reward + mining fees) is approximately constant
sc_per_day = siamine["block_reward"] / int(siamine["difficulty"]) * hashrates.BLAKE2B * 1000 * 1000 * 60 * 60 * 24

# SC difficulty given instead of hashrate as difficulty moves in steps
println("SC", str(hashrates.BLAKE2B), "MH/s", str(int(siamine["difficulty"]) / 1000 / 1000 / 1000 / 1000), "TH",
        sc_per_day, sc_price, sc_price * sc_per_day * 1000, sc_price * sc_per_day * btc_sgd)
