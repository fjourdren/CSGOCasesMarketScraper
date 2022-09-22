import json
import time
import requests
from datetime import datetime, timedelta

def nearest(inputDict, value):
    return min(inputDict, key=lambda sub: abs(sub - value))

def timestampToDatetime(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat()

def timestampToDatetimeDict(inputDict):
    return dict(map(lambda kv: (timestampToDatetime(kv[0]), kv[1]), inputDict.items()))

def preparePrices(cotations):
    output = {}
    for cotation in cotations:
        date = datetime.strptime(cotation[0], '%b %d %Y %H: +0').timestamp()
        price = cotation[1]

        output[date] = price

    return output

def getAuthCookie():
    try:
        with open('cookie.txt') as cookieFile:
            cookie = {
                'steamLoginSecure': cookieFile.read()
            }

            cookieFile.close()

            return cookie
    except IOError as e:
        raise IOError('Error while reading cookie.txt')

def requestPriceHistory(marketHashName):
    cookie = getAuthCookie()

    params = {
        'country': 'EN',
        'currency': 1,
        'appid': 730,
        'market_hash_name': marketHashName
    }

    # https://steamcommunity.com/market/pricehistory/?country=EN&currency=3&appid=730&market_hash_name=Winter%20Offensive%20Weapon%20Case
    response = requests.get('http://steamcommunity.com/market/pricehistory', cookies=cookie, params=params)
    if(response.status_code == 200):
        prices = response.json()['prices']
        return preparePrices(prices)
    else:
        raise ValueError('Error while getting prices')

def searchItem(market_hash_name):
    cookie = getAuthCookie()

    # https://steamcommunity.com/market/search/render/?query=Case&start=0&count=5000&search_descriptions=0&sort_column=default&sort_dir=desc&appid=730&category_730_ItemSet[]=any&category_730_ProPlayer[]=any&category_730_StickerCapsule[]=any&category_730_TournamentTeam[]=any&category_730_Weapon[]=any&category_730_Type[]=tag_CSGO_Type_WeaponCase&norender=1
    response = requests.get('https://steamcommunity.com/market/search/render/?query=' + market_hash_name + '&start=0&count=1&search_descriptions=0&sort_column=default&sort_dir=desc&appid=730&category_730_ItemSet[]=any&category_730_ProPlayer[]=any&category_730_StickerCapsule[]=any&category_730_TournamentTeam[]=any&category_730_Weapon[]=any&category_730_Type[]=tag_CSGO_Type_WeaponCase&norender=1', cookies=cookie)
    if(response.status_code == 200 and response.json()['success'] == 1 and len(response.json()['results']) > 0):
        item = response.json()['results'][0]
        return item
    else:
        raise ValueError('Error while getting item ' + market_hash_name + ' informations')

def searchItemOverview(market_hash_name):
    cookie = getAuthCookie()

    # https://steamcommunity.com/market/priceoverview/?country=EN&currency=3&appid=730&market_hash_name=Glove%20Case
    response = requests.get('https://steamcommunity.com/market/priceoverview/?country=EN&currency=3&appid=730&market_hash_name=' + market_hash_name, cookies=cookie)
    if(response.status_code == 200 and response.json()['success'] == 1):
        item = response.json()
        return item
    else:
        raise ValueError('Error while getting item ' + market_hash_name + ' overview')

def computeReleaseDate(pricehistory):
    return timestampToDatetime(list(pricehistory.keys())[0])

def computePrices(pricehistory):
    now = datetime.utcnow()

    Y5 = datetime(now.year - 5, now.month, now.day, 1, 0, 0).timestamp()
    Y3 = datetime(now.year - 3, now.month, now.day, 1, 0, 0).timestamp()
    Y2 = datetime(now.year - 2, now.month, now.day, 1, 0, 0).timestamp()
    Y1 = datetime(now.year - 1, now.month, now.day, 1, 0, 0).timestamp()
    M6 = datetime(now.year, now.month - 6, now.day, 1, 0, 0).timestamp()
    M3 = datetime(now.year, now.month - 3, now.day, 1, 0, 0).timestamp()
    M1 = datetime(now.year, now.month - 1, now.day, 1, 0, 0).timestamp()
    W1 = datetime(now.year, now.month, now.day - 7, 1, 0, 0).timestamp()

    Y5Key = nearest(pricehistory.keys(), Y5)
    Y3Key = nearest(pricehistory.keys(), Y3)
    Y2Key = nearest(pricehistory.keys(), Y2)
    Y1Key = nearest(pricehistory.keys(), Y1)
    M6Key = nearest(pricehistory.keys(), M6)
    M3Key = nearest(pricehistory.keys(), M3)
    M1Key = nearest(pricehistory.keys(), M1)
    W1Key = nearest(pricehistory.keys(), W1)
    nowKey = list(pricehistory.keys())[-1]

    Y5Price = pricehistory[Y5Key]
    Y3Price = pricehistory[Y3Key]
    Y2Price = pricehistory[Y2Key]
    Y1Price = pricehistory[Y1Key]
    M6Price = pricehistory[M6Key]
    M3Price = pricehistory[M3Key]
    M1Price = pricehistory[M1Key]
    W1Price = pricehistory[W1Key]
    nowPrice = pricehistory[nowKey]

    return { 'Y5': Y5Price, 'Y3': Y3Price, 'Y2': Y2Price, 'Y1': Y1Price, 'M6': M6Price, 'M3': M3Price, 'M1': M1Price, 'W1': W1Price, 'now': nowPrice }

def computeEarns(computedPrices):
    earnsY5 = (computedPrices['now'] - computedPrices['Y5']) / computedPrices['Y5']
    earnsY3 = (computedPrices['now'] - computedPrices['Y3']) / computedPrices['Y3']
    earnsY2 = (computedPrices['now'] - computedPrices['Y2']) / computedPrices['Y2']
    earnsY1 = (computedPrices['now'] - computedPrices['Y1']) / computedPrices['Y1']
    earnsM6 = (computedPrices['now'] - computedPrices['M6']) / computedPrices['M6']
    earnsM3 = (computedPrices['now'] - computedPrices['M3']) / computedPrices['M3']
    earnsM1 = (computedPrices['now'] - computedPrices['M1']) / computedPrices['M1']
    earnsW1 = (computedPrices['now'] - computedPrices['W1']) / computedPrices['W1']
    
    return { 'Y5': earnsY5, 'Y3': earnsY3, 'Y2': earnsY2, 'Y1': earnsY1, 'M6': earnsM6, 'M3': earnsM3, 'M1': earnsM1, 'W1': earnsW1 }

def computeMomentum(computedPrices):
    momentumY5 = computedPrices['now'] - computedPrices['Y5']
    momentumY3 = computedPrices['now'] - computedPrices['Y3']
    momentumY2 = computedPrices['now'] - computedPrices['Y2']
    momentumY1 = computedPrices['now'] - computedPrices['Y1']
    momentumM6 = computedPrices['now'] - computedPrices['M6']
    momentumM3 = computedPrices['now'] - computedPrices['M3']
    momentumM1 = computedPrices['now'] - computedPrices['M1']
    momentumW1 = computedPrices['now'] - computedPrices['W1']

    average = (momentumY5 + momentumY3 + momentumY2 + momentumY1 + momentumM6 + momentumM3 + momentumM1 + momentumW1) / 9
    
    return { 'Y5': momentumY5, 'Y3': momentumY3, 'Y2': momentumY2, 'Y1': momentumY1, 'M6': momentumM6, 'M3': momentumM3, 'M1': momentumM1, 'W1': momentumW1, 'average': average }

def computeMomentumAtADate(pricehistory, date, windowSize = 10):
    dateKey = nearest(pricehistory.keys(), date.timestamp())
    previousDay = date - timedelta(days=windowSize)
    previousDayKey = nearest(pricehistory.keys(), previousDay.timestamp())
    return pricehistory[dateKey] - pricehistory[previousDayKey]

def computeMomentumHistory1Y(pricehistory):
    now = datetime.utcnow()
    now = datetime(now.year, now.month, now.day, 1, 0, 0)

    nowKey = list(pricehistory.keys())[-1]

    output = {}

    for i in range(0, 365):
        day = now - timedelta(days=i)
        dayKey = nearest(pricehistory.keys(), day.timestamp())
        output[dayKey] = computeMomentumAtADate(pricehistory, day)

    return output

def main():
    with open('items_raw.json') as jsonFile:
        items = json.load(jsonFile)
        jsonFile.close()

    for item in items:
        try:
            marketHashName = item['market_hash_name']

            itemInfos = searchItem(marketHashName)
            itemOverview = searchItemOverview(marketHashName)
            pricehistory = requestPriceHistory(marketHashName)
            computedPrices = computePrices(pricehistory)

            item['volume'] = int(itemOverview['volume'].replace(',', ''))
            item['sell_listings'] = int(itemInfos['sell_listings'])
            item['ratio_sell_volume'] = item['volume'] / item['sell_listings']
            item['release_date'] = computeReleaseDate(pricehistory)
            item['price'] = computedPrices
            item['price_history'] = timestampToDatetimeDict(pricehistory)
            item['earns'] = computeEarns(computedPrices)
            item['momentum'] = computeMomentum(computedPrices)
            item['momentum_history_1y'] = timestampToDatetimeDict(computeMomentumHistory1Y(pricehistory))

            print('The price of the ' + item['market_hash_name'] + ': ' + str(item['price']['now']) + '$')
        except Exception as e:
            print("Error with item: " + item['market_hash_name'] + '. Error: ' + str(e))

        time.sleep(3) # To avoid being banned for too many requests

    with open('items_results.json', 'w') as outJsonFile:
        json.dump(items, outJsonFile, indent=4)
        outJsonFile.close()

if __name__ == "__main__":
    main()
