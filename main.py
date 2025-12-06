from os import path
from time import sleep

import pandas as pd
import matplotlib.pyplot as plt
from numpy import array, argsort

import webscrape

dirname = "data"

filename = dirname + "/homegate.csv"

if not path.isfile(filename):
    w = webscrape.WebScrape(None, None)
    w.write_data(start_page=1, end_page=51, timeout=7, path=filename, show=True)

prices = pd.read_csv(filename, usecols=["price"]).values
rooms = pd.read_csv(filename, usecols=["rooms"]).values
meters = pd.read_csv(filename, usecols=["meters"]).values
addresses = pd.read_csv(filename, usecols=["address"]).values

dist_file = dirname + "/distances.csv"

if not path.isfile(dist_file):
    w = webscrape.WebScrape(None, None)
    w.write_distances(addresses, path=dist_file, timeout=1.1, show=True)

distances = pd.read_csv(dist_file, usecols=["distance"]).values

def price_meters_graph():
    plt.title("Apartments from homegate.ch")
    plt.xlabel("Square meters (m^2)")
    plt.ylabel("Price (CHF)")

    plt.scatter(meters, prices)
    plt.show()

def price_dist_graph():
    plt.title("Apartments from homegate.ch")
    plt.xlabel("Distance from ETH (km)")
    plt.ylabel("Price (CHF)")

    plt.scatter(distances, prices)
    plt.show()


def loss(p, weights, dist=True):
    if p[0] != 0.0 and p[1] != 0.0 and p[2] != 0.0:
        if dist:
            return (p[0] * weights[0] / (p[1] * weights[1])) + (p[3] * weights[2] /  (p[2] * weights[3]))
        else:
            return (p[0] * weights[0] / (p[1] * weights[1] /  p[2] * weights[3]))
    return 10.0

limit_price = 4000
limit_rooms = 0.0

lst_prices = []
lst_meters = []
lst_rooms = []
lst_distances = []

targets = []
for i in range(len(prices)):
    if prices[i] <= limit_price and rooms[i] >= limit_rooms:
        targets.append([prices[i], meters[i], rooms[i], addresses[i], distances[i]])

        lst_prices.append(prices[i][0])
        lst_meters.append(meters[i][0])
        lst_rooms.append(rooms[i][0])
        lst_distances.append(distances[i][0])

max_price = max(lst_prices)
max_meter = max(lst_meters)
max_room = max(lst_rooms)
max_distance = max(lst_distances)

# price, meters, rooms, distance
# weights = [0.4, 0.7, 0.9, 0.4]
weights = [1, 1, 1, 1]

scores = []
for i in range(len(targets)):
    params = []
    params.append(float(lst_prices[i]) / float(max_price))
    params.append(float(lst_meters[i]) / float(max_meter))
    params.append(float(lst_rooms[i]) / float(max_room))
    params.append(float(lst_distances[i]) / float(max_distance))

    score = loss(params, weights, dist=False)
    scores.append(score)

np_scores = array(scores)
sorted_indices = np_scores.argsort()
sorted_scores = np_scores[sorted_indices]

for i in range(10):
    best_apartment = targets[sorted_indices[i]]
    print("Score:", round(sorted_scores[i], 2), best_apartment[0][0], best_apartment[1][0], best_apartment[2][0], best_apartment[3][0], best_apartment[4][0])

print("Average price:", int(sum(lst_prices) / len(lst_prices)))
