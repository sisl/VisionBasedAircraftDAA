import pandas as pd
import numpy as np
import cv2
from data_generation.helpers import Aircraft
import argparse
import json
import os
import data_generation.constants as c

def get_bb_size(o, i, aw0=0, daw=1):
    """Gets height and width of bounding box"""
    
    x = i.n - o.n
    y = -(i.e - o.e) # right-handed coordinates
    z = i.u - o.u
    
    # Get height and width of bounding box
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    w = float(daw) * (1 / r) + aw0
    h = (3 / 8) * w
    return h, w

def gen_labels(metadata, total_images):
    """Writes bounding box data in Yolo format
    
    Parameters
    ----------
    metadata : dict
        contains metadata for the dataset
    total_images : number of images in dataset
    """

    # Load in the positions
    outdir = metadata['outdir']
    data_file = os.path.join(outdir, 'state_data.csv')
    sh, sw, _ = cv2.imread(os.path.join(outdir, "train", "images", "0.jpg")).shape
    df = pd.read_csv(data_file)

    curr_dir = outdir + "train/"
    for i in range(total_images - metadata['num_train'] - metadata['num_valid'], total_images):
        if i == total_images - metadata['num_valid']: curr_dir = os.path.join(outdir, "valid", "")
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

    with open(os.path.join(outdir, "metadata.json"), "r") as metafile:
        metadata = json.load(metafile)

    set_names = [float(x) for x in list(metadata.keys()) if x != 'total_images']
    to_label = str(max(set_names))

    gen_labels(metadata[to_label], metadata['total_images'])
    
if __name__ == "__main__":
    # TODO: make this a parser argument
    
    data_folder = input("Name of folder for data you would like to label: ")

    run_labeling(c.PATH + data_folder)
