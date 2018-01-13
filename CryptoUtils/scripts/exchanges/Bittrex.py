"""
   See https://bittrex.com/Home/Api
"""

from exchanges.AbcExchange import AbcExchange, PROTECTION_PUB, PROTECTION_PRV

import hashlib
import hmac

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

TICKINTERVAL_ONEMIN = 'oneMin'
TICKINTERVAL_FIVEMIN = 'fiveMin'
TICKINTERVAL_HOUR = 'hour'
TICKINTERVAL_THIRTYMIN = 'thirtyMin'
TICKINTERVAL_DAY = 'Day'

ORDERTYPE_LIMIT = 'LIMIT'
ORDERTYPE_MARKET = 'MARKET'

TIMEINEFFECT_GOOD_TIL_CANCELLED = 'GOOD_TIL_CANCELLED'
TIMEINEFFECT_IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL'
TIMEINEFFECT_FILL_OR_KILL = 'FILL_OR_KILL'

CONDITIONTYPE_NONE = 'NONE'
CONDITIONTYPE_GREATER_THAN = 'GREATER_THAN'
CONDITIONTYPE_LESS_THAN = 'LESS_THAN'
CONDITIONTYPE_STOP_LOSS_FIXED = 'STOP_LOSS_FIXED'
CONDITIONTYPE_STOP_LOSS_PERCENTAGE = 'STOP_LOSS_PERCENTAGE'

API_V1_1 = 'v1.1'

BASE_URL_V1_1 = 'https://bittrex.com/api/v1.1{path}?'


# BASE_URL_V2_0 = 'https://bittrex.com/api/v2.0{path}?'

