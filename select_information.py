import pymongo


def get_house_information(dictionary):

    client = pymongo.MongoClient(host='localhost', port=27017) 
    db = client['House']
    information = db.todo.find(dictionary)

    return information
    
        
    
