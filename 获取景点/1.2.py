import pickle

with open('data.pickle', 'rb') as f:
    data = pickle.load(f)

with open('data31-100.pickle', 'rb') as f:
    data2 = pickle.load(f)

data+=data2

# name = [x[0] for x in data if x[0]]

print(data)
print(len(data))