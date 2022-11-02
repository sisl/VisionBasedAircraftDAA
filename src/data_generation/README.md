# Dataset Generation Instructions

## Before Starting

1. Make sure you are running XPlane 11.5+. If you are not, follow the prompts on XPlane to update your version.
2. From the main directory, run `pip install -r setup/requirements.txt`
3. cd into src

## Generating the Dataset

1. Open XPlane in full screen mode
2. Toggle to View > Internal > Forward with No Display
3. In the src folder, run `python3 -m data_generation.generate_traffic_data`
4. Quickly toggle to have XPlane in the foreground and wait for the 10 images to be generated.

## Checking the Bounding Boxes

1. Go to the BoundingBoxTuning.ipynb notebook
2. Adjust the value of `DATASET_NAME` to match the name of the folder in which the data is stored.
3. Run all cells and view results in the "View and Tune Bounding Boxes" section.
