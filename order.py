# 주문
import datetime
import hashlib
import uuid
from urllib.parse import urlencode
import time
import jwt
import requests

from constant import *

class ORDER:
    def __init__(self, market=None, price=None, side=None, volume=None, ord_type=None, identifier=None):
        self.market = market
        self.price = price
        self.side = side
        self.volume = volume
        self.ord_type = ord_type
        self.identifier = identifier

def order(order_info):
    # volume: 매도 시 필수
    # price: 매수 시 필수

    is_buy = True if order_info.side == BUY else False
    query = {
        'market': order_info.market,
        'side': order_info.side,
        # 'volume': order_info.volume,
        # 'price': order_info.price,
        'ord_type': order_info.ord_type,
    }
    if is_buy:  # 매수
        query['price'] = order_info.price
    else:       # 매도
        query['volume'] = order_info.volume
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(SERVER_URL + "/v1/orders", params=query, headers=headers)
    return res.json()

def possible_order_search(market):
    query = {
        'market': market,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(SERVER_URL + "/v1/orders/chance", params=query, headers=headers)
    return res.json()

def order_withdraw():
    query = {
        'uuid': 'cdd92199-2897-4e14-9448-f923320408ad',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.delete(SERVER_URL + "/v1/order", params=query, headers=headers)

    print(res.json())


def order_list_search():
    query = {
        'state': 'done',
    }
    query_string = urlencode(query)

    uuids = [
        '9ca023a5-851b-4fec-9f0a-48cd83c2eaae',
        # ...
    ]
    uuids_query_string = '&'.join(["uuids[]={}".format(id) for id in uuids])

    query['uuids[]'] = uuids
    query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(SERVER_URL + "/v1/orders", params=query, headers=headers)

    print(res.json())


def account_search():
    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(SERVER_URL + "/v1/accounts", headers=headers)
    return res.json()

def price_search_minute(market):
    # PathParam: 분 단위(가능한 값 : 1, 3, 5, 15, 10, 30, 60, 240)
    url = f"https://api.upbit.com/v1/candles/minutes/{MINUTE}"
    # market(string): 마켓 코드, 캔들 개수(최대 200개),
    # to(string)
    # 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ss'Z' or yyyy-MM-dd HH:mm:ss. 비워서 요청시 가장 최근 캔들
    querystring = {"market": market, "count": COUNT}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    req_remain_check(response)
    return volume_check(response, PIVOT_VOL_RATE)


def volume_check(response, pivot):
    global account_markets
    infos = response.json()
    market = infos[-1]['market']
    increasing = True if (infos[-1]['trade_price'] > infos[-1]['opening_price']) else False
    vol_list, price_list = [], []
    for info in infos:
        vol_list.append(info['candle_acc_trade_volume'])
        price_list.append(info['high_price'])
        price_list.append(info['low_price'])
    MIN_VOL = min(vol_list[:-1])        #마지막 vol 일부분만 집계 돼서 MIN에선 제외
    RECENT_VOL = infos[-1]['candle_acc_trade_volume']
    if market in account_markets:
        if (higher_price[market] - (higher_price[market] * LOWER_BOUND_RATE)) > min(price_list):
            #sell
            order_info = order(ORDER(market=market, side=SELL, volume=possible_order_search(market)['ask_account']['balance'], ord_type=MARKET_PRICE_SELL))
            f.write(f"{convert_time(datetime.datetime.now())}-{market}: {order_info['price']}, SELL")
            account_markets.remove(market)
        else:
            higher_price[market] = max(higher_price)
    return (RECENT_VOL > (MIN_VOL * pivot)) and increasing

def req_remain_check(response):
    group, min, sec = response.headers['Remaining-Req'].split(';')
    min_time, sec_time = min[min.index('=') + 1:], sec[sec.index('=') + 1:]
    print(f'remain: min-{min_time}, sec-{sec_time}')
    if int(min_time) <= 3:
        time.sleep(60)
    elif int(sec_time) <= 3:
        time.sleep(1)


def market_code_search():
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails": "false"}

    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, params=querystring)

    markets = []
    for infos in response.json():
        market = infos['market']
        if EXCEPT_MARKET in market: continue
        markets.append(market)
    return markets


def live_price_search():
    url = "https://api.upbit.com/v1/ticker"

    headers = {"Accept": "application/json"}
    querystring = {"markets": "KRW-BTC"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()


def convert_time(time):
    time = time.strftime('%H:%M:%S')
    hour, min, sec = time.split(':')
    return int(sec) + (int(min) * 60) + (int(hour) * 60 * 60)


# start_time = convert_time(datetime.datetime.now())

def all_sell():
    accounts = account_search()
    for account in accounts:
        market = account['unit_currency']+"-"+account['currency']
        if market in ['KRW-BTC', 'KRW-KRW']: continue
        volume = possible_order_search(market)['ask_account']['balance']
        order(ORDER(market=market, side=SELL, volume=volume, ord_type=MARKET_PRICE_SELL))
if __name__ == '__main__':
    higher_price = {}

    # 코드 검색
    markets = market_code_search()
    with open("trade_detail.txt", 'a') as f:
        while True:
            account_markets = set()
            # 판매
            accounts = account_search()
            for account in accounts:
                market = account['unit_currency']+"-"+account['currency']
                if market in ['KRW-BTC', 'KRW-KRW']: continue
                account_markets.add(market)
                if market not in higher_price: higher_price[market] = 0
                price_search_minute(market)
            do_buy_list = []
            # 봉 검색
            for i, market in enumerate(markets):
                try:
                    if price_search_minute(market): do_buy_list.append(market)
                except:
                    print(ValueError)

            for market in do_buy_list:
                try:
                    if market in account_markets: continue
                    market_info = possible_order_search(market)
                    can_buy_money = float(market_info['bid_account']['balance']) * TRADE_RATE
                    if can_buy_money < market_info['bid']['min_total']: continue    # 최소 매수 금액보다 적으면 넘김
                    # can_buy_volume = (can_buy_money / order_info.price) % market_info['market.bit.price_unit']
                    order_info = order(ORDER(market=market, side=BUY, price=can_buy_money, ord_type=MARKET_PRICE_BUY))
                    f.write(f"{convert_time(datetime.datetime.now())}-{market}: {order_info['avg_price']}, BUY")
                except:
                    print(ValueError)