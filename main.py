import os
from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from os import environ
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import pymongo
from model import *
from werkzeug.utils import secure_filename
import geocoder
from gevent.pywsgi import WSGIServer

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World Omkar'


@app.route('/upload', methods=['GET','POST'])
def mark_attendance():
    print("flag")
    if request.method == 'POST':
        print("Flag2")
        grp_image = request.files['image']
        # grp_image = cv2.imread("./test_data/Group Photo (1).png")
        img_file_name = 'grp_img.png'
        grp_image.save(secure_filename(img_file_name))
        grp_image = cv2.imread(img_file_name)
        # grp_image = cv2.cvtColor(grp_image, cv2.COLOR_RGB2BGR)
        # embeds = convert_image(image)
        grp_image = np.array(grp_image)
        CONNECTION_STRING = os.getenv("MONGO_URL")
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Labourers"]
        info_cur = list(users.find({}, {
            "name": 1,
            "face_embedding": 1
        }))

        attendance_list = list(set(wrapper(grp_image, info_cur)))

        for worker in attendance_list:
            users.update_one({"name": str(worker)},
                             {
                "$inc": {"days_present": 1}
            })

        users.update_many({}, {
            "$inc": {"total_days": 1}
        })
        # optional -> if to < 30/getMonth:total_day = 0
    attendance_list = str(attendance_list)
    return {"msg": attendance_list}

@app.route('/display_percentage', methods=['GET', 'POST'])
def display_percentage():
    if request.method == 'GET':
        CONNECTION_STRING = os.getenv("MONGO_URL")
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Labourers"]

        data = list(users.find({},
                               {
            "name": 1,
            "days_present": 1,
            "total_days": 1,
            "age":1,
            "gender":1,
            "aadhar_number":1,
        }
        ))
        res = {"msg": "Success", "result": []}
        for w in data:
            if w['total_days'] !=0:
                percent = round((w['days_present']/w['total_days'])*100, 2)
            else:
                percent = 0
            name = w['name']
            age = w['age']
            aadhar = w['aadhar_number']
            gender = w['gender']
            res['result'].append({"name": name, "percent": percent, "age": age, "aadhar_number": aadhar,"gender":gender})
        return res



@app.route("/add_test_data")
def add_test_data():
    if request.method == "GET":
        print(os.listdir(os.getcwd() + "\\test_data"))
        for img in os.listdir(os.getcwd() + "\\test_data"):
            if img != "group_photo.jpg":
                add_test(img)

    return "test data added"

def add_test(imgname):
        name = imgname.split(".")[0]
        image = cv2.imread('./test_data/' + imgname)
        embeds = convert_image(image)

        # Code for adding worker to db
        CONNECTION_STRING = os.getenv("MONGO_URL")
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Labourers"]

        item_2 = {
            "name": name,
            "days_present": 0,
            "total_days": 0,
            # "face_embedding": request.form.get('face_embd'),
            "face_embedding": embeds,
        }
        users.insert_one(item_2)


@app.route("/add_worker", methods=['GET', 'POST'])
def add_worker():
    print("flag")
    if request.method == "POST":
        name = request.form['name']
        age = request.form['age']
        card_number = request.form['card_number']
        gender = request.form['gender']
        image = request.files['image']

        print("Flag1.1")
        # name = "Bansi"
        img_file_name = 'new_add.png'
        image.save(secure_filename(img_file_name))
        image = cv2.imread(img_file_name)
        embeds = convert_image(image)
        print("flag1")
        # image1 = cv2.imread("./test_data/Image_10.png")
        # image1 = np.array(image1)
        # print(image1)
        # print(type(image1))
        # print(type(image1[0]))
        # embeds = convert_image(image1)
        # print(len(embeds))

        # Code for adding worker to db
        CONNECTION_STRING = os.getenv("MONGO_URL")
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Labourers"]

        item_2 = {
            "name": name,
            "age": age,
            "gender":gender,
            "aadhar_number":card_number,
            "days_present": 0,
            "total_days": 0,
            "face_embedding": embeds,
        }
        users.insert_one(item_2)
        print("flag2")
        return {"msg":"Successs"}
    if request.method == "GET":
        return render_template("register_emp.html")


@app.route("/delete_worker")
def delete_worker():
    # Code for deleting worker from db
    if request.method == "POST":
        name = request.form['name']
        CONNECTION_STRING = os.getenv("MONGO_URL")
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Labourers"]
        users.delete_one({"name": name})
        return "Worker deleted!"

@app.route('/test')
def sayhello():
    if request.method=='POST':
        name = request.form['name']
        return name
    else:
        return "HELLO"


def main():
    print("done")
    app.run(host='<IP>', port=5000, debug=True, threaded=False)


if __name__ == '__main__':
    main()
