#from clearml import Task
from ultralytics import YOLO
import os
import argparse

def train():
    '''Skeleton code for training a YOLo model'''
    
    model = YOLO(args.model)  # build a new model from scratch
    path = os.path.join("..", "..", "datasets", args.dataset, f"{args.dataset}.yaml")
    print(os.path.isfile(path))

    results = model.train(data=f"{path}", epochs=100)  # train the model
    results = model.val()
    success = model.export()
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset", dest="dataset", default = "sample_small", help="Dataset name (within folder 'datasets') with which to train the model", type=str)
    parser.add_argument("-m", "--model", dest="model", default="yolov8s.yaml", help="Model type to change, detailed in YOLO documentation", type=str)
    global args
    args = parser.parse_args()
    train()