import numpy as np
from PIL import Image, ImageFont

"""
Script for separating thumbnails from a single image. Adapteed from the original made by Damir Šegon.
"""


def apply_vignetting(image2correct, vignetting_parameter):
    image2correct = np.array(image2correct)
    height, width = image2correct.shape
    cy, cx = height // 2, width // 2
    yy, xx = np.meshgrid(np.arange(height), np.arange(width))
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    r = r.T
    corrected_image_array = (
        (image2correct / np.cos(vignetting_parameter * r) ** 4)
        .clip(0, 255)
        .astype(np.uint8)
    )
    corrected_image = Image.fromarray(corrected_image_array)
    return corrected_image


# Set thumbnail dimensions
thumbnail_width = 320
thumbnail_height = 190
resize_factor = 4  # Resize factor
pixels_to_delete_from_top_of_all_thumbnails_image = 20
pixels_to_delete_from_top_of_single_thumbnail_image = 10
box = (0, 0, 56, 10)
box_where = (10, 10)
font = ImageFont.truetype("tahoma.ttf", 16)
vignetting_parameter = 0.0009  # for 6mm lens use 0.0007
folder_path = r"D:\Documents\Astronomija\GMN\dev\SpriteNet\thumbs"

# Open the original image
original_image = Image.open(
    r"D:\Preuzimanja\HR0001_20240910_175313_784114_DETECTED_thumbs.jpg"
)
# Crop top 20 pixels
cropped_image = original_image.crop(
    (
        0,
        pixels_to_delete_from_top_of_all_thumbnails_image,
        original_image.width,
        original_image.height,
    )
)
# Calculate the number of rows and columns based on the cropped image size
num_rows = cropped_image.height // (thumbnail_height)
num_columns = 10  # Assuming 10 columns of thumbnails
count = 0
for row in range(num_rows):
    for column in range(num_columns):
        # Calculate the coordinates for cropping
        left = column * thumbnail_width
        upper = row * thumbnail_height  # Adjust height for cropping
        right = left + thumbnail_width
        lower = upper + thumbnail_height
        # Crop the thumbnail and delete the top 10 pixels
        thumbnail = cropped_image.crop((left, upper, right, lower))

        thumb_timestamp = thumbnail.crop(box)

        # thumbnail.show()
        # Delete the top 10 pixels
        thumbnail = thumbnail.crop(
            (
                0,
                pixels_to_delete_from_top_of_single_thumbnail_image,
                thumbnail.width,
                thumbnail.height,
            )
        )

        # Resize the thumbnail up by a factor of 4
        """
        thumbnail = thumbnail.resize(
            (
                thumbnail_width * resize_factor,
                (thumbnail_height - pixels_to_delete_from_top_of_single_thumbnail_image)
                * resize_factor,
            )
        )  # Adjusted height for resizing
        """

        thumbnail = thumbnail.resize(
            (
                thumbnail_width * resize_factor,
                (thumbnail_height - pixels_to_delete_from_top_of_single_thumbnail_image)
                * resize_factor,
            )
        )  # Adjusted height for resizing
        # thumbnail.paste(thumb_timestamp, box_where)
        thumbnail = apply_vignetting(thumbnail, vignetting_parameter).convert("RGB")
        thumbnail = thumbnail.resize((320, 320))
        # Save the thumbnail to a separate file
        count += 1
        # thumbnail.save(f"{folder_path}/thumbnail_{row+1}_{column+1}.bmp")
        thumbnail.save(f"{folder_path}/thumbnail_{count}.bmp")
        # thumbnail.show()


# Close the original and cropped images
original_image.close()
cropped_image.close()

# SHOULD USE RMS environment!!!
# cd source\rms
# conda activate rms
# python ThumbsResizeBackTest_v03.py
