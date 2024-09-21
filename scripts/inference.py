import os
import tensorflow as tf
from PIL import Image
import numpy as np


interpreter = tf.lite.Interpreter(
    model_path=r"yolov5_results\train\spriteNetv5-maxpix\weights\best-fp16.tflite"
)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()[0]
output_details = interpreter.get_output_details()[0]

print(input_details)
print(output_details)

for img in os.listdir("thumbs"):
    image_path = os.path.join("thumbs", img)
    image = Image.open(image_path).convert("RGB")
    input_shape = input_details["shape"]
    image = image.resize((input_shape[1], input_shape[2]))
    input_data = np.expand_dims(image, axis=0)
    input_data = np.array(input_data, dtype=np.float32)

    # Set the tensor to point to the input data to be inferred
    interpreter.set_tensor(input_details["index"], input_data)

    # Run the inference
    interpreter.invoke()

    # Get the output tensor
    output_data = interpreter.get_tensor(output_details["index"])
    print(output_data)
    break


# input_data = tf.constant(1., shape=[1, 1])
# interpreter.set_tensor(input['index'], input_data)
# interpreter.invoke()
# interpreter.get_tensor(output['index']).shape
