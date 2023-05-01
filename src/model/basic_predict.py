import os
import argparse
from ultralytics import YOLO
from PIL import Image


def basic_predict():
    model = YOLO(args.path_to_model)
    source_list = os.listdir(os.path.join(
        args.path_to_datadir))
    image_list = []
    
    for im_f in source_list:
        im_path = os.path.join(args.path_to_datadir, im_f)
        if im_path == os.path.join(args.path_to_datadir, '.DS_Store'): continue
        image_list.append(Image.open(im_path))

    results = model.predict(
        source=image_list, save=True, save_txt=False, hide_labels=True, hide_conf=True)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadir", dest="path_to_datadir",
                        default="./test_imgs", help="Relative path to the directory for the dataset with which you want to evaluate the model.")
    parser.add_argument("-m", "--model", dest="path_to_model",
                        default="../../models/baseline.pt", help="Relative path to the file for the model (e.g. model.pt) you want to evaluate.")
    parser.add_argument("-t", "--train", dest="train_and_val",
                        action=argparse.BooleanOptionalAction, default=False, help="Flag for specifying that the evaluation should be done on both the training and validation data.")
    parser.add_argument("-o", "--outfile",
                        dest="outfile_name", default="results", help="Name of output file for evaluation results, without a filetype suffix. If a file with this name already exists, it will be overwritten.")
    global args
    args = parser.parse_args()
    basic_predict()