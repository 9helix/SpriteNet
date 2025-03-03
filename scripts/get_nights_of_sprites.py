import os
import argparse
from pathlib import Path


def find_ff_files(root_folder,station_code):
    """
    Find all files starting with FF_ in subfolders, ignoring Sprites-false folder.
    
    Args:
        root_folder (str): Path to the root folder to search
    
    Returns:
        list: List of found FF_ files
    """
    dates=set()
    root_path = Path(root_folder)
    
    # Walk through all subdirectories
    for folder_path, subfolders, filenames in os.walk(root_folder):
        # Skip the Sprites-false folder at the first depth level
        rel_path = Path(folder_path).relative_to(root_path)
        parts = rel_path.parts
        
        if len(parts) > 0 and parts[0] == "Sprites-false":
            continue
            
        # Find files starting with FF_
        for filename in filenames:
            if filename.startswith(f"FF_{station_code}"):
                                # Extract date and hour from filename
                date_str = filename[10:18]  # yyyyMMdd
                hour_str = filename[19:21]  # hh
                
                # Convert to datetime and adjust if hour < 13
                from datetime import datetime, timedelta
                date_time = datetime.strptime(f"{date_str}", "%Y%m%d")
                if int(hour_str) < 13:
                    date_time = date_time - timedelta(days=1)
                
                # Update filename with adjusted date
                date =date_time.strftime("%Y%m%d")
                #full_path = os.path.join(folder_path, filename)
                #ff_files.append(full_path)
                dates.add(date)
    
    return dates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find FF_ files in subfolders.")
    parser.add_argument("folder", help="Root folder to search")
    parser.add_argument("--station", "-s", default="", help="Station code to filter FF_ files (e.g. 'CA0001')")
    args = parser.parse_args()
    
    ff_files = find_ff_files(args.folder, args.station)
    
    print(f"Found {len(ff_files)} unique nights for station {args.station}:")
    for file_path in ff_files:
        print(file_path)