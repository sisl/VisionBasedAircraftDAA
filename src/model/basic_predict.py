import os
import argparse
from ultralytics import YOLO
from PIL import Image

def basic_predict():
    '''Helper function for predicting on select test images'''

    model = YOLO(args.path_to_model) #yolov8
    #model = torch.hub.load('ultralytics/yolov5', 'custom', path=args.path_to_model) #yolov5
    source_list = os.listdir(os.path.join(
        args.path_to_datadir))
    image_list = []
    
    for im_f in source_list:
        im_path = os.path.join(args.path_to_datadir, im_f)
        if im_path == os.path.join(args.path_to_datadir, '.DS_Store'): continue
        image_list.append(Image.open(im_path))

    # yolov8
    results = model.predict(
        source=image_list, save=True, save_txt=False, hide_labels=True, hide_conf=True)
    for prediction in results:
        boxes = prediction.boxes.xyxy
        print(boxes)
    return
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadir", dest="path_to_datadir",
                        default="./test_imgs", help="Relative path to the directory for the dataset with which you want to evaluate the model.")
    parser.add_argument("-m", "--model", dest="path_to_model",
                        default="../../models/baseline.pt", help="Relative path to the file for the model (e.g. model.pt) you want to evaluate.")
    global args
    args = parser.parse_args()
    basic_predict()