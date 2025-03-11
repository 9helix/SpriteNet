#import comet_ml
from clearml import Task
from roboflow import Roboflow
from dotenv import load_dotenv
import os
from ultralytics import YOLO


# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('API_KEY')


project_name = "results"
dataset_name = "spritenet"
dataset_version=5
descriptor="pretrained-yolo11s" 
experiment_name = f"{dataset_name}-v{dataset_version}-{descriptor}"
format="yolov5"

rf = Roboflow(api_key=api_key)
project = rf.workspace("gmnsprites").project(dataset_name)
version = project.version(dataset_version)
#dataset = version.download(format,f"roboflow/{dataset_name}-{dataset_version}") 

dataset_dir = "roboflow/SpriteNet-5-copy"#dataset.location
print(f"\nDataset downloaded to {dataset_dir}")

#comet_ml.init()

task = Task.init(project_name="spritenet", task_name=experiment_name)

model_variant = "yolo11s"
task.set_parameter("model_variant", model_variant)

args = dict(data=f"{dataset_dir}/data_yolo11.yaml", epochs=250, imgsz=320,device='cuda',batch=100,cache='disk',project=f"{project_name}/train",name=experiment_name,plots=True)
task.connect(args)

model = YOLO(f"{model_variant}.pt")
results = model.train(**args)