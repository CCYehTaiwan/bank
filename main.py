import os
from house import *
import pymongo
import time

client = pymongo.MongoClient(host='localhost', port=27017) 
db = client['House']

mycol = db['todo']

house_information = House()
for area in ["1", "3"]:
    _, info = house_information.search(filter_params={"region":area, "kind":'0'})
    mycol.insert_many(info)

# mycol.delete_many({"city": "3"})
"""
if __name__ == "__main__":
    house = House()
    _, _, information = house.search()
    print(information)
"""