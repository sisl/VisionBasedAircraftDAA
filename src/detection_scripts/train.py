from clearml import Task
from ultralytics import YOLO

def train():
    task = Task.init(project_name="YOLOv8", task_name="test")

    # Load a model
    model = YOLO("yolov5s.yaml")  # build a new model from scratch

    # Use the model
    results = model.train(data="../datasets/test/test.yaml", epochs=3)  # train the model
    results = model.val()  # evaluate model performance on the validation set
    success = model.export()  # export a model to pt format


if __name__ == '__main__':
    train()