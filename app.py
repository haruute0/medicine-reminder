from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps, loads
import time
from datetime import datetime, timedelta
from pytz import timezone

import json, random, string
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db as fdb

cred = credentials.Certificate('medicine-reminder-947cb-firebase-adminsdk-05dsp-aaed29d4a9.json')
tz = timezone('Asia/Jakarta')
app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://medicine-reminder-947cb.firebaseio.com/'
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
