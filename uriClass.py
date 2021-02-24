

class uriClass:
    def __init__(self):
        self.server_url = 'https://api.upbit.com'
        self.uri_account = "/v1/accounts"
        self.access_key = self.read_key('accesskey.txt')
        self.secret_key = self.read_key('secretkey.txt')
        self.get_uri_account()
        self.get_uri_market_all()
        self.get_uri_minute_candle()
        self.get_uri_current_price()

    def read_key(self, path2key):
        with open(path2key, "r") as f:
            return f.readline()

    def get_uri_account(self):
        self.account_uri = "/v1/accounts"

    def get_uri_market_all(self):
        self.account_market_all = "/v1/market/all"

    def get_uri_minute_candle(self):
        self.candle_minutes = '/v1/candles/minutes/15'

    def get_uri_current_price(self):
        self.current_price = '/v1/ticker'

