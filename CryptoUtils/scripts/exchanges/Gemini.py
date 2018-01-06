"""
   See https://docs.gemini.com/rest-api/
"""

import base64
import hashlib
import hmac
import json

from exchanges.AbcExchange import AbcExchange, PROTECTION_PUB, PROTECTION_PRV

BASE_URL = 'https://api.gemini.com'


class Gemini(AbcExchange):

    @property
    def _base_url(self):
        return BASE_URL

    def _build_headers(self, **kwargs):
        payload = base64.b64encode(json.dumps({
            "request": '/v1' + kwargs['url'],
            "nonce": self.nonce
        }).encode()
                                   )
        signature = hmac.new(self.api_secret.encode(), payload, hashlib.sha384).hexdigest()
        return {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': payload,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
        }

    def _build_full_url(self, **kwargs):
        return self._base_url + '/v1' + kwargs['url']

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
