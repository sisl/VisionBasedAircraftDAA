# Dataset Generation Instructions

## Before Starting

1. Download XPlane 11: [Download Link](https://www.x-plane.com/desktop/try-it/older/)
2. Make sure you are running XPlane 11.5+. If you are not, follow the prompts on XPlane to update your version.
3. Download and configure XPlane Connect: [Instructions Here](https://github.com/nasa/XPlaneConnect) (Make sure you download the file titled XPlaneConnect.zip)
4. From the main directory, run `pip install -r setup/requirements.txt`
5. cd into src

## Generating the Dataset

1. Open XPlane in full screen mode
2. Toggle to View > Internal > Forward with No Display
3. In the src folder, run `python3 -m data_generation.generate_traffic_data`
4. Quickly toggle to have XPlane in the foreground and wait for the 10 images to be generated.

## Checking the Bounding Boxes

1. Go to the BoundingBoxTuning.ipynb notebook
2. Adjust the value of `DATASET_NAME` to match the name of the folder in which the data is stored.
3. Run all cells and view results in the "View and Tune Bounding Boxes" section.

## Troubleshooting
- **If screenshots are all of the same frame even though the XPlane simulator is updating positions properly:** Configure windowed simulator on XPlane by navigating to `Flight -> Flight Configuration -> Settings icon in upper right -> Graphics -> Monitor usage -> toggle to “Windowed Simulator”`