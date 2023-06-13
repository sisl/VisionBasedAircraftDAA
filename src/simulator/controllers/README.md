# Controllers

## Overview
Directory containing controller classes which instruct the ownship how to proceed based on information about the intruder provided by the perception system. Controllers have two required member functions: `getStateForPolicy` and `getActionFromPolicy`. The former takes in the encounter state (as defined in the `encounter_sets` repository) and outputs the state format that is required by the controller in order to produce an advisory. The latter takes in the modified state and outputs the advisory based on the class's policy. 

## Contents
* **[BasicController.py](./BasicController.py):** Directly uses 3D coordinates of the intruder and ownship to determine the advisory required. An advisory is issued if the intruder is within 600 vertical feet and 2.1 nautical miles. 
* **[VCAS.py](./VCAS.py):** Returns appropriate advisory based on `vcas_values.h5`, which contains Q-values for each state of the encounter as determined by the previous advisory, tau, relative altitude between aircraft, and vertical velocity.