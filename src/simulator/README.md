# Simulator

## Overview
This folder contains files for building aircraft encounter sets and running encounter simulations, organized into three main elements: the encounter model, perception system, and controller. 

## Contents
* **[encounter_model](encounter_model/):** Contains files for generating aircraft encounters. The encounters are then followed step by step to simulate two aircrafts encountering each other mid-air. 
* **[perception](perception/):** Contains files that provide functionality for the ownship in the simulator to perceive where the intruder is in the frame. This informs the controller in the system. 
* **[controllers](controllers/):** Contains files for the controller which processes the state found by the perception system and outputs the action the pilot should take. 

* **[encounter_sets](encounter_sets/):** Contains encounter files outputted by the encounter model to be used by the simulator. 
* **[gifs](gifs/):** Contains any gifs of the encounters created by the simulator. See instructions below on how to invoke this functionality. 
* **simulate.py:** Contains functionality for running the encounter simulations. 
* **constants.py:** Contains necessary constants for the simulator. 
* **evaluation.py:** Contains evaluation functions for the simulator. 

## Instructions
### Running simulation