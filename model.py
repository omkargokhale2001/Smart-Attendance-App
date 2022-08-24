import pandas as pd
from deepface import DeepFace
import os
import face_recognition
import numpy as np



def detect_faces(grp_img):
    face_locations = face_recognition.face_locations(grp_img)
    images_array = []
    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_array = grp_img[top-100:bottom+100, left-100:right+100]
        images_array.append(face_array)
    return images_array

def convert_image(image):
    result = DeepFace.represent(img_path=image, model_name="Facenet", enforce_detection=False)
    return result


def find_embeds(image_arr):
    embed_arr = []
    for i in range(len(image_arr)):
        result = DeepFace.represent(img_path=image_arr[i], model_name="Facenet", enforce_detection=False)
        embed_arr.append(result)
    return embed_arr


def collect_embeds(cur):
    names = []
    face_embeds = []
    for i in cur:
        names.append(i['name'])
        face_embeds.append(i['face_embedding'])
    db_dict = dict(zip(names, face_embeds))
    return db_dict


def is_same_person(img1, img2):
    em1 = np.array(img1)
    em2 = np.array(img2)
    a = np.matmul(np.transpose(em1), em2)
    b = np.sum(np.multiply(em1, em1))
    c = np.sum(np.multiply(em2, em2))
    score = 1 - (a / (np.sqrt(b) * np.sqrt(c)))
    return score


def wrapper(grp_img, cur):
    img_arr = detect_faces(grp_img)
    embeds_arr = find_embeds(img_arr)
    db_dict = collect_embeds(cur)
    attendance = []
    db_dict_1 = sorted(db_dict)
    db_dict = {key:db_dict[key] for key in db_dict_1}
    names = list(db_dict.keys())
    embeds = list(db_dict.values())
    scores = []
    for i in range(len(embeds_arr)):
        temp_arr = []
        for j in embeds:
            score = is_same_person(embeds_arr[i],j)
            temp_arr.append(score)
        scores.append(temp_arr)
        print(temp_arr)
        min_ind = np.argmin(temp_arr)
        attendance.append(names[min_ind])
    return attendance

