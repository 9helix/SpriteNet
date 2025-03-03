import os
from PIL import ImageDraw
import numpy as np
import logging
from getThumbs import main
import tarfile
import math
from datetime import datetime

try:
    from tflite_runtime.interpreter import Interpreter

    TFLITE_AVAILABLE = True
except ImportError:
    try:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        from tensorflow.lite.python.interpreter import Interpreter

        TFLITE_AVAILABLE = True
        USING_FULL_TF = True
    except ImportError:
        TFLITE_AVAILABLE = False

"""Some functions were adapted from the yolov5 github repository, mostly from the utils/general.py"""

DEBUG_MODEL_PATH = "/mnt/1tb/Documents/Astronomija/GMN/dev/SpriteNet/yolov5_results/train/spriteNetv5-maxpix_pretrained/weights/best-fp16.tflite"
#DEBUG_MODEL_PATH = "/mnt/1tb/Documents/Astronomija/GMN/dev/SpriteNet/yolov5_results/train/spritenet-maxpixel-v4-pretrained/weights/best-fp16.tflite"
log = logging.getLogger("logger")


def init_interpreter(model_path):
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    print(input_details["shape"], input_details["dtype"])
    print(output_details["shape"])
    return interpreter, input_details, output_details


# taken from yolov5/utils/general.py
def xywh2xyxy(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right."""
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y


# adapted from https://blog.roboflow.com/how-to-code-non-maximum-suppression-nms-in-plain-numpy/
def box_iou_batch(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:

    def box_area(box):
        return (box[2] - box[0]) * (box[3] - box[1])

    # determine surface of each box
    area_a = box_area(boxes_a.T)
    area_b = box_area(boxes_b.T)

    # determine the intersection box
    top_left = np.maximum(boxes_a[:, None, :2], boxes_b[:, :2])
    bottom_right = np.minimum(boxes_a[:, None, 2:], boxes_b[:, 2:])

    # calculate intersection area
    area_inter = np.prod(np.clip(bottom_right - top_left, a_min=0, a_max=None), 2)

    # return iou
    return area_inter / (area_a[:, None] + area_b - area_inter)


def nms(predictions: np.ndarray, iou_threshold: float = 0.45) -> np.ndarray:

    rows, columns = predictions.shape

    # sort predictions by descending score
    sort_index = np.flip(predictions[:, 4].argsort())
    predictions = predictions[sort_index]

    # prepare ious
    boxes = predictions[:, :4]
    ious = box_iou_batch(boxes, boxes)
    ious = ious - np.eye(rows)

    # start with accepting all boxes
    keep = np.ones(rows, dtype=bool)

    # iterate over ious in regard to each box
    for index, iou in enumerate(ious):
        # skip rejected boxes
        if not keep[index]:
            continue

        # discard boxes with high iou
        condition = iou > iou_threshold
        keep = keep & ~condition

    return keep[sort_index.argsort()]

def get_timestamp(folder_path, imgname):
    """
    Find the timestamp in a specific file from a tar.bz2 archive
    
    Args:
        folder_path (str): Path to the folder with thumbnails
        imgname (str): Name of the image without extension
    """
    
    # Get parent folder (directory containing the folder_path)
    parent_folder = os.path.dirname(folder_path)
    
    # Extract info from imgname (assuming imgname format contains station code
    code_and_date = imgname[:15]
    thumb_index=int(imgname.split("_")[-1])
    
    # Find all .tar.bz2 files in parent folder that match pattern
    archive_file=""
    for filename in sorted(os.listdir(parent_folder)):
        if filename.endswith(".tar.bz2") and filename.startswith(f"FS_{code_and_date}"):
            archive_file=filename
            break
    
    if archive_file=="":
        print(f"No matching archives found for {code_and_date} in {parent_folder}")
        return imgname
    
    # Extract the timestamp from the appropriate file in the archive
    archive_path = os.path.join(parent_folder, archive_file)
    FF_FILES_IN_THUMB=5
    try:
        with tarfile.open(archive_path, "r:bz2") as tar:
            ct=1
            # Look through archive files
            for member in sorted(tar.getmembers(),key=lambda x: datetime.strptime(x.name[12:27], "%Y%m%d_%H%M%S")):
                # Find file containing timestamp information 
                # (adjust this condition based on your specific file naming convention)
                if math.ceil(ct/FF_FILES_IN_THUMB)==thumb_index:
                    return member.name[5:27]+"_thumbnail"+str(thumb_index)
                ct+=1
                
    except Exception as e:
        print(f"Error reading archive {archive_file}: {e}")
        return imgname
    
    print(f"No timestamp found for {imgname}")
    return imgname


def mark_sprites(output, image, folder_path, imgname):
    edit_image = image.copy()
    draw = ImageDraw.Draw(edit_image)
    # Draw the rectangle
    width, height = edit_image.size
    for i in range(output.shape[0]):
        top_left = (output[i, 0] * width, output[i, 1] * height)
        bottom_right = (output[i, 2] * width, output[i, 3] * height)
        draw.rectangle([top_left, bottom_right], outline="red", width=1)
        # Display the number above the rectangle
        number = str(round(output[i, 4], 3))
        text_position = (top_left[0], top_left[1] - 15)  # Adjust the position as needed
        draw.text(text_position, number, fill="red")
    imgname=get_timestamp(folder_path,imgname)
    # Save the modified image
    edit_image.save(f'{os.path.join(folder_path,imgname+"_marked")}.png')


def process(
    prediction,
    image,
    folder_path,
    imgname,
    conf_thres=0.25,
    iou_thres=0.45,
    max_det=-1,
    save=True,
):
    """Runs the detector for a single image

    Args:
        prediction (_type_): _description_
        image (_type_): _description_
        folder_path (str): _description_. Defaults to "".
        imgname (str): _description_. Defaults to "".
        conf_thres (float, optional): confidence threshold. Defaults to 0.25.
        iou_thres (float, optional): iou threshold. Defaults to 0.45.
        max_det (int, optional): maximum allowed number of detections. Defaults to -1.
        save (bool, optional): _description_. Defaults to True.
    """
    max_nms = 30000  # upper limit for number of boxes before nms
    # max_wh = 7680 maximum box width/height

    xc = prediction[..., 4] > conf_thres  # detection candidates mask
    # output = np.zeros((max_det, 5))

    # we can later vectorize prediction so it processes all images at once
    for xi, x in enumerate(prediction):
        x = x[xc[xi]]  # detection candidates
        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf
        # calculate box
        box = xywh2xyxy(x[:, :4])
        # find highest confidence among all classes
        conf = np.max(x[:, 5:6], 1, keepdims=True)
        # j=np.argmax(x[:, 5:6], 1, keepdims=True)
        # merge results into one array and filter candidates
        x = np.concatenate((box, conf), 1)[np.reshape(conf, -1) > conf_thres]
        if not x.shape[0]:
            continue
        f = open(os.path.join(folder_path, "detections.txt"), "a")
        f.write(f"{imgname}\n")
        print()
        print(imgname)
        print("Number of initial boxes:", x.shape[0])
        # sort by confidence and remove excess boxes
        x = x[np.argsort(x[:, 4])[::-1][:max_nms]]
        print("Pre-NMS:", x)
        # classes (only 1 used here),c=0
        # c = x[:, 5:6] * max_wh
        # boxes (offset by class), scores
        x = x[:, :5]
        # boxes, scores = x[:, :4] + c, x[:, 4]
        # non-max suppression
        i = nms(x, iou_thres)
        print("Post-NMS:", i)

        # limit detections
        if max_det > 0:
            output = x[i][:max_det]
        else:
            output = x[i]

        # the output is in the format [x1, y1, x2, y2, conf]
        # x1, y1 is the top left corner, x2, y2 is the bottom right corner
        # values are normalized to the image size (0-1)
        # 0,0 is upper left corner
        print("Output:", output)
        if output.shape[0] > 0 and save:
            mark_sprites(output, image, folder_path, imgname)
        for i in output:
            f.write(f"{i[0]},{i[1]},{i[2]},{i[3]},{i[4]}\n")
        f.write("\n")
        f.close()


def run_sprite_detection(folder_path, model_path):
    interpreter, input_details, output_details = init_interpreter(model_path)
    for i in os.listdir(folder_path):
        if not i.endswith("_CAPTURED_thumbs.jpg"):
            continue

        thumbnail_file = os.path.join(folder_path, i)

        for thumbnail, thumbnail_name, subfolder_path in main(0.0009, thumbnail_file):
            image = thumbnail  # .convert("RGB") already done in main

            input_shape = input_details["shape"]
            image = image.resize((input_shape[1], input_shape[2]))
            input_data = np.array(image, dtype=np.float32)

            input_data /= 255
            if len(input_data.shape) == 3:
                input_data = input_data[None]  # expand for batch dim

            # Set the tensor to point to the input data to be inferred
            interpreter.set_tensor(input_details["index"], input_data)

            # Run the inference
            interpreter.invoke()

            # Get the output tensor
            prediction = interpreter.get_tensor(output_details["index"])

            # process(prediction, image, subfolder_path, thumbnail_name, save=True)
            process(
                prediction,
                image,
                subfolder_path,
                thumbnail_name,
                conf_thres=0.434,
                iou_thres=0.1,
                max_det=4,
                save=True,
            )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run sprite detection on FITS files")
    parser.add_argument("folder_path", help="Path to the folder containing FITS files")
    parser.add_argument(
        "--model",
        "-m",
        default=DEBUG_MODEL_PATH,
        help="Path to the TFLite model file (default: %(default)s)",
    )

    args = parser.parse_args()
    if not TFLITE_AVAILABLE:
        log.warning(
            "TensorFlow Lite is not available on this system. Sprite detection skipped..."
        )
    else:
        run_sprite_detection(folder_path=args.folder_path, model_path=args.model)
