# Data Generation

## Contents
* **constants.py:** Contains constants for locations and aircrafts used in data generation and labeling calculations
* **generate_traffic_data.py:** Main file containing code for generating images using XPlane
* **generate.sh and generate.ps1:** Script files that can be used for running multiple commands in a row. Includes example data generation commands
* **helpers.py:** Contains helper functions for data generation
* **label_traffic_data.py:** Main code file for labeling the XPlane images in YOLO format

## Instructions
Instructions for using the data_generation portion of the repository. This will walk you through how to generate images rapidly of different scenes in XPlane using XPlaneConnect for vision-based aircraft detect-and-avoid algorithm testing. All images and labels (in YOLO format) are saved to the [datasets folder](../../datasets/).

### Setup XPlane
1. Follow the setup instructions in the [root README](../../README.md).
2. Open XPlane in full screen mode. If using Windows OS, follow troubleshooting tip #1 below. 
3. From the main menu, select "New Flight"
4. **Setup aircrafts**
    * Select any aircraft type for the ownship. Testing was predominantly done with Cessna Skyhawk as ownship.
    * In the upper right corner of the Aircraft menu, select "AI Aircraft." 
    * If there are intruder aircrafts already listed, delete all but 1 and then click on "Edit." If there are none, select "Add Aircraft" in the bottom left corner and then select "Edit" for the aircraft that newly appears.
    * In the Edit menu, select one of the following aircrafts: Boeing 737-800, Cessna Skyhawk, or King Air C90. Then click "Done." 
5. In the bottom right corner, select "Start Flight" and wait for the scene to appear. 

### Generate Images

*Overview*
All commands to generate data will have the general form of `python3 -m generate_traffic_data -ac [AIRCRAFT NAME]` run from the data_generation folder. The default command will generate 5 training and 5 validation images with 0 cloud cover in Palo Alto with the aircraft as currently set. Specifying the aircraft name in the command is for calculation purposes and will NOT change the aircraft in XPlane. (This must be done manually as specified above). 

The sample command in the `generate` script files is of the form: `python3 -m generate_traffic_data -aw -ac "Cessna Skyhawk" --newac --name "test"`. As specified by the '-aw' flag, the command will generate 10 images (5 training and 5 validation) in each of 6 levels of cloud cover in the default location (Palo Alto) As specified by '--newac', a prompt will appear in the terminal before data is generated asking the user to confirm that the intruder aircraft type in XPlane matches the one specified in the command. As specified by '--name "test"', the data will be generated in a folder called 'test'. 

Use the `-h` flag to see the different arguments and options available for setting the dataset, flight, and environment specifications. The only required argument is `-ac`/`--craft`, which must be followed by the name of the aircraft type. 

*General Recommendations*
The '-ac' argument is required, and it is recommended that you use '--newac' every time the aircraft needs to be changed. The '--newac' flag will ask the user to verify that the intruder aircraft in XPlane matches the one specified in the command. The options for aircraft type and location strings can be found in the help text outputed when the '-h' flag is used. Location and weather can be changed as desired in sequential commands, and there will be a longer pause between images with these changes. '-aw' can be used to specify that the same command should be run for each of the 6 weather types. The number of training and validation images can be specified using the '-nt' and '-nv' arguments. If a '--name' is not specified for the dataset folder, a folder will be generated with the prefix 'data_' followed by the current time as a floating point number.

*Instructions*
1. Open a terminal window from this repository and cd into the "data_generation" folder. 
2. Determine what command(s) you would like to run. If there are multiple commands, you can put them in a script file (such as '.sh' or '.ps1' files).
3. From the "data_generation" folder, run the command or script file as desired. If '--newac' is used, you must reply 'y' in the terminal when requested. After responding to that prompt, toggle to the XPlane window and wait for the images to generate. If the scene does not begin changing rapidly after 15 seconds, return to the terminal window, as an error may have occurred. Wait for the images to finish generated, which will be evident when the scene stops changing at the same rapid cadence and when there is more than a 15 second pause (which would be to be expected between location switches).

### Visualize Results
1. Open the DatasetVisualization.ipynb jupyter notebook located in the "notebooks" folder. 
2. Adjust the value of `DATASET_NAME` to match the name of the folder in which the data is stored.
3. Run all cells and view results in the "Check Results of label_traffic_data" section.

### Troubleshooting

1. **If screenshots are all of the same frame even though the XPlane simulator is updating positions properly:** Configure windowed simulator on XPlane by navigating to `Flight -> Flight Configuration -> Settings icon in upper right -> Graphics -> Monitor usage -> toggle to “Windowed Simulator”`
2. **If screenshots on MacOS are not capturing XPlane:** Go to System Preferences > Security & Privacy > Privacy > Screen Recording. Then make sure your IDE and/or Terminal are listed as allowed to take screen recordings on your device. 
