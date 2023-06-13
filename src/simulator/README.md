# Simulator

## Overview
This folder contains files for building aircraft encounter sets and running encounter simulations, organized into three main elements: the encounter model, perception system, and controller. 

## Main Contents
* **[encounter_model](encounter_model/):** Contains files for generating aircraft encounters. The encounters are then followed step by step to simulate two aircraft encountering each other mid-air. 
* **[perception](perception/):** Contains files that provide functionality for the ownship in the simulator to perceive where the intruder is in the frame. This informs the controller in the system. 
* **[controllers](controllers/):** Contains files for the controller which processes the state found by the perception system and outputs the action the pilot should take. 

## Other Contents
* **[encounter_sets](encounter_sets/):** Contains encounter files outputted by the encounter model to be used by the simulator. 
* **[gifs](gifs/):** Contains any gifs of the encounters created by the simulator. See instructions below on how to invoke this functionality. 
* **[simulate.py](./simulate.py):** Contains functionality for running the encounter simulations. 
* **[simulate.sh](./simulate.sh):** Shell script file that contains commands to simulate encounters with the 96 combinations of the 6 cloud types, 4 locations, and 4 times of day.
* **[constants.py](./constants.py):** Contains necessary constants for the simulator. 
* **[evaluation.py](./evaluation.py):** Contains evaluation functions for the simulator. 

## Instructions
### Running simulation
The simulator is customizable so that models can be evaluated on the collision avoidance task in a variety of conditions. These condition variables can be set using command line arguments; a summary of the available arguments can be viewed using the command `python3 simulate.py -h`. 

In order to run simulation, X-Plane must be set up (instructions below) and open on your computer so that you can quickly toggle to the window and wait for simulation to begin. Then, there are two main ways simulation can be run:

1. **One command at a time:** To run only one set of encounters on the same set of conditions (i.e. with the same command line arguments), use the command line call to `python3 simulate.py` with the desired arguments as outlined in the helper text visible from a call to `python3 simulate.py -h`. 
2. **In a shell script:** If you want to run a shell script with multiple simulation commands, this can be done easily by creating a shell script file and executing it using the command `./[FILENAME]`. In order to set variables for use in all commands in the shell script file, the `-b` flag can be added to each command to indicate "bulk" simulation, in which case variables can be overriden in the `BULK SIMULATION VARIABLE SETUP` section of [simulate.py](./simulate.py). 

You will need to keep the X-Plane window open and full-screen for the entirety of simulation, and then simulation results can be found in a csv file whose default name is `per_enc_eval.csv`. Each simulation takes around 30 seconds to run. 

### Setup X-Plane
1. Follow the setup instructions in the [root README](../../README.md).
2. Open XPlane in full screen mode. If using Windows OS, follow troubleshooting tip #1 below. 
3. From the main menu, select "New Flight"
4. **Setup aircraft**
    * Select any aircraft type for the ownship. Testing was predominantly done with Cessna Skyhawk as ownship.
    * In the upper right corner of the Aircraft menu, select "AI Aircraft." 
    * If there are intruder aircraft already listed, delete all but 1 and then click on "Edit." If there are none, select "Add Aircraft" in the bottom left corner and then select "Edit" for the aircraft that newly appears.
    * In the Edit menu, select one of the following aircraft: Boeing 737-800, Cessna Skyhawk, or King Air C90. Then click "Done." 
5. In the bottom right corner, select "Start Flight" and wait for the scene to appear. 