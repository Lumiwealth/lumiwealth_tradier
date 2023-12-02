import datetime as dt

import pandas as pd

from .base import TradierApiBase


class Quotes(TradierApiBase):
    def __init__(self, account_number, auth_token, is_paper=True):
        TradierApiBase.__init__(self, account_number, auth_token, is_paper)

        # Quotes endpoints for market data about equities
        self.QUOTES_ENDPOINT = "v1/markets/quotes"  # GET (POST)
        self.QUOTES_HISTORICAL_ENDPOINT = "v1/markets/history"  # GET
        self.QUOTES_SEARCH_ENDPOINT = "v1/markets/search"  # GET
        self.QUOTES_TIMESALES_ENDPOINT = "v1/markets/timesales"  # GET

    def get_historical_quotes(self, symbol, interval='daily', start_date=False, end_date=False):
        """
        Fetch historical stock data for a given symbol from the Tradier Account API.

        This function makes a GET request to the Tradier Account API to retrieve historical stock
        data for a specified symbol within a specified time interval.

        Args:
            symbol (str): The trading symbol of the stock (e.g., 'AAPL', 'MSFT') for which you want
                          to retrieve historical data.
            interval (str, optional): The time interval for historical data. Default is 'daily'. Alt values are
                                      'weekly' or 'monthly'.
            start_date (str, optional): The start date for historical data in the format 'YYYY-MM-DD'.
                                       If not provided, the function will default to the most recent Monday.
            end_date (str, optional): The end date for historical data in the format 'YYYY-MM-DD'.
                                     If not provided, the function will default to the current date.

        Returns:
            pandas.DataFrame: A DataFrame containing historical stock data for the specified symbol.

        Example:
            # Create a Quotes instance
            q = Quotes(ACCOUNT_NUMBER, AUTH_TOKEN)

            # Retrieve historical stock data for symbol 'BIIB'
            historical_data = q.get_historical_quotes(symbol='BIIB')

            Sample Output:
                     date    open     high     low   close   volume
            0  2023-08-28  265.40  266.470  263.54  265.05   359872
            1  2023-08-29  265.35  268.150  265.11  268.00   524972
            2  2023-08-30  268.84  269.460  265.25  267.18   552728
            3  2023-08-31  266.83  269.175  265.32  267.36  1012842
            4  2023-09-01  269.01  269.720  266.91  267.17   522401
        """

        def last_monday(input_date):
            """
            Helper function used to index the start of the trading week
            Find the date of the previous Monday for a given input date.

            Args:
                input_date (datetime.date): the input date

            Returns:
                datetime.date: The date of the previous Monday.
            """
            return input_date - dt.timedelta(days=(input_date.weekday()))

        if not end_date:
            end_date = dt.datetime.today().strftime('%Y-%m-%d')

        if not start_date:
            tmp = dt.datetime.strptime(end_date, '%Y-%m-%d')
            start_date = last_monday(tmp).strftime('%Y-%m-%d')

        params = {
            'symbol': symbol,
            'interval': interval,
            'start': start_date,
            'end': end_date
        }
        data = self.request(self.QUOTES_HISTORICAL_ENDPOINT, params=params)
        return pd.DataFrame(data['history']['day'])

    def get_quote_day(self, symbol, last_price=False):
        """
        Fetch the current quote data for a given symbol from the Tradier Account API.

        This function makes a GET request to the Tradier Account API to retrieve the current quote
        data for a specified symbol.

        Args:
            symbol (str): The trading symbol of the stock (e.g., 'AAPL', 'MSFT') for which you want
                          to retrieve the current quote data.
            last_price (bool, optional): If True, only fetch the last price of the symbol. Default is False.

        Returns:
            pandas.DataFrame or float: A DataFrame containing the current quote data for the specified symbol
                                       or just the last price as a float if last_price is set to True.

        Example:
            # Retrieve current quote data for symbol 'CCL' and transpose the DataFrame for easy viewing
            quote_data = q.get_quote_day(symbol='CCL').T

            Sample Output:
                                       0
            symbol                 CCL
            description  Carnival Corp
            exch                     N
            type                 stock
            last                 15.73
            change               -0.09
            volume            16767253
            open                 15.83
            high                 16.06
            low                  15.58
            close                15.73
            bid                   15.7
            ask                  15.73
            change_percentage    -0.57
            average_volume    39539044
            last_volume              0
            trade_date   1693609200001
            prevclose            15.82
            week_52_high         19.55
            week_52_low           6.11
            bidsize                 11
            bidexch                  P
            bid_date     1693612800000
            asksize                 29
            askexch                  P
            ask_date     1693612764000
            root_symbols           CCL

            # Retrieve only the last price for symbol 'CCL'
            last_price = q.get_quote_day(symbol='CCL', last_price=True)
            Sample Output: 15.73
        """
        params = {'symbols': symbol, 'greeks': 'false'}
        data = self.request(self.QUOTES_ENDPOINT, params=params)
        df_quote = pd.json_normalize(data['quotes']['quote'])

        if last_price:
            return float(df_quote['last'])

        return df_quote

    def get_timesales(self, symbol, interval='1min', start_time=False, end_time=False):
        # noinspection GrazieInspection
        """
        This function returns the tick data for `symbol` in increments specified by `interval`.
        Eventually, we can use this to analyze/visualze stock data in a time series context.

        Arguments `start_time` and `end_time` must be strings with format 'YYYY-MM-DD HH:MM'

        Sample output:
            >>> quotes = Quotes('ACCOUNT_NUMBER', 'AUTH_TOKEN')
            >>> quotes.get_timesales('VZ', start_time='2023-09-27 09:45', end_time='2023-09-27 14:00')
                                time   timestamp     price   open   high      low   close  volume       vwap
            0    2023-09-27T09:45:00  1695822300  32.92995  32.95  32.95  32.9099  32.915   39077  32.924828
            1    2023-09-27T09:46:00  1695822360  32.89560  32.91  32.91  32.8800  32.895   32867  32.891113
            2    2023-09-27T09:47:00  1695822420  32.88750  32.89  32.91  32.8650  32.910   75720  32.888736
            3    2023-09-27T09:48:00  1695822480  32.91750  32.91  32.92  32.9100  32.910   15126  32.913109
            4    2023-09-27T09:49:00  1695822540  32.91000  32.91  32.92  32.9000  32.920   20335  32.907385
            ..                   ...         ...       ...    ...    ...      ...     ...     ...        ...
            251  2023-09-27T13:56:00  1695837360  32.35425  32.34  32.36  32.3430  32.360   58256  32.354522
            252  2023-09-27T13:57:00  1695837420  32.35500  32.35  32.36  32.3500  32.360   15825  32.355307
            253  2023-09-27T13:58:00  1695837480  32.36125  32.35  32.37  32.3525  32.365   34624  32.362786
            254  2023-09-27T13:59:00  1695837540  32.37500  32.37  32.39  32.3600  32.390   27728  32.370699
            255  2023-09-27T14:00:00  1695837600  32.38750  32.38  32.39  32.3800  32.385   53837  32.386281

            (vwap = volume weighted average price during the interval)
        """
        r_params = {'symbol': symbol}
        if start_time:
            r_params['start'] = start_time
        if end_time:
            r_params['end'] = end_time

        data = self.request(self.QUOTES_TIMESALES_ENDPOINT, params=r_params)
        return pd.json_normalize(data['series']['data'])

    def search_companies(self, query):
        if not query:
            return "Need that search term yo"

        params = {'q': query, 'indexes': 'false'}
        data = self.request(self.QUOTES_SEARCH_ENDPOINT, params=params)

        if not data['securities']:
            return "Nothing found"

        return pd.DataFrame(data['securities']['security'])
