from astropy.io import fits
import os
from PIL import Image
import numpy as np

"""
Python script for converting FITS files into PNGs by extracting the detection only image by subtracting maxpixel and average pixel images.
"""

while True:
    converted=0
    folder = input("Enter folder: ")
    if not os.path.exists(folder):
        print("Folder does not exist!")
        exit()
    new_folder = os.path.join(folder, "converted")
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)
    for filename in os.listdir(folder):
        if ".bin" in filename:
            with open(os.path.join(folder, filename), "rb") as fid:
                # TODO
                continue

        print("Converting:", filename, end=" -> ")
        if os.path.isfile(os.path.join(new_folder, filename + ".png")):
            print("Already exists.")
            continue
        try:
            hdul = fits.open(os.path.join(folder, filename))
        except OSError:
            print("Not a FITS file.")
            continue

        try:
            maxpix = hdul[1].data
            avgpix = hdul[3].data
        except TypeError:
            print("Possibly corrupted FITS file.")
            continue

        detection = maxpix - avgpix

        im = Image.fromarray(detection)
        im.save(os.path.join(new_folder, filename + ".png"))
        hdul.close()
        converted+=1
        print("Success!")

    print(f"\nDone! Converted {converted} FITS files.\n")
