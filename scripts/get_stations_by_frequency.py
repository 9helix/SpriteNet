import os
import argparse
from collections import defaultdict


def find_ff_files(root_folder):
    """
    Find all files starting with FF_ in subfolders, ignoring Sprites-false folder.

    Args:
        root_folder (str): Path to the root folder to search

    Returns:
        list: List of found FF_ files
    """
    subdirs = ["train", "test", "valid"]
    x = defaultdict(int)
    for subdir in subdirs:
        search_dir = os.path.join(root_folder, subdir, "labels")
        for filename in os.listdir(search_dir):

            if (
                filename.startswith(f"FF_")
                and filename.endswith(".txt")
                and os.stat(os.path.join(search_dir, filename)).st_size > 0
            ):
                x[filename[3:9]] += 1

    # Sort x by value in ascending order
    sorted_items = sorted(x.items(), key=lambda item: item[1])
    # Return just the keys (station codes)
    sorted_stations = [(item[0], item[1]) for item in sorted_items]
    return sorted_stations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find FF_ files in subfolders.")
    parser.add_argument("folder", help="Root folder to search")

    args = parser.parse_args()

    ff_files = find_ff_files(args.folder)

    print(f"Found {len(ff_files)} unique stations:")
    with open("scripts/stations.txt", 'w') as f:
        for file_path in ff_files:
            f.write(f"{file_path}\n")
