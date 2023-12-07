import firebase_admin
from firebase_admin import credentials, storage
import os
print("Current working directory:", os.getcwd())

# Initialize Firebase with your own credentials JSON file
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'stayfit-efe50.appspot.com'})

def download_image(image_name, destination_path):
    try:
        # Get a reference to the Firebase Storage bucket
        bucket = storage.bucket()

        # Specify the path to the image in the storage bucket
        image_path = f"images/{image_name}"

        # Check if the image exists
        blob = bucket.blob(image_path)
        if blob.exists():
            # Download the image to the specified destination path
            blob.download_to_filename(destination_path)
            return True
        else:
            return False

    except Exception as e:
        return f"Error: {str(e)}"


# Example usage
image_name_to_download = "img.jpg"
destination_path_to_save = "saved/img.jpg"

if download_image(image_name_to_download, destination_path_to_save):
    print(f"Image downloaded successfully to {destination_path_to_save}")
else:
    print(f"Image {image_name_to_download} does not exist in Firebase Storage.")
