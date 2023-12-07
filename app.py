import csv
import dbm
import os
import streamlit as st
from PIL import Image
from keras.preprocessing.image import img_to_array
import numpy as np
from keras.models import load_model
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, storage,  initialize_app

# Initialize Firebase with your own credentials JSON file
cred = credentials.Certificate("credentials.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'storageBucket': 'stayfit-efe50.appspot.com'}, name='stayfit')


from hwrd import download_image

from hwrd import download_image

image_name_to_download = "img.jpg"
destination_path_to_save = "saved/img.jpg"

if download_image(image_name_to_download, destination_path_to_save):
    print(f"Image downloaded successfully to {destination_path_to_save}")
else:
    print(f"Image {image_name_to_download} does not exist in Firebase Storage.")


model = load_model('FV.h5')
labels = {0: 'apple', 1: 'banana', 2: 'beetroot', 3: 'bell pepper', 4: 'cabbage', 5: 'capsicum', 6: 'carrot',
          7: 'cauliflower', 8: 'chilli pepper', 9: 'corn', 10: 'cucumber', 11: 'eggplant', 12: 'garlic', 13: 'ginger',
          14: 'grapes', 15: 'jalepeno', 16: 'kiwi', 17: 'lemon', 18: 'lettuce',
          19: 'mango', 20: 'onion', 21: 'orange', 22: 'paprika', 23: 'pear', 24: 'peas', 25: 'pineapple',
          26: 'pomegranate', 27: 'potato', 28: 'raddish', 29: 'soy beans', 30: 'spinach', 31: 'sweetcorn',
          32: 'sweetpotato', 33: 'tomato', 34: 'turnip', 35: 'watermelon'}

fruits = ['Apple', 'Banana', 'Bello Pepper', 'Chilli Pepper', 'Grapes', 'Jalepeno', 'Kiwi', 'Lemon', 'Mango', 'Orange',
          'Paprika', 'Pear', 'Pineapple', 'Pomegranate', 'Watermelon']
vegetables = ['Beetroot', 'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Corn', 'Cucumber', 'Eggplant', 'Ginger',
              'Lettuce', 'Onion', 'Peas', 'Potato', 'Raddish', 'Soy Beans', 'Spinach', 'Sweetcorn', 'Sweetpotato',
              'Tomato', 'Turnip']

def fetch_calories(prediction):
    
    try:
        url = 'https://www.google.com/search?&q=calories in ' + prediction
        req = requests.get(url).text
        scrap = BeautifulSoup(req, 'html.parser')
        calories = scrap.find("div", class_="BNeawe iBp4i AP7Wnd").text
        return calories
    except Exception as e:
        st.error("Can't able to fetch the Calories")
        print(e)

def processed_img(img_path):
    try:
        # Open the image using PIL
        with Image.open(img_path) as img:
            img = img.resize((224, 224))
            img_array = img_to_array(img)
            img_array = img_array / 255.0  # Normalize the image
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            answer = model.predict(img_array)
            y_class = answer.argmax(axis=-1)
            print(y_class)
            y = int(y_class[0])
            res = labels[y]
            print(res)
            return res.capitalize()

    except Exception as e:
        st.error("Error processing image")
        print(e)
        return None
def write_to_csv(csv_file_path, data):
    try:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["result", "calories"])
            writer.writeheader()
            writer.writerow(data)
    except Exception as e:
        st.error(f"Error writing to CSV file: {str(e)}")

def upload_csv_to_storage(csv_file_path):
    try:
        # Get a reference to the Firebase Storage bucket
        bucket = storage.bucket()

        # Specify the path to the CSV file in the storage bucket
        storage_path = f"results/{os.path.basename(csv_file_path)}"

        # Upload the CSV file to Firebase Storage
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(csv_file_path)
        print(f"CSV file uploaded successfully to {storage_path}")
    except Exception as e:
        st.error(f"Error uploading CSV file to Firebase Storage: {str(e)}")    

def run():
    
    st.title("StayFit ImgProcessing Backend")
    
    img_file_path = "saved/img.jpg"

    result = processed_img(img_file_path)
    if result:
        st.info(f'**Category: {"Vegetable" if result in vegetables else "Fruit"}**')
        st.success(f'**Predicted: {result}**')
        cal = fetch_calories(result)
        if cal:
            st.warning(f'**{cal} (100 grams)**')

            # Write to CSV file
            csv_data = {"result": result, "calories": cal}
            csv_file_path = "results.csv"
            write_to_csv(csv_file_path, csv_data)

            # Upload CSV file to Firebase Storage
            upload_csv_to_storage(csv_file_path)
            

    st.image(img_file_path, use_column_width=False)

if __name__ == "__main__":
    run()
