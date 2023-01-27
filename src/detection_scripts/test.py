from ultralytics import YOLO
from PIL import Image

model = YOLO("../../runs/detect/train/weights/best.pt")

# from PIL
path = "../../datasets/sample_small/images/valid"
#im1 = Image.open("../../datasets/sample_mini/images/valid")
results = model.predict(source=path, save=True)  # save plotted images
results2 = model(path)

for r in results2:
    boxes = r.boxes  # Boxes object for bbox outputs
    masks = r.masks  # Masks object for segmenation masks outputs
    probs = r.probs  # Class probabilities for classification outputs
    print(boxes, masks, probs)

#outputs = model.predict(source="../../datasets/sample_mini/images/train/2.jpg", show=True) # treat predict as a Python generator