import json

from exchanges.Bittrex import Bittrex
from exchanges.Cryptopia import Cryptopia
from exchanges.Gemini import Gemini


def getSecret(exchange=None):
    if (exchange == None):
        return None
    else:
        with open("secrets.json") as secrets_file:
            secrets = json.load(secrets_file)
            secrets_file.close()
            return secrets[exchange]


# secret = getSecret('gemini')
# gemini = Gemini(secret['key'], secret['secret'])
#
# gemini.print_header()
#
# gemini_total = gemini.get_total_balance_in_btc()
# print('Gemini total = ' + str(gemini_total) + " BTC")
#
# secret = getSecret('bittrex')
# bittrex = Bittrex(secret['key'], secret['secret'])
# bittrex_total = bittrex.get_total_balance_in_btc()
# print('Bittrex total = ' + str(bittrex_total) + ' BTC')
#
# secret = getSecret('cryptopia')
# cryptopia = Cryptopia(secret['key'], secret['secret'])
# cryptopia_total = cryptopia.get_balance('BTC')['Data'][0]['Total']
# print('Cryptopia total = ' + str(cryptopia_total) + ' BTC')
#
# total = gemini_total + bittrex_total + cryptopia_total
# print("Total in BTC = " + str(total))
# print("Total in USD = $" + str(float(total)*float(BTC_price)))
# print("Total in SGD = $" + str(float(total)*float(BTC_price)*1.33))


class Portfolio(object):

    def __init__(self, secrets_json="secrets.json"):
        self._secrets = self._get_secret(secrets_json)
        self._exchanges = self._init_exchanges()
        self._btc_price = self._exchanges['Gemini'].get_price('btc', 'usd')
        self._balances = self._update_balances()
        self._total_btc_value, self._total_usd_value = self.update_btc_value()

    def _get_secret(self, secrets):
        with open(secrets) as secrets_file:
            secrets = json.load(secrets_file)
            secrets_file.close()
            return secrets

    def _init_exchanges(self):
        gemini = Gemini(self._secrets['gemini']['key'], self._secrets['gemini']['secret'])
        bittrex = Bittrex(self._secrets['bittrex']['key'], self._secrets['bittrex']['secret'])
        cryptopia = Cryptopia(self._secrets['cryptopia']['key'], self._secrets['cryptopia']['secret'])
        return {'Gemini': gemini, 'Bittrex': bittrex}

    def _update_balances(self):
        balances = dict()
        for k, exchange in self._exchanges.items():
            exchange_balances = exchange.get_balances()
            for currency, balance in exchange_balances.items():
                if currency in balances:
                    balances[currency]['amount'] += balance
                else:
                    balances[currency] = dict()
                    balances[currency]['amount'] = balance
        for currency in balances:
            if 'btc' in currency.lower():
                balances[currency]['btc_value'] = balances[currency]['amount']
                balances[currency]['btc_price'] = 1.0
                balances[currency]['usd_value'] = balances[currency]['amount'] * self._btc_price
            elif 'usd' in currency.lower():
                balances[currency]['btc_value'] = 0
                balances[currency]['btc_price'] = 0
                balances[currency]['usd_value'] = balances[currency]['amount']
            else:
                balances[currency]['btc_price'] = self._exchanges['Bittrex'].get_price(currency, 'btc')
                btc_value = balances[currency]['amount'] * balances[currency]['btc_price']
                balances[currency]['btc_value'] = btc_value
                balances[currency]['usd_value'] = btc_value * self._btc_price
        return balances

    def update_btc_value(self):
        btc_sum = 0.0
        usd_sum = 0.0
        for currency in self._balances:
            usd_sum += self._balances[currency]['usd_value']
            if 'usd' not in currency.lower():
                btc_sum += self._balances[currency]['btc_value']
        return btc_sum, usd_sum

    def update_usd_value(self):
        btc_sum = 0.0
        for currency in self._balances:
            btc_sum += self._balances[currency]['usd_value']
        return btc_sum

    def print_balances_raw(self):
        print(self._balances)

    def print_balances(self):
        self._print_header()
        for currency in self._balances:
            self.print_coin(currency, self._balances[currency]['amount'], self._balances[currency]['btc_price'],
                            self._balances[currency]['btc_value'], self._balances[currency]['usd_value'])
        print('')
        self._print_total()

    def _print_header(self):
        btc_price = self._exchanges['Gemini'].get_price('BTC', 'USD')
        print('1 BTC = USD $' + str(btc_price))
        print('')
        print("|{:^10}|{:^20}|{:^20}|{:^20}|{:^20}|{:^20}|".format("Currency", "Units", "Price(BTC)",
                                                                   "Price(USD)", "Total(BTC)", "Total(USD)"))

    def _print_total(self):
        print(
            " {:^10} {:^20} {:^20} {:^20}|{:^20}|{:^20}|".format('', '',
                                                                 '',
                                                                 'Total',
                                                                 "{:.4f}".format(self._total_btc_value),
                                                                 "{:.4f}".format(self._total_usd_value)))

    def print_coin(self, coin, amount, price_btc, btc_value, usd_value):
        print("|{:^10}|{:^20}|{:^20}|{:^20}|{:^20}|{:^20}|".format(str(coin.upper()), "{:.4f}".format(amount),
                                                                   "{:.6f}".format(price_btc),
                                                                   "{:.4f}".format(price_btc * self._btc_price),
                                                                   "{:.4f}".format(btc_value),
                                                                   "{:.4f}".format(usd_value)))


folio = Portfolio()
folio.print_balances()
