from abc import *
import requests
import time

try:
    from Crypto.Cipher import AES
except ImportError:
    encrypted = False
else:
    import getpass
    import ast
    import json

    encrypted = True


def encrypt(api_key, api_secret, export=True, export_fn='secrets.json'):
    cipher = AES.new(getpass.getpass(
        'Input encryption password (string will not show)'))
    api_key_n = cipher.encrypt(api_key)
    api_secret_n = cipher.encrypt(api_secret)
    api = {'key': str(api_key_n), 'secret': str(api_secret_n)}
    if export:
        with open(export_fn, 'w') as outfile:
            json.dump(api, outfile)
    return api


PROTECTION_PUB = 'pub'  # public methods
PROTECTION_PRV = 'prv'  # authenticated methods


class AbcExchange(object):

    def __init__(self, api_key, api_secret, calls_per_second=1):
        self.call_rate = 1.0 / calls_per_second
        self.last_call = None

        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.nonce = int(time.time() * 1000)
        self.balances = None
        self.total_balance_in_btc = -1

    @property
    @abstractmethod
    def _base_url(self):
        pass

    @staticmethod
    def _dispatch(method, request_url, headers):
        return requests.request(
            method,
            request_url,
            headers=headers
        ).json()

    @abstractmethod
    def _build_headers(self):
        pass

    @abstractmethod
    def _build_full_url(self):
        pass

    def _api_query(self, method="GET", url='', options=None, protection=PROTECTION_PUB):
        ++(self.nonce)
        full_url = self._build_full_url(url=url, options=options, protection=protection)
        headers = None
        if protection is not PROTECTION_PUB:
            headers = self._build_headers(url=url, full_url=full_url)
        self.wait()
        try:
            return self._dispatch(method, full_url, headers)
        except Exception:
            return {
                'success': False,
                'message': 'NO_API_RESPONSE',
                'result': None
            }

    def decrypt(self):
        if encrypted:
            cipher = AES.new(getpass.getpass(
                'Input decryption password (string will not show)'))
            try:
                if isinstance(self.api_key, str):
                    self.api_key = ast.literal_eval(self.api_key)
                if isinstance(self.api_secret, str):
                    self.api_secret = ast.literal_eval(self.api_secret)
            except Exception:
                pass
            self.api_key = cipher.decrypt(self.api_key).decode()
            self.api_secret = cipher.decrypt(self.api_secret).decode()
        else:
            raise ImportError('"pycrypto" module has to be installed')

    def wait(self):
        if self.last_call is None:
            self.last_call = time.time()
        else:
            now = time.time()
            passed = now - self.last_call
            if passed < self.call_rate:
                # print("sleep")
                time.sleep(self.call_rate - passed)

            self.last_call = time.time()
