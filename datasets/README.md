# Datasets

Each dataset folder is generated programmatically according to formatting required by YOLOv5 which is described in detail in [this formatting guide](./FORMAT.pdf). Information about the anatomy of a request to produce these datasets can be found [in the data_generation README](../src/data_generation/README.md). 

## Sample Datasets
* **[sample_mini](sample_mini/):** A 10-image mini dataset that was the result of one call to generate data with clear skies in one location with one aircraft type
* **[sample_small](sample_small/):** A 60-image dataset that was the result of one call to generate data with the '-aw' flag, so the same call was made for all 6 weather types in the same location with the same aircraft

## Dataset Structure Outline
The general structure of each folder is diagrammed below. See the above-linked formatting guide for a more in-depth description. 
```
.
└── [DATASET NAME]/
    ├── metadata.json
    ├── [DATASET NAME].yaml
    ├── state_data.json
    ├── images/
    │   ├── train/
    │   │   ├── 0.jpg
    │   │   ├── 1.jpg
    │   │   └── ...
    │   └── valid/
    │       ├── 0.txt
    │       ├── 1.txt
    │       └── ...
    └── labels/
        ├── train/
        │   ├── x.jpg
        │   ├── x+1.jpg
        │   └── ...
        └── valid/
            ├── x.txt
            ├── x+1.txt
            └── ...
```
