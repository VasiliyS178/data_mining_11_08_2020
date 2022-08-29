import requests

# press F12 in Chrome - Network - Fetch/XHR - all/ - RBM - copy - Node.js fetch
url = "https://auto.ru/sankt-peterburg/cars/audi/all/"
params = {
  "headers": {
    "accept": "application/json",
    "accept-language": "ru,en;q=0.9",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Yandex\";v=\"22\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-csrf-token": "e05d0bfa06da2261fec318eb6a807341c9e05fbf94250b7d",
    "x-requested-with": "fetch",
    "x-susanin-react": "true",
    "cookie": "_csrf_token=e05d0bfa06da2261fec318eb6a807341c9e05fbf94250b7d; autoru_sid=a%3Ag621b2405236rcv7kfhal0stl8ndqric.92605d754cde6352038c124feb2e12ca%7C1645945861041.604800.SM8p8wVd_B-3w0w63s83eQ.G6rysVEaIpw1sHNFHujLCC4aR-VODScXUPNzVJy69MY; autoruuid=g621b2405236rcv7kfhal0stl8ndqric.92605d754cde6352038c124feb2e12ca; suid=d02db9e5b00cab0cc9c01e1d7eae2bfa.39417867ec1f6686b838987329fc7f54; from=yandex; X-Vertis-DC=vla; yuidlt=1; yandexuid=2236891391598724671; my=YwA%3D; crookie=Jmmt2Vxq+HWVUyICXH61iYliCRPXK1Nu9u9EFC3bw/ehumwC6cSxjYbA8gOkk7K6BAGnPEPf9Y1K0PZZPgPKaXCL/OE=; cmtchd=MTY0NTk0NTg2MjA2Ng==; credit_filter_promo_popup_closed=true; gdpr=0; _ym_isad=2; _ym_uid=1645945865900315531; _yasc=2wFUA5q1Lk8vByBZ1kPjXu0hmrzw3HtZOzIXDlyRLKO6vtHS; Session_id=3:1645945871.5.0.1598724747018:UgjjvA:b.1.2:1|6347174.0.2|231574015.20648084.2.2:20648084|61:2618.904337.WMOAxcjHXoj9IWVaaUQqUDifFnE; yandex_login=Vasey; ys=udn.cDpWYXNleQ%3D%3D#c_chck.1102200699; i=jibhpSi0RGrL2itZkpjYIsTJqN1sVxmjuV4OTIWbmqN6K3OOvnDjm3w86XEnFjcRe8GfaO6FfdYKjjjvvphBj02zroI=; mda2_beacon=1645945871061; sso_status=sso.passport.yandex.ru:synchronized; cycada=lH2/l+93NyZsKoRg1jRG0XueCwKFguvRs6qiAgaYLUo=; from_lifetime=1645946603294; _ym_d=1645946603",
    "Referer": "https://auto.ru/sankt-peterburg/",
    "Referrer-Policy": "no-referrer-when-downgrade"
  },
  "body": None,
  "method": "GET"
}


def fetch(url, params):
    headers = params['headers']
    # body = params['body'].encode('utf-8')
    body = None
    if params['method'] == 'GET':
        return requests.get(url, headers=headers)
    if params['method'] == 'POST':
        return requests.post(url, headers=headers, data=body)


audi_response = fetch(url, params)
print(audi_response.status_code)
print(audi_response.json().keys())

cars = audi_response.json()['listing']['offers']
for car in cars:
    print(car['lk_summary'])
