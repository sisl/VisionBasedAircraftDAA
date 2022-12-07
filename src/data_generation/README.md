# Dataset Generation Instructions
# TO FINISH

## Before Starting

1. Download XPlane 11: [Download Link](https://www.x-plane.com/desktop/try-it/older/)
2. Make sure you are running XPlane 11.5+. If you are not, follow the prompts on XPlane to update your version.
3. Download and configure XPlane Connect: [Instructions Here](https://github.com/nasa/XPlaneConnect) (Make sure you download the file titled XPlaneConnect.zip)
4. From the main directory, run `pip install -r setup/requirements.txt`
5. cd into src

## Setup in X-Plane

1. Open XPlane in full screen mode. If using Windows OS, follow troubleshooting tip #1 below. 
2. From the main menu, select "New Flight"
3. Select any aircraft type for the ownship. Testing was predominantly done with Cessna Skyhawk as ownship.
4. In the upper right corner of the Aircraft menu, select "AI Aircraft." 
5. If there are intruder aircrafts already listed, delete all but 1 and then click on "Edit." If there are none, select "Add Aircraft" in the bottom left corner and then select "Edit" for the aircraft that newly appears.
6. In the Edit menu, select one of the following aircrafts: Boeing 737-800, Cessna Skyhawk, or King Air C90. Then click "Done." 
7. In the bottom right corner, select "Start Flight" and wait for the scene to appear. 

## General Instructions for Generating a Dataset

1. If using MacOS, open run.sh. If using Windows OS, open run.ps1. In these files, there are pre-set calls to generate and label the dataset. This will run the scripts 4 times to generate the dataset for each of the four location options listed. The main things that will need to be adjusted are the `--daw` and `--name` flags. Be sure to adjust these flags for each of the four commands. Run `python3 -m data_generation.generate_traffic_data --help` to see the meaning of each flag.
2. Adjust the `--daw` flag to match the current state of the intruder aircraft. There are values specified in the help text for this flag to indicate which value should be used for each aircraft type.
3. Adjust the `--name` flag to match the desired name for the dataset folder. This can be an existing folder or a new one. If you are using the name of an existing folder, be sure to add the `--append` flag to the first command. 
4. Adjust any other flags as desired. (Other likely ones are the `-nt` and `-nv` flags)
5. From the src folder, run the appropriate shell script file (e.g. `./run.sh`)
6. Quickly toggle to have XPlane in the foreground and wait for the images to be generated.

## Specific Instructions for Dataset Generation for Anthony
1. Follow the setup instructions above to create a flight with a Cessna Skyhawk intruder. 
2. From the src folder, run the test shell script currently in the "run" files (e.g. `./run.sh` for MacOS or `.\run.ps1` on Windows). Use the "Checking the Bounding Boxes" instructions below to verify that the bounding boxes look correct. 
3. In the appropriate script file (run.sh if on Mac or run.ps1 for Windows), 

## Checking the Bounding Boxes

1. Open the DatasetVisualization.ipynb jupyter notebook located in the "notebooks" folder. 
2. Adjust the value of `DATASET_NAME` to match the name of the folder in which the data is stored.
3. Run all cells and view results in the "Check Results of label_traffic_data" section.

## Troubleshooting

1. **If screenshots are all of the same frame even though the XPlane simulator is updating positions properly:** Configure windowed simulator on XPlane by navigating to `Flight -> Flight Configuration -> Settings icon in upper right -> Graphics -> Monitor usage -> toggle to “Windowed Simulator”`
2. **If screenshots on MacOS are not capturing XPlane:** Go to System Preferences > Security & Privacy > Privacy > Screen Recording. Then make sure your IDE and/or Terminal are listed as allowed to take screen recordings on your device. 
