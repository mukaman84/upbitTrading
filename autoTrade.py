import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
import uriClass
import json
from collections import Counter
import time
import utils
import numpy as np
#############################################
import matplotlib.pyplot as plt
import pandas as pd
#############################################

uriClass = uriClass.uriClass()
m = hashlib.sha512()
query = {
    'market': 'KRW-ETH',
}
query_string = urlencode(query).encode()
m.update(query_string)
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

# res = requests.get(uriClass.server_url + uriClass.account_uri, params=query, headers=headers)
res = requests.get(uriClass.server_url + uriClass.account_market_all, headers=headers)

str2json = res.json()

market_list = [market_code['market'] for market_code in str2json]

max_N=30
list_top_50_volue=dict()


# for market_code in market_list:

str_market = ','.join(market_list)
querystring = {"markets": "{}".format(str_market)}

res = requests.request("GET", uriClass.server_url + uriClass.current_price, params=querystring)

text_res = res.text
list_res=json.loads(text_res)

for item in list_res:
    if item['market'][:3]=='KRW':
        list_top_50_volue[item['market']]=item['acc_trade_price_24h']
d = Counter(list_top_50_volue)
# get a top 50 item list
t=d.most_common(max_N)


dict_pd=dict()
w_size=20
pb=2


list_buying=[]

list_end=[]
dict_buying = dict()
dict_buying_mounts = dict()

start = time.time()
while(1):
    for item in t:
        querystring = {"market": "{}".format(item[0]), "count": "200"}
        res = requests.request("GET", uriClass.server_url + uriClass.candle_minutes, params=querystring)
        flag=False
        while(flag==False):
            # try:
                if res.status_code == 200:
                    str2json= res.json()
                    list_close=[str2json['trade_price'] for str2json in reversed(str2json)]
                    my_df = pd.DataFrame(data=list_close, columns=['close'])
                    my_df['moving_average'] = my_df['close'].rolling(window=20,min_periods=1).mean()
                    my_df['SD'] = my_df['close'].rolling(window=20,min_periods=1).std()
                    my_df['Upper BollingerBand'] = my_df['moving_average'] + (my_df['SD']*pb)
                    my_df['Lower BollingerBand'] = my_df['moving_average'] - (my_df['SD']*pb)
                    my_df['Band Gap'] = (my_df['Upper BollingerBand'] - my_df['Lower BollingerBand']) / my_df['moving_average']
                    my_df.head()
                    plt.subplot(2, 1, 1)
                    plt.plot(my_df.index,my_df['close'],label='close')
                    plt.plot(my_df.index,my_df['moving_average'],label='moving_average')
                    plt.plot(my_df.index,my_df['Upper BollingerBand'],label='Upper BollingerBand')
                    plt.plot(my_df.index,my_df['Lower BollingerBand'],label='Lower BollingerBand')
                    plt.subplot(2, 1, 2)
                    plt.plot(my_df.index, my_df['Band Gap'], label='Band Gap')
                    plt.legend(loc='best')
                    plt.grid()
                    plt.show()

                    print("test")
                    # if len(list_buying)>0:

                    if False:
                        # list_buying.append(dict_buying)
                        # list_temp_buying = [buying_obj.keys() for buying_obj in list_buying]

                        # dict_buying[item[0]]
                        # del dict_buying_mounts[item[0]]

                        avg_buy_price, balance = utils.get_order_status(item[0])
                        dict_buying[item[0]] = float(avg_buy_price)
                        dict_buying_mounts[item[0]] = float(balance)


                        # if item[0] in dict_buying.keys():
                        if float(dict_buying_mounts[item[0]]) > 0:
                            if dict_buying[item[0]]*1.02 < my_df['close'].values[-1]:
                                if dict_buying_mounts[item[0]] > 0:
                                    trading_volume = str(dict_buying_mounts[item[0]])
                                    utils.do_sell(market=item[0], close=my_df['close'].values[-1])

                        if my_df['close'].values[-1] < my_df['Lower BollingerBand'].values[-1] and float(dict_buying[item[0]])==0.0:
                            status_code = utils.do_buy(market=item[0], close=my_df['close'].values[-1])
                            # if status_code == 200:
                            dict_buying[item[0]] = float(my_df['close'].values[-1])
                            print("check status")

                        # if my_df['close'].values[-1] < my_df['Lower BollingerBand'].values[-1]*0.99:
                        #     print("check status1")
                        #
                        if my_df['close'].values[-1] < my_df['Lower BollingerBand'].values[-1]:
                            print("check status2")



                        # if my_df['close'].values[-1] < my_df['Lower BollingerBand'].values[-1]:
                        #     print('buying'+item[0]+' : '+str(my_df['close'].values[-1]))
                        # if item[0] == 'KRW-XRP':
                        #     print('KRW-XRP',my_df['close'].values[-1])
                        # else:
                        #     print(item[0])

                    flag=True

                    dict_pd[item[0]]=my_df
                else:
                    res = requests.request("GET", uriClass.server_url + uriClass.candle_minutes, params=querystring)

            # except Exception as e:
            #     res = requests.request("GET", uriClass.server_url + uriClass.candle_minutes, params=querystring)
            #     time.sleep(0.02)
            #     print("error occurs", e)
    time.sleep(3)
    counter = int((time.time() - start)/10)
    if counter % (6*10)==0:
        print('dict_buying lefting : ',str(dict_buying))
    # print("time :", counter)
