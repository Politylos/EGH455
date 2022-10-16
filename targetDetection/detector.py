import sys
import torch
import utils
from IPython.display import Image, clear_output   # to display images
from utils.downloads import attempt_download    # to download models/datasets
from roboflow import Roboflow
import matplotlib.pyplot as plt   # as in Pycharm

print('Setup complete. Using torch %s %s' % (torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'))


rf = Roboflow(model_format="yolov5", notebook="roboflow-yolov5")
# rf = Roboflow(api_key="ohCaTajM89xo0LgO1OHG")
# project = rf.workspace("qut-ydf1k").project("egh455-epcw7")
# dataset = project.version(7).download("yolov5")
