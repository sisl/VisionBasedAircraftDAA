# Dataset Generation Instructions
#### Specifics for Anthony

## Before Starting

1. Download XPlane 11: [Download Link](https://www.x-plane.com/desktop/try-it/older/)
2. Make sure you are running XPlane 11.5+. If you are not, follow the prompts on XPlane to update your version.
3. Download and configure XPlane Connect: [Instructions Here](https://github.com/nasa/XPlaneConnect) (Make sure you download the file titled XPlaneConnect.zip)

## Setup in X-Plane

1. Open XPlane in full screen mode. If using Windows OS, follow troubleshooting tip #1 below. 
2. From the main menu, select "New Flight"
3. Select "Cessna Skyhawk" for ownship.
4. Click on "AI Aircraft" in the upper right corner of the panel. Click "Edit" on the existing intruder listed and select "Cessna Skyhawk" from the menu that pops up. Then click "Done" twice to confirm. 
5. Click "Start Flight" in the bottom right corner and wait for the scene to fully load. 

## Dataset Generation Instructions

1. Open a terminal window from this repository and cd into the "src" folder. 
2. From the "src" folder, run the script file with the "run" prefix according to which will run on your system (e.g. "run.sh" if on MacOS). Answer "y" in the terminal when asked if the intruder craft has been properly set. Quickly toggle to the XPlane window and wait for the images to generate. 
3. Uncomment lines 1, 5, 7, and 12 and comment out lines 14 and 19 (using a '#'). This will enable the scripts to run to capture data for the Boeing 737-800 intruder craft. 
4. Adjust the intruder craft in XPlane to be a Boeing 737-800 by clicking the plane symbol in the upper right corner, selecting AI Aircraft, and editing the AI craft to be the Boeing 737-800. 
5. Run the script file again, answer "y" when prompted about the intruder craft, and toggle to the XPlane window for the images to generate. 
6. Uncomment lines 14 and 19 and comment out lines 21 and 26. This will enable the scripts to run for the King Air C90. Adjust the intruder craft to be a King Air C90 following the same procedure as step 4. 
7. Run the script file again, answer "y" when prompted about the intruder craft, and toggle to the XPlane window for the images to generate.
