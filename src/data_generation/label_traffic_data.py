# TODOs in order
# DONE: generate YOLO format directly - one script that generates images, create folder structure, training and validation images, put state data in YOLO folder
# DONE: command line args and then generate it as json file, shell scripts
# DONE: constants.py file for the things that will never change
# TODO; get it to a point where it's super clean and documented -- fully documented data generation python. docstrings for functions, removing old functions, detailed instructions in readme for a small dataset
# TODO: auto cropping for images -- get screen coordinates from xplane? or screenshot window only?

import pandas as pd
import numpy as np
import cv2
from data_generation.helpers import Aircraft
import argparse
import json

def get_bb_size(o, i, aw0=0, daw=1):
    """Gets height and width of bounding box"""
    
    x = i.n - o.n
    y = -(i.e - o.e) # right-handed coordinates
    z = i.u - o.u
    
    # Get height and width of bounding box
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    w = daw * (1 / r) + aw0
    h = (3 / 8) * w
    return h, w

def gen_labels(metadata):
    """Writes bounding box data in Yolo format
    
    Parameters
    ----------
    outdir : str
        The location of the csv file to which to save data
    """

    # Load in the positions
    outdir = metadata['outdir']
    data_file = outdir + "state_data.csv"
    sh, sw, _ = cv2.imread(outdir + "train/images/0.jpg").shape
    df = pd.read_csv(data_file)

    curr_dir = outdir + "train/"
    for i in range(len(df)):
        if i == metadata['num_train']: curr_dir = outdir + "valid/"
        xp_data = df.iloc[i]
        own = Aircraft(0, xp_data['e0'], xp_data['n0'], xp_data['u0'], xp_data['h0'])
        intr = Aircraft(0, xp_data['e1'], xp_data['n1'], xp_data['u1'], xp_data['h1'])
        xp, yp = xp_data['intr_x'], xp_data['intr_y']
        h, w = get_bb_size(own, intr, daw=metadata['daw'])

        file_name = curr_dir + "labels/" + str(i) + ".txt"
        with open(file_name, 'w+') as fd:
            fd.write("0 %f %f %f %f\n" %
                     (xp  / sw, yp / sh, w / sw, h / sh))

    print("Dataset folder: " + outdir)

def run_labeling(outdir):
    """Begin data labeling sequence"""
    with open(outdir + "/metadata.json", "r") as metafile:
        metadata = json.load(metafile)

    gen_labels(metadata)
    
if __name__ == "__main__":
    data_folder = input("Name of folder for data you would like to label: ")

    parser = argparse.ArgumentParser()
    parser.set_defaults(outdir="../datasets/")
    args = parser.parse_args()

    run_labeling(args.outdir + data_folder)