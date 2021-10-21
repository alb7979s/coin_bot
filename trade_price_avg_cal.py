krw, btc, market = [], [], {}
while True:
    try:
        i1, i2 = input().split()
        if i1[:3] == 'KRW': krw.append(float(i2))
        else: btc.append(float(i2))
        market[i2] = i1
    except:
        break
krw.sort(reverse=True)
btc.sort(reverse=True)
percent = 5
print('krw', krw)
print('btc', market[str(btc[0])])
print(f'krw 거래 상위 {percent}%: {krw[int(len(krw)*percent/100)]}')
print(f'btc 거래 상위 {percent}%: {btc[int(len(btc)*percent/100)]}')