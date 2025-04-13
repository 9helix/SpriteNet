import glob
from roboflow import Roboflow
from dotenv import load_dotenv
import os

"""
Script used for uploading images with their annotations to roboflow.
"""

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('API_KEY')
# Initialize Roboflow client
rf = Roboflow(api_key=api_key)

# Directory path and file extension for images
dir_name = "/mnt/1tb/Documents/Astronomija/GMN/dev/SpriteNet/raw_data/converted/"
file_extension_type = ".png"

# Annotation file path and format (e.g., .coco.json)
data_folder="/mnt/1tb/Documents/Astronomija/GMN/dev/SpriteNet/roboflow/spritenet-maxpixel-7"
# Get the upload project from Roboflow workspace
project = rf.workspace().project("spritenet")

# Upload images
ct=0
image_glob = glob.glob(dir_name + '/*' + file_extension_type)
for image_path in image_glob:
    subfolders = ["test/labels", "train/labels", "valid/labels"]
    found=False
    for subfolder in subfolders:
        subfolder_files = os.listdir(os.path.join(data_folder, subfolder))
        # print(subfolder_files)
        for file in subfolder_files:
            if file.find("fits_") != -1 and os.path.basename(image_path).startswith(file[: file.find("fits_")-1]):
                annotation_filename=os.path.join(data_folder, subfolder,file)
                print("Annotation filename:", annotation_filename)

                if os.stat(annotation_filename).st_size == 0:
                    print(project.single_upload(
                        image_path=image_path,))
                else:
                    print(project.single_upload(
                        image_path=image_path,
                        annotation_path=annotation_filename,
                        annotation_labelmap="/mnt/1tb/Documents/Astronomija/GMN/dev/SpriteNet/roboflow/spritenet-maxpixel-7/data.yaml"
                ))
                print("Uploaded image:", image_path)
                found=True
                ct+=1
                break
        if found:
            break
print(ct)