# Perception System

## Overview
Contains code for the simulator perception system. Custom perception systems can be created so long as they include the three required functions listed below, per the default simulator implementation. This includes detection of the intruder aircraft and translation into the intruder state. 

## Contents
* **[XPlanePerception](./XPlanePerception.py):** Aircraft are positioned in X-Plane and the aircraft detection model is used to detect the intruder in frame. If the intruder is detected, its true state is returned. Otherwise, it is clear of conflict. 
* **[PerfectPerception](./PerfectPerception.py):** Intruder state is perfectly perecived every time. It's true state is simply returned as the result of the perception system. 

## Required Functions
* `perceiveIntruderState`: takes as input the states of the ownship and intruder and determines the intruder state detected by the ownship
* `set_time`: set the time of the encounter in X-Plane
* `evalEnc`: takes as input an encounter, its index, and associated command line arguments and performs and records results from desired evaluation of the model's performance on the encounter