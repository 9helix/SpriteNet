import os
from astropy.io import fits
from PIL import Image

"""
Replaces detection images in the provided dataset with maxpixel images from the original FITS files.
"""


def find_file_with_string(folder, search_string):
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(folder):
        for file in files:
            pairs[file] = os.path.join(root, file)
            if search_string == file:
                return os.path.join(root, file)
    return None


pairs = {}
dataset_folder = input("Enter folder path: ")
subfolders = ["test/images", "train/images", "valid/images"]
sprites = r"D:\Documents\Astronomija\GMN\dev\SpriteNet\sprites"
for subfolder in subfolders:
    for file in os.listdir(os.path.join(dataset_folder, subfolder)):
        ff_file = file[: file.find("_png")]
        ff_file = ff_file.replace("-", ".")
        if ff_file in pairs:
            file_path = pairs[ff_file]
        else:
            file_path = find_file_with_string(sprites, ff_file)
            if not file_path:
                raise FileNotFoundError(f"File {ff_file} not found in {subfolder}")

        print("Converting:", ff_file, end=" -> ")

        try:
            with fits.open(file_path) as hdul:
                try:
                    maxpix = hdul[1].data
                except TypeError:
                    print("Possibly corrupted FITS file.")

                im = Image.fromarray(maxpix)

                im_resized = im.resize((320, 320))
                im_gray = im_resized.convert("L")

                im_gray.save(
                    os.path.join(os.path.join(dataset_folder, subfolder), file)
                )
                print("Success!")
        except OSError:
            print("Not a FITS file.")
