# TODO: combine gen_data and gen_data_yolo
# TODO: pull outdir as global parameter
# TODO: finish function header comments for file

# TODO: redo formatting of output for yolo


from sys import argv
import pandas as pd
import numpy as np
from sympy import arg

def cosd(x):
    """Returns the cosine of an angle given in degrees"""
    return np.cos(x * np.pi / 180)

def sind(x):
    """Returns the sine of an angle given in degrees"""
    return np.sin(x * np.pi / 180)

def tand(x):
    """Returns the tangent of an angle given in degrees"""
    return np.tan(x * np.pi / 180)

def get_bounding_box(data, hfov=80, vfov=49.50, offset=0, tilt=0, sw=1920, sh=1056, aw0=0, daw=17000):
    """Determines the bounding box for the intrudor plane
    
    Parameters
    ----------
    data : dict
        Contains the location data for a single plane and intruder instance

    Returns
    -------
    xp, yp : int
        x and y pixel locations for the bounding box for the intruder
    w, h : int
        width and height of bounding box
    """

    h0 = data['h0']

    # Make ownship be the origin
    x = data['n1'] - data['n0']
    y = -(data['e1'] - data['e0'])  # right-handed coordinates
    z = data['u1'] - data['u0']

    # Rotate x and y according to ownship heading
    xrot = x * cosd(h0) - y * sind(h0)
    yrot = -(x * sind(h0) + y * cosd(h0))

    # Account for offset
    z = z + offset

    # Rotate z according to tilt angle
    xcam = xrot * cosd(tilt) - z * sind(tilt)
    ycam = yrot
    zcam = xrot * sind(tilt) + z * cosd(tilt)

    # https://www.youtube.com/watch?v=LhQ85bPCAJ8
    xp = ycam / (xcam * tand(hfov / 2))
    yp = zcam / (xcam * tand(vfov / 2))

    # Get xp and yp between 0 and 1
    xp = (xp + 1) / 2
    yp = (yp + 1) / 2

    # Map to pixel location
    xp = xp * sw
    yp = (1 - yp) * sh

    # Get height and width of bounding box
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    w = daw * (1 / r) + aw0
    h = (3 / 8) * w

    return xp, yp, w, h

def gen_labels(outdir):
    """Writes bounding box data to a csv file for each image
    
    Parameters
    ----------
    outdir : str
        The location of the csv file to which to save data
    """

    # Load in the positions
    data_file = outdir + "state_data.csv"
    df = pd.read_csv(data_file)

    # Start new file with labels
    label_file = outdir + "bounding_boxes.csv"
    with open(label_file, 'w') as fd:
        fd.write("filename,xp,yp,w,h\n")

        for i in range(len(df)):
            xp, yp, w, h = get_bounding_box(df.iloc[i])
            fd.write("%d,%f,%f,%f,%f,\n" %
                     (i, xp, yp, w, h))

def gen_labels_yolo(outdir):
    """Writes bounding box data to a csv file for each image
    
    Parameters
    ----------
    outdir : str
        The location of the csv file to which to save data
    """

    print(argv)
    # Load in the positions
    data_file = outdir + "state_data.csv"
    df = pd.read_csv(data_file)

    for i in range(len(df)):
        xp, yp, w, h = get_bounding_box(df.iloc[i])

        file_name = outdir + "imgs/" + str(i) + ".txt"
        with open(file_name, 'w') as fd:
            fd.write("0 %f %f %f %f\n" %
                     (xp  / 1920, yp / 1056, w / 1920, h / 1080))
    
    label_name = file_name = outdir + "imgs/darket.labels"
    with open(label_name, 'w') as fd:
        fd.write("aircraft")


outdir = "/scratch/smkatz/yolo_data/val_data/"
outdir = "datasets/"
gen_labels_yolo(outdir)