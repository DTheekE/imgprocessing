import firebase_admin
from firebase_admin import credentials, storage
import os
print("Current working directory:", os.getcwd())

# Initialize Firebase with your own credentials JSON file
cred = credentials.Certificate("credentials.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'storageBucket': 'stayfit-efe50.appspot.com'}, name='stayfit')

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
