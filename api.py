from flask import Flask, render_template, redirect, url_for, request
from flask_restful import Resource, Api, reqparse
import pymongo
import json
import select_information

client = pymongo.MongoClient(host='localhost', port=27017) 
db = client['House']

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1> Hello, World! <h1>"

@app.route('/home')
def home():
    return render_template('home.html')
  

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    house_result = dict()
    info = list()
    keywords = ['city', 'rule', 'phone', 'isrole', 'principalsex', 'lastname']
    if request.method == "GET":
        req_dict = dict()
        for item in keywords:
            if request.args.get(item):
                req_dict[item] = request.args.get(item)
            
        response = select_information.get_house_information(req_dict)
        for index, item in enumerate(response):
            info.append(item)
        
        house_result["info"] = info
        json.dumps(house_result)
        return house_result
    

if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.run(port=5000, debug=True)