# Datasets

Each dataset folder is generated programmatically according to formatting required by YOLO. More information can be found [in this formatting guide](./FORMAT.pdf). The general structure of each folder is diagrammed below:
```
.
└── [DATASET NAME]/
    ├── metadata.json
    ├── [DATASET NAME].yaml
    ├── state_data.json
    ├── train/
    │   ├── images/
    │   │   ├── 0.jpg
    │   │   ├── 1.jpg
    │   │   └── ...
    │   └── labels/
    │       ├── 0.txt
    │       ├── 1.txt
    │       └── ...
    └── valid/
        ├── images/
        │   ├── x.jpg
        │   ├── x+1.jpg
        │   └── ...
        └── labels/
            ├── x.txt
            ├── x+1.txt
            └── ...
```