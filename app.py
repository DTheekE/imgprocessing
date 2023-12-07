import streamlit as st
from PIL import Image
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, storage
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from keras.models import load_model
import requests
from bs4 import BeautifulSoup

# Initialize Firebase (replace 'path/to/your/credentials.json' with the path to your Firebase credentials file)
cred = credentials.Certificate("/workspaces/imgprocessing/credentials.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'your-firebase-app-id.appspot.com'})

# Load Keras model
model = load_model('FV.h5')

labels = {
    0: 'apple', 1: 'banana', 2: 'beetroot', 3: 'bell pepper', 4: 'cabbage', 5: 'capsicum', 6: 'carrot',
    7: 'cauliflower', 8: 'chilli pepper', 9: 'corn', 10: 'cucumber', 11: 'eggplant', 12: 'garlic', 13: 'ginger',
    14: 'grapes', 15: 'jalepeno', 16: 'kiwi', 17: 'lemon', 18: 'lettuce',
    19: 'mango', 20: 'onion', 21: 'orange', 22: 'paprika', 23: 'pear', 24: 'peas', 25: 'pineapple',
    26: 'pomegranate', 27: 'potato', 28: 'raddish', 29: 'soy beans', 30: 'spinach', 31: 'sweetcorn',
    32: 'sweetpotato', 33: 'tomato', 34: 'turnip', 35: 'watermelon'
}

fruits = ['Apple', 'Banana', 'Bell Pepper', 'Chilli Pepper', 'Grapes', 'Jalepeno', 'Kiwi', 'Lemon', 'Mango', 'Orange',
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
    img = load_img(img_path, target_size=(224, 224, 3))
    img = img_to_array(img)
    img = img / 255
    img = np.expand_dims(img, [0])
    answer = model.predict(img)
    y_class = answer.argmax(axis=-1)
    print(y_class)
    y = " ".join(str(x) for x in y_class)
    y = int(y)
    res = labels[y]
    print(res)
    return res.capitalize()

def download_image_from_firebase(image_name):
    bucket = storage.bucket()
    blob = bucket.blob('images/' + image_name)
    image_content = blob.download_as_text()
    return Image.open(BytesIO(image_content)).resize((250, 250))

def run():
    st.title("Stay-Fit ImgProcessing BackEnd")
    image_name = st.text_input("Enter Image Name in Firebase Storage:")
    
    if image_name:
        try:
            img = download_image_from_firebase(image_name)
            st.image(img, use_column_width=False)

            # Save the image locally (optional)
            save_image_path = './downloaded_images/' + image_name
            img.save(save_image_path)

            result = processed_img(save_image_path)

            if result in vegetables:
                st.info('**Category: Vegetables**')
            else:
                st.info('**Category: Fruit**')

            st.success("**Predicted: " + result + '**')

            cal = fetch_calories(result)
            if cal:
                st.warning('**' + cal + '(100 grams)**')

        except Exception as e:
            st.error(f"Error: {e}")

run()
