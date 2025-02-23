import numpy as np
from PIL import Image, ImageOps
import os
import pytesseract as pyt

"""
Script for separating thumbnails from a single image. Adapted from the original script made by Damir Šegon.
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
# for 6mm lens use 0.0007, default is 0.0009, for hr0002 0.0003
vignetting_parameter = float(input("Vignetting parameter: "))  

# Open the original image
image_path = input("Image path: ")
original_image = Image.open(image_path)
folder_path = os.path.join(os.path.dirname(image_path), os.path.basename(image_path)[:15])
os.makedirs(folder_path, exist_ok=True)
# Crop top 20 pixels
cropped_image = original_image.crop(
    (
        0,
        pixels_to_delete_from_top_of_all_thumbnails_image,
        original_image.width,
        original_image.height,
    )
)
original_image.close()
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

        thumbnail = thumbnail.resize(
            (
                thumbnail_width * resize_factor,
                (thumbnail_height - pixels_to_delete_from_top_of_single_thumbnail_image)
                * resize_factor,
            )
        )  # Adjusted height for resizing

        # thumbnail = thumbnail.resize((320, 320))
        # thumbnail.paste(thumb_timestamp, box_where)
        thumbnail = apply_vignetting(thumbnail, vignetting_parameter).convert("RGB")
        thumbnail = thumbnail.resize((320, 320))
        # Save the thumbnail to a separate file
        count += 1
        # thumbnail.save(f"{folder_path}/thumbnail_{row+1}_{column+1}.bmp")
        thumbnail.save(
            f"{folder_path}/{os.path.basename(folder_path)}_thumbnail_{count}.bmp"
        )
        # thumbnail.show()
    
"""     thumb_resize_factor = 10
    thumb_timestamp = thumb_timestamp.resize(
        (
            thumb_timestamp.width * thumb_resize_factor,
            thumb_timestamp.height * thumb_resize_factor,
        )
    )
       # Apply thresholding - convert to grayscale first if not already
    thumb_timestamp = thumb_timestamp.convert('L')
    
    thumb_timestamp = ImageOps.expand(thumb_timestamp, border=100, fill="black")
    from PIL import ImageFilter
    
    #blur_radius = 1.5  # Adjust this value as needed (0.5 to 2.0 usually works well)
    
    #thumb_timestamp = thumb_timestamp.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    threshold = 100  # Adjust this value between 0-255 as needed
    thumb_timestamp = thumb_timestamp.point(lambda x: 255 if x > threshold else 0, '1')
    thumb_timestamp=thumb_timestamp.filter(ImageFilter.ModeFilter(size=15))
    print(pyt.image_to_string(thumb_timestamp).strip().replace(".",""))
    #thumb_timestamp.show()
    #exit()  """

# Close the original and cropped images
cropped_image.close()

