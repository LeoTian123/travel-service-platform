from graph import *
import pickle

with open(f'graphMaps\\000001.pickle', 'rb') as f:
    g = pickle.load(f)

print(g)