#from clearml import Task
from ultralytics import YOLO
import os


def train():
    name = "starter_dataset"
    #task = Task.init(project_name="YOLOv8", task_name=name)
    model = YOLO("yolov8s.yaml")  # build a new model from scratch

    path = os.path.join("VisionBasedAircraftDAA","datasets",name,f"{name}.yaml")
    path2 = os.path.join("datasets", name,f"{name}.yaml")
    results = model.train(data=f"{path2}", epochs=100, device="0")  # train the model
    results = model.val()
    success = model.export()

    return
    name = "sample_mini"
    task = Task.init(project_name="YOLOv8", task_name=name)

    # Load a model
    model = YOLO("yolov5s.yaml")  # build a new model from scratch

    # Use the model
    path = os.path.join("..","..","datasets",name,f"{name}.yaml")
    results = model.train(data=path, epochs=3)  # train the model
    results = model.val()  # evaluate model performance on the validation set
    success = model.export()  # export a model to pt format


if __name__ == '__main__':
    train()