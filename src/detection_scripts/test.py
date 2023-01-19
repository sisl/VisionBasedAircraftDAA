from ultralytics import YOLO

model = YOLO("/Users/elysiasmyers/Desktop/VisionBasedAircraftDAA/runs/detect/train237/weights/best.pt") 
results = model("../datasets/demo/train/images/2.jpg")
print(results)

outputs = model.predict(source="../datasets/demo/train/images/2.jpg", return_outputs=True) # treat predict as a Python generator
for output in outputs:
  # each output here is a dict.
  # for detection
  #print(output["det"])  # np.ndarray, (N, 6), xyxy, score, cls
  pass