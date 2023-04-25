# Perception System

## Overview
Contains code for the simulator perception system. This includes detection of the intruder craft and translation into the intruder state. 

## Contents
* **[XPlanePerception](./XPlanePerception.py):** Aircrafts are positioned in XPlane and the aircraft detection model is used to detect the intruder in frame. If the intruder is detected, its true state is returned. Otherwise, it is clear of conflict. 
* **[PerfectPerception](./PerfectPerception.py):** Intruder state is perfectly perecived every time. It's true state is simply returned as the result of the perception system. 
* **[images](./images/):** Self-managed directory that stores images for gif generation. Images are automatically cleared

## Required Functions
* `perceiveIntruderState`