from urllib.parse import urlencode
import numpy as np
import hashlib
import uriClass
import jwt
import uuid
import requests


uriClass=uriClass.uriClass()

def buy_item(market,volume='0.01',price='100.0'):
    query = {
        'market': market,
        'side': 'bid',
        'volume': str(volume),
        'price': str(price),
        'ord_type': 'limit',
    }

    return query


def sell_item(market,volume='0.01',price='100.0'):
    query = {
        'market': market,
        'side': 'ask',
        'volume': str(volume),
        'price': str(price),
        'ord_type': 'limit',
    }
    return query

def check_order(market,volume='0.01',price='100.0'):
    query = {
        'market': market,
    }
    return query



def do_sell(market,close,trading_volume):
    trading_price = close
    # trading_volume = (np.floor((100000 / trading_price) * 100)) / 100
    sell_query = sell_item(market, volume=trading_volume, price=trading_price)
    sell_query_string = urlencode(sell_query).encode()

    m = hashlib.sha512()
    m.update(sell_query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': uriClass.access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, uriClass.secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.post(uriClass.server_url + "/v1/orders", params=sell_query, headers=headers)

    if res.status_code == 200:
        print('sell :', res.text)


def do_buy(market,close):
    # dict_buying[item[0]] = my_df['close'].values[-1]
    trading_price = close
    trading_volume = (np.floor((100000 / trading_price) * 100)) / 100
    buy_query = buy_item(market, volume=trading_volume, price=trading_price)
    buy_query_string = urlencode(buy_query).encode()

    m = hashlib.sha512()
    m.update(buy_query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': uriClass.access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, uriClass.secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.post(uriClass.server_url + "/v1/orders", params=buy_query, headers=headers)
    if res.status_code == 200:
        print("buy : ",res.text)
    else:
        print(res.text)

    return res.status_code

def get_order_status(market):
    status_query = buy_item(market)
    status_query_string = urlencode(status_query).encode()

    m = hashlib.sha512()
    m.update(status_query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': uriClass.access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, uriClass.secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.get(uriClass.server_url + "/v1/orders/chance", params=status_query, headers=headers)
    if res.status_code == 200:
        # print("buy : ", res.text)
        strStatus2json = res.json()
        if float(strStatus2json['ask_account']['balance']) == 0.0:
            return 0.0, 0.0
        else:
            return strStatus2json['ask_account']['avg_buy_price'], strStatus2json['ask_account']['balance']
    else:
        # print('status error : ', res.text)
        return 0,0







    # try:
    #     print('buying' + market + ' : ' + str(my_df['close'].values[-1]))
    # except Exception as e:
    #     print(e)

    # strbuy2json = res.json()
    # dict_buying_mounts[market] = strbuy2json['executed_volume']
    # print('selling' + item[0] + ' : ' + str(my_df['close'].values[-1]))
    # del dict_buying[item[0]]
    # del dict_buying_mounts[item[0]]