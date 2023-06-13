# Models

## Overview
Directory for storing model files for evaluation and use in the simulator. See the [src/model](../src/model) directory for details on how to train a new model. 

## Contents
* **baseline.pt:** YOLOv8 trained on the [AVOIDDS dataset](https://purl.stanford.edu/hj293cv5980)
* **alternative.pt:** YOLOv8 model trained on a subset of the AVOIDDS dataset that included images in nominal conditions (in Palo Alto, with minimal cloud cover, between 8:00 and 15:00)