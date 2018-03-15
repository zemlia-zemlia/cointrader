#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import collections
import time
from cointrader.exchanges.poloniex import Poloniex as PoloniexApi
from cointrader.chart import Chart
from cointrader.indicators import MIN_POINTS


def get_market_name(market):
    return market[0]


def add_fee(btc, fee=0.025):
    return btc - (btc / 100 * fee)


class ExchangeException(Exception):
    pass


class Coin(object):

    """Docstring for Coin."""

    def __init__(self, name, quantity, btc_value=None):
        self.name = name
        self.quantity = quantity
        self.btc_value = btc_value

    @property
    def value(self):
        return self.btc_value


class Market(object):

    """Docstring for Market. """

    def __init__(self, exchange, name, dry_run=False):
        """TODO: to be defined1.

        :name: TODO

        """
        self._exchange = exchange
        self._name = name
        self._dry_run = dry_run

    @property
    def currency(self):
        pair = self._name.split("_")
        return pair[1]

    @property
    def url(self):
        return "{}{}".format(self._exchange.url, self._name)

    def _get_chart_data(self, resolution, start, end):
        """Will return the data for the chart."""
        # To ensure that the data cointains enough data to calculate SMA
        # or EMA right from the start we need to calculate internal
        # start date of the chart which lies before the given start
        # date. On default we excpect at least 120 data points in the
        # chart to be present.
        period = self._exchange.resolution2seconds(resolution)
        internal_start = start - datetime.timedelta(seconds=period * MIN_POINTS)
        return self._exchange._api.chart(self._name, internal_start, end, period)

    def get_chart(self, resolution="30m", start=None, end=None):
        """Will return a chart of the market.

        You can provide a `resolution` of the chart. On default the
        chart will have a resolution of 30m.

        You can define a different timeframe by providing a `start` and
        `end` point. On default the the chart will include the last
        recent data.

        :resolution: Resolution of the chart (Default 30m)
        :start: Start of the chart data (Default Now)
        :end: End of the chart data (Default Now)
        :returns: Chart instance.
        """
        if end is None:
            end = datetime.datetime.utcnow()
        if start is None:
            start = datetime.datetime.utcnow()

        data = self._get_chart_data(resolution, start, end)
        return Chart(data, start, end)

    def buy(self, btc, price=None, option=None):
        """Will buy coins on the market for the given amount of BTC. On
        default we will make a market order which means we will try to
        buy for the best price available. If price is given the order
        will be placed for at the given price. You can optionally
        provide some options. See
        :class:`cointrader.exchanges.poloniex.api` for more details.

        :btc: Amount of BTC
        :price: Optionally price for which you want to buy
        :option: Optionally some buy options
        :returns: Dict witch details on the order.
        """
        if price is None:
            # Get best price on market.
            orderbook = self._exchange._api.book(self._name)
            asks = orderbook["asks"]   # Asks in the meaning of "I wand X for Y"
            best_offer = asks[-1]
            price = float(best_offer[0])
        amount = btc / price
        if self._dry_run:
            amount = add_fee(amount)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                    u'resultingTrades': [
                        {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                         u'rate': u'{}'.format(price),
                         u'amount': u'{}'.format(amount),
                         u'date': u'{}'.format(date),
                         u'total': u'{}'.format(btc),
                         u'type': u'buy'}]}
        else:
            return self._exchange._api.buy(self._name, amount, price, option)

    def sell(self, amount, price=None, option=None):
        if price is None:
            # Get best price on market.
            orderbook = self._exchange._api.book(self._name)
            bids = orderbook["bids"]  # Bids in the meaning of "I give you X for Y"
            best_offer = bids[-1]
            price = float(best_offer[0])
        btc = amount * price
        if self._dry_run:
            btc = add_fee(btc)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                    u'resultingTrades': [
                        {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                         u'rate': u'{}'.format(price),
                         u'amount': u'{}'.format(amount),
                         u'date': u'{}'.format(date),
                         u'total': u'{}'.format(btc),
                         u'type': u'sell'}]}
        else:
            return self._exchange._api.sell(self._name, amount, price, option)


