import os
import argparse


def find_ff_files(root_folder, station_code):
    """
    Find all files starting with FF_ in subfolders, ignoring Sprites-false folder.

    Args:
        root_folder (str): Path to the root folder to search

    Returns:
        list: List of found FF_ files
    """
    subdirs = ["train", "test", "valid"]
    dates = set()
    for subdir in subdirs:
        search_dir = os.path.join(root_folder, subdir, "labels")
        for filename in os.listdir(search_dir):

            if (
                filename.startswith(f"FF_{station_code}")
                and filename.endswith(".txt")
                and os.stat(os.path.join(search_dir, filename)).st_size > 0
            ):
                # Extract date and hour from filename

                # full_path = os.path.join(folder_path, filename)
                # ff_files.append(full_path)
                dates.add(filename[3:25])

    return dates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find FF_ files in subfolders.")
    parser.add_argument("folder", help="Root folder to search")
    parser.add_argument(
        "--station",
        "-s",
        default="",
        help="Station code to filter FF_ files (e.g. 'CA0001')",
    )
    args = parser.parse_args()

    ff_files = find_ff_files(args.folder, args.station)

    print(f"Found {len(ff_files)} unique nights for station {args.station}:")
    with open("scripts/nights.txt", 'w') as f:
        for file_path in ff_files:
            f.write(f"{file_path}\n")
