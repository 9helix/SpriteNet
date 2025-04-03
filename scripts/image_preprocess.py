from PIL import Image
import os

folder = input("Enter the location of the image folder: ")

OUT_FOLDER = "resized2"
os.makedirs(os.path.join(folder, OUT_FOLDER), exist_ok=True)
IMG_SIZE = (640, 640)
for i in os.listdir(folder):
    i = os.path.join(folder, i)
    if os.path.isfile(i):
        img = Image.open(i)
        if img.mode != "L":
            img = img.convert("L")
        img = img.resize(IMG_SIZE)
        img.save(os.path.join(folder, OUT_FOLDER, os.path.basename(i)))
