import json
import traceback
import matplotlib.pylab as plt

item_id = 0

try:
    with open('items_results.json') as jsonFile:
        items = json.load(jsonFile)
        jsonFile.close()

        momentum_history_1y = items[item_id]['momentum_history_1y']

        lists = sorted(momentum_history_1y.items()) # sorted by key, return a list of tuples

        x, y = zip(*lists) # unpack a list of pairs into two tuples

        plt.xlabel('Date', fontsize = 11, color = 'blue')
        plt.ylabel('Momentum', fontsize = 11, color = 'blue')
        plt.title(label= items[item_id]["market_hash_name"] + " momentum chart", fontsize=15, color="green")
        plt.axhline(y=0, color='r', linestyle='-')
        plt.plot(x, y)
        plt.show()
except Exception as e:
    print(e)
    traceback.print_exc()