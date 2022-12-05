# Dataset Generation Instructions
#### Specifics for Anthony
These instructions will walk you through the process of generating 72,000 XPlane images for a training dataset. The commands overall will produce 24,000 total images for each of 3 aircraft types, where 10% of the images are validation images. Each command produces 900 training and 100 validation images for each of the 6 weather types at each location for each aircraft type. 

The commands will need to be run in three groups (one for each aircraft type) where 24,000 images are produced for that aircraft. The aircraft will then need to be manually changed between each grouping of commands. The instructions will walk you through changing the aircraft and toggling on and off the necessary command groups in the script files. 

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
2. From the "src" folder, run the script file with the "generate" prefix according to which will run on your system (e.g. "./generate.sh" if on MacOS). Answer "y" in the terminal when asked if the intruder craft has been properly set. After responding to that prompt, toggle to the XPlane window and wait for the images to generate. If the scene does not begin changing rapidly after 15 seconds, return to the terminal window, as an error may have occurred. Wait for the images to finish generated, which will be evident when the scene stops changing at the same rapid cadence. This is estimated to take about 2 hours. 
3. Uncomment lines 3 and 11 and comment out lines 1, 13, and 21 (using a '#'). This will enable the scripts to run to capture data for the Boeing 737-800 intruder craft. 
4. Adjust the intruder craft in XPlane to be a Boeing 737-800 by clicking the plane symbol in the upper right corner, selecting AI Aircraft, and editing the AI craft to be the Boeing 737-800. 
5. Run the script file again, answer "y" when prompted about the intruder craft, and toggle to the XPlane window for the images to generate. (Again, estimated to complete in about 2 hours).  
6. Uncomment lines 13 and 21 and comment out lines 23 and 31. This will enable the scripts to run for the King Air C90. Adjust the intruder craft to be a King Air C90 following the same procedure as step 4. 
7. Run the script file again, answer "y" when prompted about the intruder craft, and toggle to the XPlane window for the images to generate. (Again, estimated to complete in about 2 hours). 
