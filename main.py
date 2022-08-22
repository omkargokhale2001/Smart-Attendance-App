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

load_dotenv()

app = Flask(__name__)


# @app.route('/')
# def hello_world():
#     return 'Hello World'


@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        grp_image = request.form['grp_image']
        # grp_image = cv2.imread("./test_data/Group Photo (1).png")
        grp_image = np.array(grp_image)
        CONNECTION_STRING = os.getenv("MONGO_URL")
        # CONNECTION_STRING = "mongodb+srv://omkar:omkar1212@cluster1.2melkie.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Workers"]
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

    return attendance_list


@app.route('/display_percentage', methods=['GET', 'POST'])
def display_percentage():
    if request.method == 'GET':
        CONNECTION_STRING = os.getenv("MONGO_URL")
        # CONNECTION_STRING = "mongodb+srv://omkar:omkar1212@cluster1.2melkie.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Workers"]

        data = list(users.find({},
                               {
            "name": 1,
            "days_present": 1,
            "total_days": 1,
        }
        ))

        res = []
        percentage_dict = {}
        for w in data:
            percentage_dict[w['name']] = (w['days_present'] / w['total_days']) * 100

        return percentage_dict


@app.route("/add_worker")
def add_worker():
    if request.method == "POST":
        name = request.form['name']
        image = request.form['image']
        embeds = convert_image(image)

        # image1 = cv2.imread("./test_data/Image_10.png")
        # image1 = np.array(image1)
        # print(image1)
        # print(type(image1))
        # print(type(image1[0]))
        # embeds = convert_image(image1)
        # print(len(embeds))

        # Code for adding worker to db
        CONNECTION_STRING = os.getenv("MONGO_URL")
        # CONNECTION_STRING = "mongodb+srv://omkar:omkar1212@cluster1.2melkie.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Workers"]

        item_2 = {
            "name": name,
            "days_present": 0,
            "total_days": 0,
            # "face_embedding": request.form.get('face_embd'),
            "face_embedding": embeds,
        }
        users.insert_one(item_2)

        return "Worker added!"


@app.route("/delete_worker")
def delete_worker():
    # Code for deleting worker from db
    if request.method == "POST":
        name = request.form['name']
        CONNECTION_STRING = os.getenv("MONGO_URL")
        # CONNECTION_STRING = "mongodb+srv://omkar:omkar1212@cluster1.2melkie.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(CONNECTION_STRING)
        db_name = client["SIH_app_database"]
        users = db_name["Workers"]
        users.delete_one({"name": name})
        return "Worker deleted!"


# @app.route("/clear_days")
# def clear_days():
#     if request.method == "GET":
#         #CONNECTION_STRING = "mongodb+srv://syntaxico:{i2hhW_Z5@cluster0.fx786w6.mongodb.net/?retryWrites=true&w=majority"
#         CONNECTION_STRING = "mongodb+srv://omkar:omkar1212@cluster1.2melkie.mongodb.net/?retryWrites=true&w=majority"
#         client = MongoClient(CONNECTION_STRING)
#         db_name = client["SIH_app_database"]
#         users = db_name["Workers"]
#
#         users.update_many({},
#                           {"$set": {"days_present": 0, "total_days": 0}}
#                           )
#         return "days cleared!"


if __name__ == '__main__':
    app.run()
