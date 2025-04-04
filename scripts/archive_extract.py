import os
import tarfile
from datetime import datetime, timedelta
with open("stations.txt") as f:
    for line in f:
        night = line.strip()
        station_code,date_str,time_str = night.split("_")
        date = datetime.strptime(date_str+"_"+time_str, "%Y%m%d_%H%M%S")
        best_night=("",timedelta(hours=22).total_seconds())
        print(night)
        with os.scandir(f"/home/{station_code.lower()}/files/processed/") as entries:
            for entry in entries:
                if entry.is_file():
                    date2 = datetime.strptime("_".join(entry.name.split("_")[1:-2]), "%Y%m%d_%H%M%S")
                    if date2 <= date:
                        time_diff = date - date2
                        if best_night[1]>=time_diff.total_seconds():
                            best_night=(entry.name,time_diff.total_seconds())

        if best_night[0]!="":
            path=os.path.join(f"/home/{station_code.lower()}/files/processed/",best_night[0])
            file_suffix='_'.join(best_night[0].split("_")[:-1])
            if not os.path.exists(f"./CALSTARS_{file_suffix}.txt"):
                print(f"./CALSTARS_{file_suffix}.txt not found. extracting...")
                with tarfile.open(os.path.join(f"/home/{station_code.lower()}/files/processed/",best_night[0]), "r:bz2") as tar:
                    #os.makedirs(f"./{night}/", exist_ok=True)
                    #try:
                    #    tar.extract(f'./FS_{file_suffix}_fieldsums.tar.bz2', f"./{night}/")
                    #    print(f"Extracted: {member.name}")
                    #except KeyError:
                    #    print(f"Couldnt extract: {member.name}")
                    try:
                        tar.extract(f'./CALSTARS_{file_suffix}.txt', f"./")
                        print(f"Extracted: ./CALSTARS_{file_suffix}.txt")
                    except KeyError:
                        print(f"Couldnt extract: ./CALSTARS_{file_suffix}.txt")
