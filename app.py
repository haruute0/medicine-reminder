from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps, loads
import time
from datetime import datetime, timedelta
from pytz import timezone

"""
    V1  MongoDB Based Database API
    V2  Google Firebase Based Database API
"""

import json, random, string
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db as fdb

import os

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

firebase_key = os.environ.get('FIREBASE_KEY', None)
database_url = os.environ.get('FIREBASE_DB_URL', None)

cred = credentials.Certificate(json.loads(firebase_key))
tz = timezone('Asia/Jakarta')
app = firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})

client = MongoClient('localhost:27017')
db = client['medicine_reminder']

app = Flask(__name__)

def generate_meds_id():
    letters = string.ascii_letters + "1234567890_-"
    return ''.join(random.choice(letters) for i in range(11))

@app.route("/")
def hello():
    return "Welcome to medicine reminder database API."

@app.route("/api/v2/medicines", methods=['POST'])
def add_firebase_medicine():
    try:
        data = json.loads(request.data)
        key = data['key']
        id = generate_meds_id()
        if key:
            post_data = {
                'id': id,
                'nama_obat': data['nama_obat'],
                'jenis_obat': data['jenis_obat'],
                'intensitas': data['intensitas'],
                'penggunaan': data['penggunaan'],
                'satuan': data['satuan'],
                'sesudah_makan': data['sesudah_makan'],
                'qty': data['qty'],
                'notes': data['notes'],
                'date_added': round(time.time()),
                'date_expired': round(time.time()) + (data['duration']*3600*24)
            }
            ref = fdb.reference("/medicines")
            user_data = ref.child(str(id))
            current = user_data.get()
            if current == None:
                user_data.set(post_data)
        return dumps({'message' : str(id)})
    except Exception as e:
        return dumps({'error' : str(e)})
    
@app.route("/api/v2/medicines", methods=['GET'])
def get_firebase_medicine():
    ref = fdb.reference("/medicines")
    return jsonify(ref.get())

@app.route("/api/v2/medicines/<id>", methods=['GET'])
def get_firebase_medicine_by_id(id):
    ref = fdb.reference("/medicines")
    user_data = ref.child(str(id))
    current = user_data.get()
    if current == None:
        json = {
            "error" : str(id) + " Not Found"
        }
        return jsonify(json)
    else:
        return jsonify(user_data.get())

"""
@app.route("/api/v2/medicines/<id>", methods=['GET'])
def get_firebase_medicine(id):
    ref = fdb.reference("/medicines")
    return jsonify(ref.equal_to(id))
"""

@app.route("/api/v1/medicines", methods=['POST'])
def add_medicine():
    try:
        data = json.loads(request.data)
        key = data['key']
        id = generate_meds_id()
        if key:
            db.medicines.insert_one({
                "id": id,
                "id_obat": data['id_obat'],
                "nama_obat": data['nama_obat'],
                "jenis_obat": data['jenis_obat'],
                "intensitas": data['intensitas'],
                "penggunaan": data['penggunaan'],
                "satuan": data['satuan'],
                "sesudah_makan": data['sesudah_makan'],
                "qty": data['qty'],
                "notes": data['notes'],
                "date_added": datetime.datetime.now(),
                "date_expired": datetime.datetime.now() + timedelta(days=data['duration'])
            })
        return dumps({'message' : str(id)})
    except Exception as e:
        return dumps({'error' : str(e)})

@app.route("/api/v1/medicines/<id>", methods=['GET'])
def get_medicine(id):
    result = db.medicines.find_one({
        "id": id
    })
    return jsonify(json.loads(dumps(result)))

@app.route("/api/v1/medicines", methods=['GET'])
def get_medicine_all():
    result = db.medicines.find({})
    return jsonify(json.loads(dumps(result)))

@app.route("/api/v1/medicines/<id>", methods=['DELETE'])
def delete_medicine(id):
    db.medicines.delete_one({
        "id": id
    })
    return dumps({'deleted' : str(id)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)