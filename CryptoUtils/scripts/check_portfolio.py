import json

from exchanges.Bittrex import Bittrex
from exchanges.Gemini import Gemini


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
print('Bittrex total = ' + str(bittrex_total) + ' USD')

secret = getSecret('gemini')
gemini = Gemini(secret['key'], secret['secret'])
gemini_total = gemini.get_total_balance_in_usd()
print('Gemini total = ' + str(gemini_total) + " USD")

print('Grand total = ' + str(bittrex_total + gemini_total) + 'USD')
