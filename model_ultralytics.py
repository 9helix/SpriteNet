#import comet_ml
from clearml import Task
from roboflow import Roboflow
from dotenv import load_dotenv
import os
from ultralytics import YOLO, settings

settings.update({"comet": False})

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('API_KEY')

project_name = "results"
dataset_name = "spritenet-maxpixel"
dataset_version=7
descriptor="pretrained" 
experiment_name = f"{dataset_name}-v{dataset_version}-{descriptor}"
format="yolov11"

rf = Roboflow(api_key=api_key)
project = rf.workspace("gmnsprites").project(dataset_name)
version = project.version(dataset_version)
dataset = version.download(format,f"roboflow/{dataset_name}-{dataset_version}-yolo11") 

dataset_dir = dataset.location
print(f"\nDataset downloaded to {dataset_dir}")

#comet_ml.init()

task = Task.init(project_name="spritenet", task_name=experiment_name)

model_variant = "yolo11s" 
task.set_parameter("model_variant", model_variant)

args = dict(data=f"{dataset_dir}/data.yaml", epochs=250, imgsz=320,device='cuda',batch=0.4,cache="disk",project=f"{project_name}/train",name=experiment_name,plots=True)
task.connect(args)

model = YOLO(f"{model_variant}.pt")
results = model.train(**args)

# Evaluate model performance on the validation set
#metrics = model.val()

# Perform object detection on an image
#results = model("path/to/image.jpg")
#results[0].show()

# Export the model to TFLITE format
#path = model.export(format="tflite")  # return path to exported model