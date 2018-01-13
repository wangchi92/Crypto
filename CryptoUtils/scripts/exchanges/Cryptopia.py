"""
   [Public API] https://www.cryptopia.co.nz/Forum/Thread/255
   [Private API] https://www.cryptopia.co.nz/Forum/Thread/256
"""
import base64
import hashlib
import hmac
import json
import urllib

from exchanges.AbcExchange import AbcExchange, PROTECTION_PUB, PROTECTION_PRV

BASE_URL = 'https://www.cryptopia.co.nz/api'


class Cryptopia(AbcExchange):

    # def __init__(self, api_key, api_secret):
    #       super().__init__(api_key=api_key, api_secret=base64.b64decode(api_secret + '=' * (-len(api_secret) % 4)))

    @property
    def _base_url(self):
        return BASE_URL

    def _build_headers(self, **kwargs):
        post_data = kwargs['post_data']
        m = hashlib.md5()
        m.update(post_data.encode('utf-8'))
        rcb64 = base64.b64encode(m.digest()).decode('UTF-8')
        signature = self.api_key + "POST" + urllib.parse.quote_plus(kwargs['full_url']).lower() + str(
            self.nonce) + rcb64
        sign = base64.b64encode(
            hmac.new(base64.b64decode(self.api_secret), signature.encode('UTF-8'), hashlib.sha256).digest())
        header_value = "amx " + self.api_key + ":" + sign.decode('UTF-8') + ":" + str(self.nonce)
        return {'Authorization': header_value, 'Content-Type': 'application/json; charset=utf-8'}

    def _build_full_url(self, **kwargs):
        return self._base_url + kwargs['url']

    def get_market(self, pair):
        return self._api_query(url='/GetMarket/' + pair)

    def get_balance(self, currency):
        post_data = json.dumps({'Currency': currency})
        return self._api_query(method='POST', url='/GetBalance', post_data=post_data, protection=PROTECTION_PRV)