class BacktestMarket(Market):

    """Market to enable backtesting a strategy on the market."""

    def __init__(self, exchange, name):
        """TODO: to be defined1.

        :exchange: TODO
        :name: TODO

        """
        Market.__init__(self, exchange, name)
        self._chart_data = None
        self._backtest_tick = 1

    def continue_backtest(self):
        self._backtest_tick += 1
        if self._chart_data and len(self._chart_data) >= self._backtest_tick:
            return True
        return False

    def get_chart(self, resolution="30m", start=None, end=None):
        if self._chart_data is None:
            self._chart_data = self._get_chart_data(resolution, start, end)
            self._backtest_tick += MIN_POINTS
        return Chart(self._chart_data[0:self._backtest_tick], start, end)

    def buy(self, btc, price=None):
        price = float(self._chart_data[0:self._backtest_tick][-1]['close'])
        date = datetime.datetime.utcfromtimestamp(self._chart_data[0:self._backtest_tick][-1]['date'])
        btc = add_fee(btc)
        amount = btc / price
        return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                u'resultingTrades': [
                    {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                     u'rate': u'{}'.format(price),
                     u'amount': u'{}'.format(amount),
                     u'date': u'{}'.format(date),
                     u'total': u'{}'.format(btc),
                     u'type': u'buy'}]}

    def sell(self, amount, price=None):
        price = float(self._chart_data[0:self._backtest_tick][-1]['close'])
        date = datetime.datetime.utcfromtimestamp(self._chart_data[0:self._backtest_tick][-1]['date'])
        btc = add_fee(amount * price)
        return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                u'resultingTrades': [
                    {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                     u'rate': u'{}'.format(price),
                     u'amount': u'{}'.format(amount),
                     u'date': u'{}'.format(date),
                     u'total': u'{}'.format(btc),
                     u'type': u'sell'}]}


class Exchange(object):

    """Baseclass for all exchanges"""

    # According to Poloniex support the following candlestick period in
    # seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400.
    resolutions = {"5m": 300,
                   "15m": 900,
                   "30m": 1800,
                   "2h": 7200,
                   "4h": 14400,
                   "24h": 86400}

    def __init__(self, config, api=None):
        """TODO: to be defined1. """
        self._api = api
        self.coins = collections.OrderedDict()

        # Setup coins
        balance = self._api.balance()
        for currency in sorted(balance):
            if balance[currency]["btc_value"] > 0:
                self.coins[currency] = Coin(currency,
                                            balance[currency]["quantity"],
                                            balance[currency]["btc_value"])

    @property
    def url(self):
        raise NotImplementedError

    @property
    def total_btc_value(self):
        return sum([self.coins[c].value for c in self.coins])

    @property
    def total_euro_value(self, limit=10):
        ticker = self._api.ticker()
        return float(ticker["USDT_BTC"]["last"]) * self.total_btc_value

    @property
    def markets(self):
        ticker = self._api.ticker()
        tmp = {}
        for currency in ticker:
            if currency.startswith("BTC_"):
                change = round(float(ticker[currency]["percentChange"]) * 100, 2)
                volume = round(float(ticker[currency]["baseVolume"]), 1)
                tmp[currency] = {"volume": volume, "change": change}
        return tmp

    def get_top_markets(self, markets, limit=10):
        if not markets:
            markets = self.markets
        top_profit = self.get_top_profit_markets(markets, limit)
        top_volume = self.get_top_volume_markets(markets, limit)
        top_profit_markets = set(map(get_market_name, top_profit))
        top_volume_markets = set(map(get_market_name, top_volume))

        top_markets = {}
        for market in top_profit_markets.intersection(top_volume_markets):
            top_markets[market] = markets[market]
        return sorted(top_markets.items(), key=lambda x: x[1]["change"], reverse=True)[0:limit]

    def get_top_profit_markets(self, markets=None, limit=10):
        if not markets:
            markets = self.markets
        return sorted(markets.items(),
                      key=lambda x: (float(x[1]["change"]), float(x[1]["volume"])), reverse=True)[0:limit]

    def get_top_volume_markets(self, markets=None, limit=10):
        if not markets:
            markets = self.markets
        return sorted(markets.items(),
                      key=lambda x: (float(x[1]["volume"]), float(x[1]["change"])), reverse=True)[0:limit]

    def is_valid_market(self, market):
        return market in self.markets

    def is_valid_resolution(self, resolution):
        return resolution in self.resolutions

    def resolution2seconds(self, resolution):
        try:
            return self.resolutions[resolution]
        except KeyError:
            raise ExchangeException("Resolution {} is not supported.\n"
                                    "Please choose one of the following: {}".format(resolution, ", ".join(self.resolutions.keys())))


class Poloniex(Exchange):

    def __init__(self, config):
        api = PoloniexApi(config)
        Exchange.__init__(self, config, api)

    @property
    def url(self):
        return "https://poloniex.com/exchange#"

    def btc2dollar(self, amount):
        ticker = self._api.ticker("USDT_BTC")
        rate = float(ticker["last"])
        return round(amount * rate, 2)

    def dollar2btc(self, amount):
        ticker = self._api.ticker("USDT_BTC")
        rate = float(ticker["last"])
        return round(amount / rate, 8)

    def get_balance(self, currency=None):
        if currency is None:
            return self._api.balance()
        else:
            return self._api.balance()[currency]
