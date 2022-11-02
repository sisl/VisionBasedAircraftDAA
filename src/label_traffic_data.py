# TODOs in order
# TODO: generate YOLO format directly - one script that generates images, create folder structure, training and validation images, put state data in YOLO folder
# TODO: command line args and then generate it as json file, shell scripts
# TODO: constants.py file for the things that will never change
# TODO; get it to a point where it's super clean and documented -- fully documented data generation python. docstrings for functions, removing old functions, detailed instructions in readme for a small dataset
# TODO: auto cropping for images -- get screen coordinates from xplane? or screenshot window only?

import pandas as pd
import numpy as np
import cv2
import data_generation.settings as s
from data_generation.generate_traffic_data import Aircraft

def get_bb_size(o, i, aw0=0, daw=1):
    """Gets height and width of bounding box"""
    
    x = i.n - o.n
    y = -(i.e - o.e) # right-handed coordinates
    z = i.u - o.u
    print(f"{x}, {y}, {z}")
    
    # Get height and width of bounding box
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    w = daw * (1 / r) + aw0
    h = (3 / 8) * w
    print(f"{w}, {h}")
    return h, w

def gen_labels():
    """Writes bounding box data in Yolo format
    
    Parameters
    ----------
    outdir : str
        The location of the csv file to which to save data
    """

    # Load in the positions
    data_file = s.OUTDIR + "state_data.csv"
    sh, sw, _ = cv2.imread(s.OUTDIR + "imgs/0.jpg").shape
    df = pd.read_csv(data_file)

    for i in range(len(df)):
        xp_data = df.iloc[i]
        own = Aircraft(0, xp_data['e0'], xp_data['n0'], xp_data['u0'], xp_data['h0'])
        intr = Aircraft(0, xp_data['e1'], xp_data['n1'], xp_data['u1'], xp_data['h1'])
        xp, yp = xp_data['intr_x'], xp_data['intr_y'] + s.OFFSET
        h, w = get_bb_size(own, intr, aw0=s.AW0, daw=s.DAW)

        file_name = s.OUTDIR + "imgs/" + str(i) + ".txt"
        with open(file_name, 'w') as fd:
            fd.write("0 %f %f %f %f\n" %
                     (xp  / sw, yp / sh, w / sw, h / sh))
    
    label_name = file_name = s.OUTDIR + "imgs/darket.labels"
    with open(label_name, 'w') as fd:
        fd.write("aircraft")
    
if __name__ == "__main__":
    gen_labels()
