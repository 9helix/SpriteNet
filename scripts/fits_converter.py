from astropy.io import fits
import os
from PIL import Image

"""
Python script for converting FITS files into PNGs by extracting the detection only image by subtracting maxpixel and average pixel images.
"""


def fits_to_png(filename, new_folder, detection_only):
    if ".bin" in filename:
        with open(os.path.join(folder, filename), "rb") as fid:
            # TODO
            return

    print("Converting:", filename, end=" -> ")
    if os.path.isfile(os.path.join(new_folder, filename + ".png")):
        print("Already exists.")
        return
    try:
        with fits.open(os.path.join(folder, filename)) as hdul:
            try:
                maxpix = hdul[1].data
                avgpix = hdul[3].data
            except TypeError:
                print("Possibly corrupted FITS file.")
                return
            if detection_only:
                detection = maxpix - avgpix
            else:
                detection = maxpix
            im = Image.fromarray(detection)
            im.save(os.path.join(new_folder, filename + ".png"))
            converted += 1
            print("Success!")
    except OSError:
        print("Not a FITS file.")


def folder_walker(folder, detection_only=True):
    converted = 0
    if not os.path.exists(folder):
        return None
    new_folder = os.path.join(folder, "converted")
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)
    for filename in os.listdir(folder):
        fits_to_png(filename, new_folder, detection_only)
    return converted


if __name__ == "__main__":
    while True:
        folder = input("Enter folder: ")
        converted = folder_walker(folder)
        if converted is None:
            print("Folder does not exist.\n")
            continue
        print(f"\nDone! Converted {converted} FITS files.\n")
