# 弃用，会造成阻塞，使用进程间通信
import sys, os
sys.path.append('/home/pi/.local/lib/python3.5/site-packages')
import cv2
import numpy as np
import tensorflow as tf

from scratch3_adapter import settings
from scratch3_adapter.core_extension import Extension

IM_WIDTH = 640  # Use smaller resolution for
IM_HEIGHT = 480  # slightly faster framerate

camera_type = 'usb'

# This is needed since the working directory is the object_detection folder.
sys.path.append(
    '/home/pi/tensorflow1/models/research/object_detection')  # 绝对路径

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# Grab path to current working directory
CWD_PATH = "/home/pi/tensorflow1/models/research/object_detection"

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'mscoco_label_map.pbtxt')

# Number of classes the object detector can identify
NUM_CLASSES = 90

## Load the label map.
# Label maps map indices to category names, so that when the convolution
# network predicts `5`, we know that this corresponds to `airplane`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

### USB webcam ###
if camera_type == 'usb':
    # Initialize USB webcam feed
    camera = cv2.VideoCapture(0)
    ret = camera.set(3, IM_WIDTH)
    ret = camera.set(4, IM_HEIGHT)


class TensorflowExtension(Extension):
    def __init__(self):
        name = type(self).__name__  # class name
        super().__init__(name)

    def run(self):
        while self._running:
            t1 = cv2.getTickCount()

            # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
            # i.e. a single-column array, where each item in the column has the pixel RGB value
            ret, frame = camera.read()
            frame_expanded = np.expand_dims(frame, axis=0)

            # Perform the actual detection by running the model with the image as input
            (boxes, scores, classes, num) = sess.run(
                [
                    detection_boxes, detection_scores, detection_classes,
                    num_detections
                ],
                feed_dict={image_tensor: frame_expanded})
            # https://lijiancheng0614.github.io/2017/08/22/2017_08_22_TensorFlow-Object-Detection-API/
            category_name = category_index[np.squeeze(classes).astype(np.int32)[0]]['name']
            print("classes", category_name)
            message = {"topic": "eim", "message": category_name}
            self.publish(message)
            # publish
            t2 = cv2.getTickCount()
            time1 = (t2 - t1) / freq
            frame_rate_calc = 1 / time1

            # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break

        # 结束后
        # https://github.com/Scratch3Lab/scratch3_adapter_extensions/blob/master/extension_home_assistant.py
        camera.release()
        cv2.destroyAllWindows()

export = TensorflowExtension
