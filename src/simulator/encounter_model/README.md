# Encounter Model

## Overview 
This folder contains files for generating encounter sets for the aircraft simulator. Generated encounter sets are stored in [encounter_sets](../encounter_sets/).

## Contents
* **[straight_line_model.py](./straight_line_model.py):** Contains functionality for generating basic encounters in which both aircrafts travel in straight lines with a fixed vertical distance and fixed velocities. 
* **[utils.py](./utils.py):** Contains helper functions for encounter model generation, including an `EncounterDescription` class for storing encounter set metadata, an `Encounter` class for storing information about individual encounters, and a helper function for outputting the encounter set to a csv file. 

## Instructions
### Generating Encounter Set With straight_line_model
Run `python3 straight_line_model.py -h` to see the arguments available for generating the encounter set. Then, running the same command with desired arguments will generate the encounter set and place it into the [encounter_sets](../encounter_sets/) directory. See the README for [encounter_sets](../encounter_sets/) for information on the outputted formatting for the collection of encounters. See the `sampler` function in `straight_line_model.py` to see what positional parameters are used when generating encounters.