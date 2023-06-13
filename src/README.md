# VisionBasedAircraftDAA/src

## Overview
This is the main code folder for generating datasets, building models, and simulators, for the Vision-Based Aircraft detect and avoid (DAA) problem. 

## Contents
* **[data_generation](data_generation/):** Contains files relevant to generating datasets. More information can be found in the subfolder README. 
* **[notebooks](notebooks/):** Contains jupyter notebooks useful for verifying and visualizing the functionality of the repository
* **[model](model/):** Contains files relevant to training and evaluating a new model. More information can be found in the subfolder README.
* **[simulator](simulator/):** Contains files relevant to simulating aircraft encounters. More information can be found in the subfolder README.
* **[xpc3.py](./xpc3.py):** Helper functions for using [XPlaneConnect](https://github.com/nasa/XPlaneConnect) to programmatically adjust the specifications for the aircraft and environment on X-Plane
