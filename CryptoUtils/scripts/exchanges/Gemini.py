import base64
import hashlib
import hmac
import json
import time

import requests


def build_headers(api_key, payload, signature):
    return {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': api_key,
        'X-GEMINI-PAYLOAD': payload,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }


def using_requests(method, url, headers):
    return requests.request(method, url, headers=headers).json()


class Gemini(object):

    def __init__(self, api_key, api_secret, dispatch=using_requests):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.dispatch = dispatch
        self.last_call = None
        self.total_balance_in_btc = -1
        self.nonce = int(time.time() * 1000)

        self.balances = None

    def _api_query(self, method, url, protection='private'):
        url = '/v1' + url
        b64 = base64.b64encode(json.dumps({
            "request": url,
            "nonce": self.nonce
        }).encode('utf-8')
                               )
        ++(self.nonce)

        headers = None
        if protection is 'private':
            signature = hmac.new(self.api_secret.encode(), b64, hashlib.sha384).hexdigest()
            headers = build_headers(self.api_key, b64, signature)
        return self.dispatch(method, 'https://api.gemini.com' + url, headers)

    def get_ticker(self, currency):
        url = '/pubticker/' + currency + 'usd'
        return self._api_query("GET", url, protection='public')

    def get_price(self, currency):
        ticker = self.get_ticker(currency)
        return ticker["last"]

    def get_balances(self):
        if self.balances is None:
            url = "/balances"
            self.balances = self._api_query("POST", url, protection='private')
        return self.balances

    def get_balance(self, currency):
        for balance in self.get_balances():
            if currency in balance['currency']:
                return balance['amount']

    def get_total_balance_in_usd(self):
        total = 0
        for balance in self.get_balances():
            if 'USD' not in balance['currency']:
                price = self.get_price(balance['currency'])
                total += float(price) * float(balance['amount'])
            else:
                total += float(balance['amount'])
        return total
