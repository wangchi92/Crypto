import json

from exchanges.Bittrex import Bittrex


def getSecret(exchange=None):
    if (exchange == None):
        return None
    else:
        with open("secrets.json") as secrets_file:
            secrets = json.load(secrets_file)
            secrets_file.close()
            return secrets[exchange]


secret = getSecret('bittrex')
bittrex = Bittrex(secret['key'], secret['secret'])
bittrex_total = bittrex.get_total_balance_in_usd()
