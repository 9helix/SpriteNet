from astropy.io import fits
import os
from PIL import Image

"""
Python script for converting FITS files into PNGs by extracting the detection only image by subtracting maxpixel and average pixel images.
"""


def fits_to_png(filename, new_folder, detection_only, root):
    if ".bin" in filename:
        with open(os.path.join(root, filename), "rb") as fid:
            # TODO
            return 0
    if filename.endswith(".fits") == False:
        return 0
    print("Converting:", filename, end=" -> ")
    if os.path.isfile(os.path.join(new_folder, filename + ".png")):
        print("Already exists.")
        return 0
    try:
        with fits.open(os.path.join(root, filename)) as hdul:
            try:
                maxpix = hdul[1].data
                avgpix = hdul[3].data
            except TypeError:
                print("Possibly corrupted FITS file.")
                return 0
            if detection_only:
                detection = maxpix - avgpix
            else:
                detection = maxpix
            im = Image.fromarray(detection)
            im.save(os.path.join(new_folder, filename + ".png"))
            print("Success!")
            return 1
    except OSError:
        print("Not a FITS file.")
        return 0


def folder_walker(folder, detection_only=True):
    converted = 0
    if not os.path.exists(folder):
        return None
    new_folder = os.path.join(folder, "converted")
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)
    for root, dirs, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[0] in acquired_files and file.endswith(".fits"):
                if fits_to_png(file, new_folder, detection_only, root):
                    converted += 1
                    existing_files.add(os.path.splitext(file)[0])

    return converted


existing_files = set()
newest_files = set()

data_folder = "roboflow/SpriteNet-5"  # input("Enter dataset folder: ")
data_folder2 = "roboflow/spritenet-maxpixel-6"  # input("Enter dataset folder from which to copy files: ")


folder = r"/mnt/1tb/Documents/Astronomija/GMN/dev/SpriteNet/raw_data/"
detect = input("Detection only? y/N ")
subfolders = ["test/images", "train/images", "valid/images"]
for subfolder in subfolders:
    subfolder_files = os.listdir(os.path.join(data_folder, subfolder))
    # print(subfolder_files)
    for file in subfolder_files:
        if file.find("-fits") != -1:
            file_name = file[: file.find("-fits")]
            existing_files.add(file_name)

for subfolder in subfolders:

    subfolder_files = os.listdir(os.path.join(data_folder2, subfolder))
    # print(subfolder_files)
    for file in subfolder_files:
        if file.find("-fits") != -1 and not file.endswith(".npy"):

            file_name = file[: file.find("-fits")]
            newest_files.add(file_name)

acquired_files = newest_files - existing_files
print(len(newest_files), len(existing_files), len(acquired_files))
print(newest_files)
converted = folder_walker(folder, True if detect.lower() == "y" else False)

if converted is None:
    print("Folder does not exist.\n")
    exit()
print(f"\nDone! Converted {converted} FITS files.\n")