class Bittrex(AbcExchange):
    """
    Used for requesting Bittrex with API key and API secret
    """

    def __init__(self, api_key, api_secret, api_version=API_V1_1):
        super().__init__(api_key, api_secret)
        self.api_version = api_version

    @property
    def _base_url(self):
        return BASE_URL_V1_1

    def _build_full_url(self, **kwargs):
        request_url = self._base_url
        request_url = request_url.format(path=kwargs['url'])

        if kwargs['protection'] != PROTECTION_PUB:
            request_url = "{0}apikey={1}&nonce={2}&".format(request_url, self.api_key, self.nonce)

        if not kwargs['options']:
            options = {}
        else:
            options = kwargs['options']
        request_url += urlencode(options)

        return request_url

    def _build_headers(self, **kwargs):
        apisign = hmac.new(self.api_secret.encode(),
                           kwargs['full_url'].encode(),
                               hashlib.sha512).hexdigest()

        return {"apisign": apisign}

    def get_markets(self):
        """
        Used to get the open and available trading markets
        at Bittrex along with other meta data.
        1.1 Endpoint: /public/getmarkets
        2.0 NO Equivalent
        Example ::
            {'success': True,
             'message': '',
             'result': [ {'MarketCurrency': 'LTC',
                          'BaseCurrency': 'BTC',
                          'MarketCurrencyLong': 'Litecoin',
                          'BaseCurrencyLong': 'Bitcoin',
                          'MinTradeSize': 1e-08,
                          'MarketName': 'BTC-LTC',
                          'IsActive': True,
                          'Created': '2014-02-13T00:00:00',
                          'Notice': None,
                          'IsSponsored': None,
                          'LogoUrl': 'https://i.imgur.com/R29q3dD.png'},
                          ...
                        ]
            }
        :return: Available market info in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarkets',
        }, protection=PROTECTION_PUB)

    def get_currencies(self):
        """
        Used to get all supported currencies at Bittrex
        along with other meta data.
        Endpoint:
        1.1 /public/getcurrencies
        2.0 /pub/Currencies/GetCurrencies
        :return: Supported currencies info in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/public/getcurrencies',
            #API_V2_0: '/pub/Currencies/GetCurrencies'
        }, protection=PROTECTION_PUB)

    def get_ticker(self, market):
        """
        Used to get the current tick values for a market.
        Endpoints:
        1.1 /public/getticker
        2.0 NO EQUIVALENT -- but get_latest_candle gives comparable data
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :return: Current values for given market in JSON
        :rtype : dict
        """
        return self._api_query(url='/public/getticker',
                               options={'market': market}, protection=PROTECTION_PUB)

    def get_market_summaries(self):
        """
        Used to get the last 24 hour summary of all active exchanges
        Endpoint:
        1.1 /public/getmarketsummaries
        2.0 /pub/Markets/GetMarketSummaries
        :return: Summaries of active exchanges in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarketsummaries',
            #API_V2_0: '/pub/Markets/GetMarketSummaries'
        }, protection=PROTECTION_PUB)

    def get_marketsummary(self, market):
        """
        Used to get the last 24 hour summary of all active
        exchanges in specific coin
        Endpoint:
        1.1 /public/getmarketsummary
        2.0 /pub/Market/GetMarketSummary
        :param market: String literal for the market(ex: BTC-XRP)
        :type market: str
        :return: Summaries of active exchanges of a coin in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarketsummary',
            #API_V2_0: '/pub/Market/GetMarketSummary'
        }, options={'market': market, 'marketname': market}, protection=PROTECTION_PUB)

    def get_orderbook(self, market, depth_type=BOTH_ORDERBOOK):
        """
        Used to get retrieve the orderbook for a given market.
        The depth_type parameter is IGNORED under v2.0 and both orderbooks are always returned
        Endpoint:
        1.1 /public/getorderbook
        2.0 /pub/Market/GetMarketOrderBook
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param depth_type: buy, sell or both to identify the type of
            orderbook to return.
            Use constants BUY_ORDERBOOK, SELL_ORDERBOOK, BOTH_ORDERBOOK
        :type depth_type: str
        :return: Orderbook of market in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/public/getorderbook',
            #API_V2_0: '/pub/Market/GetMarketOrderBook'
        }, options={'market': market, 'marketname': market, 'type': depth_type}, protection=PROTECTION_PUB)

    def get_market_history(self, market):
        """
        Used to retrieve the latest trades that have occurred for a
        specific market.
        Endpoint:
        1.1 /market/getmarkethistory
        2.0 NO Equivalent
        Example ::
            {'success': True,
            'message': '',
            'result': [ {'Id': 5625015,
                         'TimeStamp': '2017-08-31T01:29:50.427',
                         'Quantity': 7.31008193,
                         'Price': 0.00177639,
                         'Total': 0.01298555,
                         'FillType': 'FILL',
                         'OrderType': 'BUY'},
                         ...
                       ]
            }
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :return: Market history in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/public/getmarkethistory',
        }, options={'market': market, 'marketname': market}, protection=PROTECTION_PUB)

    def buy_limit(self, market, quantity, rate):
        """
        Used to place a buy order in a specific market. Use buylimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work
        Endpoint:
        1.1 /market/buylimit
        2.0 NO Direct equivalent.  Use trade_buy for LIMIT and MARKET buys
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param quantity: The amount to purchase
        :type quantity: float
        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float
        :return:
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/market/buylimit',
        }, options={'market': market,
                    'quantity': quantity,
                    'rate': rate}, protection=PROTECTION_PRV)

    def sell_limit(self, market, quantity, rate):
        """
        Used to place a sell order in a specific market. Use selllimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work
        Endpoint:
        1.1 /market/selllimit
        2.0 NO Direct equivalent.  Use trade_sell for LIMIT and MARKET sells
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param quantity: The amount to purchase
        :type quantity: float
        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float
        :return:
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/market/selllimit',
        }, options={'market': market,
                    'quantity': quantity,
                    'rate': rate}, protection=PROTECTION_PRV)

    def cancel(self, uuid):
        """
        Used to cancel a buy or sell order
        Endpoint:
        1.1 /market/cancel
        2.0 /key/market/tradecancel
        :param uuid: uuid of buy or sell order
        :type uuid: str
        :return:
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/market/cancel',
            #API_V2_0: '/key/market/tradecancel'
        }, options={'uuid': uuid, 'orderid': uuid}, protection=PROTECTION_PRV)

    def get_open_orders(self, market=None):
        """
        Get all orders that you currently have opened.
        A specific market can be requested.
        Endpoint:
        1.1 /market/getopenorders
        2.0 /key/market/getopenorders
        :param market: String literal for the market (ie. BTC-LTC)
        :type market: str
        :return: Open orders info in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/market/getopenorders',
            #API_V2_0: '/key/market/getopenorders'
        }, options={'market': market, 'marketname': market} if market else None, protection=PROTECTION_PRV)

    def _request_get_balances(self):
        """
        Used to retrieve all balances from your account.
        Endpoint:
        1.1 /account/getbalances
        2.0 /key/balance/getbalances
        Example ::
            {'success': True,
             'message': '',
             'result': [ {'Currency': '1ST',
                          'Balance': 10.0,
                          'Available': 10.0,
                          'Pending': 0.0,
                          'CryptoAddress': None},
                          ...
                        ]
            }
        :return: Balances info in JSON
        :rtype : dict
        """
        return self._api_query(url='/account/getbalances', protection=PROTECTION_PRV)

    def get_balance(self, currency):
        """
        Used to retrieve the balance from your account for a specific currency
        Endpoint:
        1.1 /account/getbalance
        2.0 /key/balance/getbalance
        Example ::
            {'success': True,
             'message': '',
             'result': {'Currency': '1ST',
                        'Balance': 10.0,
                        'Available': 10.0,
                        'Pending': 0.0,
                        'CryptoAddress': None}
            }
        :param currency: String literal for the currency (ex: LTC)
        :type currency: str
        :return: Balance info in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/account/getbalance',
            #API_V2_0: '/key/balance/getbalance'
        }, options={'currency': currency, 'currencyname': currency}, protection=PROTECTION_PRV)

    def get_deposit_address(self, currency):
        """
        Used to generate or retrieve an address for a specific currency
        Endpoint:
        1.1 /account/getdepositaddress
        2.0 /key/balance/getdepositaddress
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: Address info in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/account/getdepositaddress',
            #API_V2_0: '/key/balance/getdepositaddress'
        }, options={'currency': currency, 'currencyname': currency}, protection=PROTECTION_PRV)

    def withdraw(self, currency, quantity, address):
        """
        Used to withdraw funds from your account
        Endpoint:
        1.1 /account/withdraw
        2.0 /key/balance/withdrawcurrency
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :param quantity: The quantity of coins to withdraw
        :type quantity: float
        :param address: The address where to send the funds.
        :type address: str
        :return:
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/account/withdraw',
            #API_V2_0: '/key/balance/withdrawcurrency'
        }, options={'currency': currency, 'quantity': quantity, 'address': address}, protection=PROTECTION_PRV)

    def get_order_history(self, market=None):
        """
        Used to retrieve order trade history of account
        Endpoint:
        1.1 /account/getorderhistory
        2.0 /key/orders/getorderhistory or /key/market/GetOrderHistory
        :param market: optional a string literal for the market (ie. BTC-LTC).
            If omitted, will return for all markets
        :type market: str
        :return: order history in JSON
        :rtype : dict
        """
        if market:
            return self._api_query(path_dict={
                API_V1_1: '/account/getorderhistory',
                #API_V2_0: '/key/market/GetOrderHistory'
            }, options={'market': market, 'marketname': market}, protection=PROTECTION_PRV)
        else:
            return self._api_query(path_dict={
                API_V1_1: '/account/getorderhistory',
                #API_V2_0: '/key/orders/getorderhistory'
            }, protection=PROTECTION_PRV)

    def get_order(self, uuid):
        """
        Used to get details of buy or sell order
        Endpoint:
        1.1 /account/getorder
        2.0 /key/orders/getorder
        :param uuid: uuid of buy or sell order
        :type uuid: str
        :return:
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/account/getorder',
            #API_V2_0: '/key/orders/getorder'
        }, options={'uuid': uuid, 'orderid': uuid}, protection=PROTECTION_PRV)

    def get_withdrawal_history(self, currency=None):
        """
        Used to view your history of withdrawals
        Endpoint:
        1.1 /account/getwithdrawalhistory
        2.0 /key/balance/getwithdrawalhistory
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: withdrawal history in JSON
        :rtype : dict
        """

        return self._api_query(path_dict={
            API_V1_1: '/account/getwithdrawalhistory',
            #API_V2_0: '/key/balance/getwithdrawalhistory'
        }, options={'currency': currency, 'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def get_deposit_history(self, currency=None):
        """
        Used to view your history of deposits
        Endpoint:
        1.1 /account/getdeposithistory
        2.0 /key/balance/getdeposithistory
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: deposit history in JSON
        :rtype : dict
        """
        return self._api_query(path_dict={
            API_V1_1: '/account/getdeposithistory',
            #API_V2_0: '/key/balance/getdeposithistory'
        }, options={'currency': currency, 'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def list_markets_by_currency(self, currency):
        """
        Helper function to see which markets exist for a currency.
        Endpoint: /public/getmarkets
        Example ::
            >>> Bittrex(None, None).list_markets_by_currency('LTC')
            ['BTC-LTC', 'ETH-LTC', 'USDT-LTC']
        :param currency: String literal for the currency (ex: LTC)
        :type currency: str
        :return: List of markets that the currency appears in
        :rtype: list
        """
        return [market['MarketName'] for market in self.get_markets()['result']
                if market['MarketName'].lower().endswith(currency.lower())]

    def get_wallet_health(self):
        """
        Used to view wallet health
        Endpoints:
        1.1 NO Equivalent
        2.0 /pub/Currencies/GetWalletHealth
        :return:
        """
        return self._api_query(path_dict={
            #API_V2_0: '/pub/Currencies/GetWalletHealth'
        }, protection=PROTECTION_PUB)

    def get_balance_distribution(self):
        """
        Used to view balance distibution
        Endpoints:
        1.1 NO Equivalent
        2.0 /pub/Currency/GetBalanceDistribution
        :return:
        """
        return self._api_query(path_dict={
            #API_V2_0: '/pub/Currency/GetBalanceDistribution'
        }, protection=PROTECTION_PUB)

    def get_pending_withdrawals(self, currency=None):
        """
        Used to view your pending withdrawals
        Endpoint:
        1.1 NO EQUIVALENT
        2.0 /key/balance/getpendingwithdrawals
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: pending withdrawals in JSON
        :rtype : list
        """
        return self._api_query(path_dict={
            #API_V2_0: '/key/balance/getpendingwithdrawals'
        }, options={'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def get_pending_deposits(self, currency=None):
        """
        Used to view your pending deposits
        Endpoint:
        1.1 NO EQUIVALENT
        2.0 /key/balance/getpendingdeposits
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: pending deposits in JSON
        :rtype : list
        """
        return self._api_query(path_dict={
            #API_V2_0: '/key/balance/getpendingdeposits'
        }, options={'currencyname': currency} if currency else None,
            protection=PROTECTION_PRV)

    def generate_deposit_address(self, currency):
        """
        Generate a deposit address for the specified currency
        Endpoint:
        1.1 NO EQUIVALENT
        2.0 /key/balance/generatedepositaddress
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: result of creation operation
        :rtype : dict
        """
        return self._api_query(path_dict={
            #API_V2_0: '/key/balance/getpendingdeposits'
        }, options={'currencyname': currency}, protection=PROTECTION_PRV)

    def trade_sell(self, market=None, order_type=None, quantity=None, rate=None, time_in_effect=None,
                   condition_type=None, target=0.0):
        """
        Enter a sell order into the book
        Endpoint
        1.1 NO EQUIVALENT -- see sell_market or sell_limit
        2.0 /key/market/tradesell
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param order_type: ORDERTYPE_LIMIT = 'LIMIT' or ORDERTYPE_MARKET = 'MARKET'
        :type order_type: str
        :param quantity: The amount to purchase
        :type quantity: float
        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float
        :param time_in_effect: TIMEINEFFECT_GOOD_TIL_CANCELLED = 'GOOD_TIL_CANCELLED',
                TIMEINEFFECT_IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL', or TIMEINEFFECT_FILL_OR_KILL = 'FILL_OR_KILL'
        :type time_in_effect: str
        :param condition_type: CONDITIONTYPE_NONE = 'NONE', CONDITIONTYPE_GREATER_THAN = 'GREATER_THAN',
                CONDITIONTYPE_LESS_THAN = 'LESS_THAN', CONDITIONTYPE_STOP_LOSS_FIXED = 'STOP_LOSS_FIXED',
                CONDITIONTYPE_STOP_LOSS_PERCENTAGE = 'STOP_LOSS_PERCENTAGE'
        :type condition_type: str
        :param target: used in conjunction with condition_type
        :type target: float
        :return:
        """
        return self._api_query(path_dict={
            #API_V2_0: '/key/market/tradesell'
        }, options={
            'marketname': market,
            'ordertype': order_type,
            'quantity': quantity,
            'rate': rate,
            'timeInEffect': time_in_effect,
            'conditiontype': condition_type,
            'target': target
        }, protection=PROTECTION_PRV)

    def trade_buy(self, market=None, order_type=None, quantity=None, rate=None, time_in_effect=None,
                  condition_type=None, target=0.0):
        """
        Enter a buy order into the book
        Endpoint
        1.1 NO EQUIVALENT -- see buy_market or buy_limit
        2.0 /key/market/tradebuy
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param order_type: ORDERTYPE_LIMIT = 'LIMIT' or ORDERTYPE_MARKET = 'MARKET'
        :type order_type: str
        :param quantity: The amount to purchase
        :type quantity: float
        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float
        :param time_in_effect: TIMEINEFFECT_GOOD_TIL_CANCELLED = 'GOOD_TIL_CANCELLED',
                TIMEINEFFECT_IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL', or TIMEINEFFECT_FILL_OR_KILL = 'FILL_OR_KILL'
        :type time_in_effect: str
        :param condition_type: CONDITIONTYPE_NONE = 'NONE', CONDITIONTYPE_GREATER_THAN = 'GREATER_THAN',
                CONDITIONTYPE_LESS_THAN = 'LESS_THAN', CONDITIONTYPE_STOP_LOSS_FIXED = 'STOP_LOSS_FIXED',
                CONDITIONTYPE_STOP_LOSS_PERCENTAGE = 'STOP_LOSS_PERCENTAGE'
        :type condition_type: str
        :param target: used in conjunction with condition_type
        :type target: float
        :return:
        """
        return self._api_query(path_dict={
            #API_V2_0: '/key/market/tradebuy'
        }, options={
            'marketname': market,
            'ordertype': order_type,
            'quantity': quantity,
            'rate': rate,
            'timeInEffect': time_in_effect,
            'conditiontype': condition_type,
            'target': target
        }, protection=PROTECTION_PRV)

    def get_candles(self, market, tick_interval):
        """
        Used to get all tick candles for a market.
        Endpoint:
        1.1 NO EQUIVALENT
        2.0 /pub/market/GetTicks
        Example  ::
            { success: true,
              message: '',
              result:
               [ { O: 421.20630125,
                   H: 424.03951276,
                   L: 421.20630125,
                   C: 421.20630125,
                   V: 0.05187504,
                   T: '2016-04-08T00:00:00',
                   BV: 21.87921187 },
                 { O: 420.206,
                   H: 420.206,
                   L: 416.78743422,
                   C: 416.78743422,
                   V: 2.42281573,
                   T: '2016-04-09T00:00:00',
                   BV: 1012.63286332 }]
            }
        :return: Available tick candles in JSON
        :rtype: dict
        """

        return self._api_query(path_dict={
            #API_V2_0: '/pub/market/GetTicks'
        }, options={
            'marketName': market, 'tickInterval': tick_interval
        }, protection=PROTECTION_PUB)

    def get_latest_candle(self, market, tick_interval):
        """
        Used to get the latest candle for the market.
        Endpoint:
        1.1 NO EQUIVALENT
        2.0 /pub/market/GetLatestTick
        Example ::
            { success: true,
              message: '',
              result:
              [ {   O : 0.00350397,
                    H : 0.00351000,
                    L : 0.00350000,
                    C : 0.00350350,
                    V : 1326.42643480,
                    T : 2017-11-03T03:18:00,
                    BV: 4.64416189 } ]
            }
        :return: Available latest tick candle in JSON
        :rtype: dict
        """

        return self._api_query(path_dict={
            #API_V2_0: '/pub/market/GetLatestTick'
        }, options={
            'marketName': market, 'tickInterval': tick_interval
        }, protection=PROTECTION_PUB)

    def get_price(self, currency, denom):
        market = denom.upper() + '-' + currency.upper()
        return float(self.get_ticker(market)['result']['Last'])

    def get_balances(self):
        if self.balances is None:
            self.balances = dict()
            for balance in self._request_get_balances()['result']:
                if balance['Balance'] > 0:
                    self.balances[balance['Currency'].lower()] = float(balance['Balance'])
        return self.balances

    def get_total_balance_in_btc(self):
        # print("[Bittrex]\nCalculating total balance in BTC...")
        total = 0.0
        balances = self.get_balances()
        for balance in balances['result']:
            if balance['Balance'] > 0:
                # print(balance['Currency'] + ': ' + str(balance['Balance']))
                if not 'BTC' in balance['Currency']:
                    market = 'BTC-' + balance['Currency']
                    total += self.get_latest_price(market) * balance['Balance']
                else:
                    total += balance['Balance']

        self.total_balance_in_btc = total
        #print('Total BTC = ' + str(total))
        return total

    def get_total_balance_in_usd(self):
        btc_price = self.get_btc_price()
        total = 0.0
        if self.total_balance_in_btc is not -1:
            total = self.total_balance_in_btc * btc_price
        else:
            total = self.get_total_balance_in_btc() * btc_price
        #print('Total USD = ' + str(total))
        return total

    def get_btc_price(self):
        btc_price = self.get_latest_price(market='USDT-BTC')
        #print('1BTC = ' + str(btc_price) + 'USDT')
        return btc_price
