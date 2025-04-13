from ultralytics import YOLO

# Load a model
model = YOLO("results/train/spritenet-maxpixel-v7-pretrained2/weights/best.pt")  # load a custom trained model

# Export the model
model.export(format="tflite",imgsz=320, half=True)  # export to TFLITE format


