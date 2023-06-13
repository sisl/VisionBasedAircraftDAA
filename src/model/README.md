# Model
Contains functionality for training and evaluating aircraft detection models 

## Contents
* [train.py](./train.py): Code for training a YOLO model -- default contains skeleton code. See instructions below on how to adapt it to your needs. 
* [eval.py](./eval.py): Code for evaluating an aircraft detection model using precision and recall. Outputs the `results.txt` file with a summary of results. See instructions below on how to run evaluation. 
* [results.txt](./results.txt): Results from model evaluation across different environmental factors, outputted by `eval.py`. (This is the default filename, but others can be specified).
* [requirements.txt](./requirements.txt): Specifies package requirements for training and evaluating a model. Run `pip3 install -r requirements.txt` from this directory to install them. 
* [runs](./runs): Git-ignored directory where prediction data is saved via the YOLO API. These files can be generating using the `-s` flag with the evaluation script. 
* [basic_predict.py](./basic_predict.py): Starter code for running model prediction tests (e.g. predictions on a specific folder of images). Image and model location can be specified and results are saved to [runs](./runs).

## Instructions
### Training a YOLO Model
The code in the train.py file is skeleton code for training a new YOLO model whose folder name within the `datasets` directory can be specified using the `-d` flag and whose YOLO model type (specified [here](https://github.com/ultralytics/ultralytics#models)) can be specified using the `-m` flag. This is meant to be starter code that trains on 100 epochs with predominantly default settings, but you will likely want significant customization with training, such as specifiying processor usage, input size, epochs, etc. See [the Ultralytics YOLO documentation](https://docs.ultralytics.com/usage/python/) for information on model training. A test training run can be invoked using `python3 train.py`.

### Evaluating a Model
Run `python3 eval.py -h` to see the available arguments for model evaluation. Most importantly, you can specify the model you are evaluating and the dataset on which to evaluate. The evaluation outputs the precision and recall for the model on different levels of cloud covering, ownship proximity to intruder, vertical angle of intruder from ownship POV, aircraft type, region, and times of day. An example evaluation run can be invoked using `python3 eval.py`. By default, the evaluation will be outputted to a file called `results.txt`.

## Troubleshooting
- If you are receiving an error that the file directory does not exist, double check in your settings.yaml file that the `datasets_dir` value is correct. The directory where you can find this file may look something like this: `/Users/$USER/Library/Application Support/Ultralytics/settings.yaml`