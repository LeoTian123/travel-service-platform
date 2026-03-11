import pickle
import os
import random
from datetime import datetime, timedelta

with open('../Media/journals/main-data.pickle', 'rb') as f:
    data = pickle.load(f)

# del data[-3]

print(data)

# with open('../Media/journals/main-data.pickle', 'wb') as f:
#     pickle.dump(data, f)