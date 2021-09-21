krw, btc = [], []
while True:
    try:
        i1, i2 = input().split()
        if i1[:3] == 'KRW': krw.append(float(i2))
        else: btc.append(float(i2))
    except:
        break
krw.sort(reverse=True)
btc.sort(reverse=True)
percent = 30
print(f'krw 거래 상위 {percent}%: {krw[int(len(krw)*percent/100)]}')
print(f'btc 거래 상위 {percent}%: {btc[int(len(btc)*percent/100)]}')