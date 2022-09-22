import json
import requests
from datetime import datetime

def extractMarktHashNames(item):
    return { 'market_hash_name': item['asset_description']['market_hash_name'] }

def filterTradableCommodity(item):
    return item['asset_description']['tradable'] == 1 and item['asset_description']['commodity'] == 1

def requestRawItemsEndpoint():
    with open('cookie.txt') as cookieFile:
        cookie = {
            'steamLoginSecure': cookieFile.read()
        }

        cookieFile.close()

        response = requests.get('https://steamcommunity.com/market/search/render/?query=Case&start=0&count=5000&search_descriptions=0&sort_column=default&sort_dir=desc&appid=730&category_730_ItemSet[]=any&category_730_ProPlayer[]=any&category_730_StickerCapsule[]=any&category_730_TournamentTeam[]=any&category_730_Weapon[]=any&category_730_Type[]=tag_CSGO_Type_WeaponCase&norender=1', cookies=cookie)
        if(response.status_code == 200):
            items = response.json()['results']
            items = list(filter(filterTradableCommodity, items))
            marketHashNames = list(map(extractMarktHashNames, items))
            return marketHashNames
        else:
            raise ValueError('Error while getting items')

def main():
    items = requestRawItemsEndpoint()

    with open('items_raw.json', 'w') as outJsonFile:
        json.dump(items, outJsonFile, indent=4)
        outJsonFile.close()

if __name__ == "__main__":
    main()
