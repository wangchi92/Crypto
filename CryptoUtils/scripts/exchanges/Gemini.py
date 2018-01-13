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

    def _request_get_ticker(self, currency, denom):
        url = '/pubticker/' + currency.upper() + denom.upper()
        return self._api_query("GET", url, protection='public')

    def get_price(self, currency, denom):
        result = self._request_get_ticker(currency, denom)
        return float(result['last'])

    def _request_get_balances(self):
        url = "/balances"
        return self._api_query("POST", url, protection='private')

    def get_balances(self):
        if self.balances is None:
            self.balances = dict()
            for balance in self._request_get_balances():
                self.balances[balance['currency'].lower()] = float(balance['amount'])
        return self.balances

    def get_balance(self, currency):
        return self.get_balances['currency'.lower()]

    def get_total_balance_in_btc(self, verbose=False):
        total = 0.0
        for currency, balance in self.get_balances().items():
            if 'btc' in currency:
                total += float(balance)
            elif 'eth' in balance:
                price = self.get_price(currency, 'btc')
                total += float(price) * float(balance)
        return total

    def get_total_balance_in_usd(self):
        total = 0
        for currency, balance in self.get_balances().items():
            if 'USD' not in currency:
                price = self.get_price(currency)
                total += float(price) * float(balance)
            else:
                total += float(balance)
        return total