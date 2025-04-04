import os
from datetime import datetime, timedelta
from CALSTARS import readCALSTARS
from matplotlib import pyplot as plt
from datetime import datetime, timedelta

subdirs = ["train", "test", "valid"]

main_folder = "roboflow/spritenet-maxpixel-7"  # input("Database folder:")
calstars_folder = "/mnt/1tb/Documents/Astronomija/GMN/dev/sprite star analysis/extracts for sprites/CALSTARS_archive/"  # input("Calstars folder:")


stars=[]
for subdir in subdirs:
    subdir_path = os.path.join(main_folder, subdir)
    for i in os.listdir(os.path.join(subdir_path, "labels")):
        if i.startswith("FF_") and i.endswith(".txt"):
            time_str = i[10:25]  # yyyyMMdd_hhmmss

            # Convert to datetime and adjust if hour < 13
            date_time = datetime.strptime(f"{time_str}", "%Y%m%d_%H%M%S")

            
            station_code=i.split("_")[1]
            best_night=("",timedelta(hours=22).total_seconds())
            for j in os.listdir(os.path.join(calstars_folder)):

                if j.startswith(f"CALSTARS_{station_code}"):
                    time_str2="_".join(j.split("_")[2:4])  
                    date_time2 = datetime.strptime(f"{time_str2}", "%Y%m%d_%H%M%S")
                    
                    if date_time2 <= date_time:
                        
                        time_diff = date_time - date_time2
                        
                        if best_night[1]>=time_diff.total_seconds():
                            best_night=(os.path.join(calstars_folder, j),time_diff.total_seconds())
                            
                            
                    
            if not best_night[0]:
                print(f"calstars not found for {i}")
                continue
            
            print(f"found calstars {os.path.basename(best_night[0])}")
            calstars_file = best_night[0]

            calstars = readCALSTARS(os.path.dirname(calstars_file),os.path.basename(calstars_file))

            thumb_stars = 0
            
            for ff in calstars:
                if os.path.splitext(ff[0])[0] in i:
                    thumb_stars=len(ff[1])
                    break
            print(i,thumb_stars)
            stars.append(thumb_stars)
print(stars)
print(len(stars))
plt.hist(stars, bins='auto')
plt.show()