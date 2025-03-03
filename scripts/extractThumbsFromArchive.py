import os
import tarfile
from datetime import datetime

def download_meteor_images():
    """
    Downloads meteor detection images from Global Meteor Network stations.
    Finds images by locating 'Captured thumbnails' text and getting the first linked image after it.
    Preserves original image filenames.
    """
    folder = input("Folder with archives: ")
    ignore=False
    start_date = input("Start date (YYYYMMDD): ")
    end_date = input("End date (YYYYMMDD): ")
    if start_date == "" or end_date == "":
        ignore=True
    else:
        # Convert string dates to datetime objects for comparison
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")
    
    thumbs_folder = os.path.join(folder, "thumbs")
    os.makedirs(thumbs_folder, exist_ok=True)

    for filename in os.listdir(folder):
        if filename.endswith(".tar.bz2"):
            archive_path = os.path.join(folder, filename)
            file_date_str = filename[10:18]
            file_date = datetime.strptime(file_date_str, "%Y%m%d")
                
            # Check if file date is within range
            if ignore or start_dt <= file_date <= end_dt:
                # Open the tar.bz2 archive
                with tarfile.open(archive_path, "r:bz2") as tar:
                    # Find files ending with _CAPTURED_thumbs.jpg
                    for member in tar.getmembers():
                        if member.name.endswith("_CAPTURED_thumbs.jpg"):
                            # Extract the file to thumbs folder
                            member.name = os.path.basename(member.name)  # Remove path info
                            tar.extract(member, thumbs_folder,filter='data')
                            print(f"Extracted: {member.name}")
                            break


if __name__ == "__main__":
    download_meteor_images()
