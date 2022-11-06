import mss
import cv2
import pymap3d as pm
import json

from xpc3 import *
from xpc3_helper import *
import data_generation.constants as c
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
import time
import os
import yaml
import sys
import argparse


class Aircraft:
    def __init__(self, ac_num, east, north, up, heading, pitch=-998, roll=-998):
        self.id = ac_num
        self.e = east
        self.n = north
        self.u = up
        self.h = heading
        self.p = pitch
        self.r = roll
    
    def __str__(self):
        out = "Craft: %.2f, East: %.2f, North: %.2f, Up: %.2f, Heading: %.2f, Pitch: %.2f, Roll: %.2f" % (self.id, self.e, self.n, self.u, self.h, self.p, self.r)
        return out

def set_position(client, aircraft):
    """Sets position of aircraft in XPlane

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    aircraft : Aircraft
        object containing details about craft's position
    """
    ref = c.REGION_OPTIONS[args.location]
    p = pm.enu2geodetic(aircraft.e, aircraft.n, aircraft.u, ref[0], ref[1], ref[2]) #east, north, up
    print(aircraft)
    client.sendPOSI([*p, aircraft.p, aircraft.r, aircraft.h], aircraft.id)

def mult_matrix_vec(m, v):
    """4x4 matrix transform of an XYZW coordinate - this matches OpenGL matrix conventions"""
    dst = np.zeros(4)
    dst[0] = v[0] * m[0] + v[1] * m[4] + v[2] * m[8] + v[3] * m[12]
    dst[1] = v[0] * m[1] + v[1] * m[5] + v[2] * m[9] + v[3] * m[13]
    dst[2] = v[0] * m[2] + v[1] * m[6] + v[2] * m[10] + v[3] * m[14]
    dst[3] = v[0] * m[3] + v[1] * m[7] + v[2] * m[11] + v[3] * m[15]
    return dst
    
def get_bb_coords(client, i, screen_h, screen_w):
    """Calculates coordinates of intruder bounding box
    
    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    i : int
        id number of ownship intruder instantiation

    Returns
    -------
    int
        x position of intruder on screen from upper left 0,0
    int
        y position of intruder on screen from upper left 0,0
    """

    # retrieve x,y,z position of intruder
    acf_wrl = np.array([
        client.getDREF("sim/multiplayer/position/plane1_x")[0],
        client.getDREF("sim/multiplayer/position/plane1_y")[0],
        client.getDREF("sim/multiplayer/position/plane1_z")[0],
        1.0
    ])
    
    mv = client.getDREF("sim/graphics/view/world_matrix")
    proj = client.getDREF("sim/graphics/view/projection_matrix_3d")
    
    acf_eye = mult_matrix_vec(mv, acf_wrl)
    acf_ndc = mult_matrix_vec(proj, acf_eye)
    
    acf_ndc[3] = 1.0 / acf_ndc[3]
    acf_ndc[0] *= acf_ndc[3]
    acf_ndc[1] *= acf_ndc[3]
    acf_ndc[2] *= acf_ndc[3]
    
    # Bizaar issue with these not retrieving the correct window size
    # screen_w = client.getDREF("sim/graphics/view/window_width")[0]
    # screen_h = client.getDREF("sim/graphics/view/window_height")[0]

    final_x = screen_w * (acf_ndc[0] * 0.5 + 0.5)
    final_y = screen_h * (acf_ndc[1] * 0.5 + 0.5)

    return final_x, screen_h - final_y

def rot_matrix(axis, theta):
    theta = np.deg2rad(theta)
    if axis == 'x':
        return np.matrix([[ 1, 0           , 0           ],
                   [ 0, np.cos(theta), -np.sin(theta)],
                   [ 0, np.sin(theta), np.cos(theta)]])
    elif axis == 'y':
        return np.matrix([[ np.cos(theta), 0, np.sin(theta)],
                    [ 0           , 1, 0           ],
                    [-np.sin(theta), 0, np.cos(theta)]])
    elif axis == 'z':
        return np.matrix([[ np.cos(theta), -np.sin(theta), 0 ],
                    [ np.sin(theta), np.cos(theta) , 0 ],
                    [ 0           , 0            , 1 ]])
    return None

def get_intruder_position(ownship, r, hang, vang, h):
    inclination = np.deg2rad(90-vang)
    azimuth = np.deg2rad(90-hang)

    # Set initial cartesian coordinates
    e1 = r * np.sin(inclination) * np.cos(azimuth)
    n1 = r * np.sin(inclination) * np.sin(azimuth)
    u1 = r * np.cos(inclination)

    # Rotate according to Tait-Bryant Convention
    intruder = np.array([e1, n1, u1]).reshape(-1, 1)
    intruder = np.matmul(rot_matrix('y', ownship.r), intruder)
    intruder = np.matmul(rot_matrix('x', ownship.p), intruder)
    intruder = np.matmul(rot_matrix('z', -1*ownship.h), intruder)
    intruder += np.array([ownship.e, ownship.n, ownship.u]).reshape(-1, 1)
    intruder_obj = Aircraft(1, float(intruder[0]), float(intruder[1]), float(intruder[2]), h)

    return intruder_obj 

def sample_random_state():
    """Generates ownship and intruder position values
    
    Returns
    -------
    ownship : Aircraft
        ownship position information
    intruder : Aircraft
        intruder position information
    vang, hang : float
        horizontal and vertical angle of intruder from ownship in degrees
    dist : int
        radial distance between ownship and intruder
    """

    # Ownship state
    e0 = np.random.uniform(-args.enurange, args.enurange)  # meters
    n0 = np.random.uniform(-args.enurange, args.enurange)  # meters
    u0 = np.random.uniform(-500, 500)  # meters
    h0 = np.random.uniform(args.own_h[0], args.own_h[1])  # degrees
    p0 = truncnorm.rvs(-args.own_p_max, args.own_p_max, loc=0, scale=10) # degrees
    r0 = truncnorm.rvs(-args.own_r_max, args.own_r_max, loc=0, scale=10) # degrees
    ownship = Aircraft(0, e0, n0, u0, h0, p0, r0)

    # Info about relative position of intruder
    vang = np.random.uniform(-args.vfov/2, args.vfov/2)  # degrees
    hang = np.random.uniform(-args.hfov/2, args.hfov/2)  # degrees
    dist = np.random.uniform(args.radius_range[0], args.radius_range[1])  # meters
    
    # Intruder state
    h1 = np.random.uniform(args.intr_h[0], args.intr_h[1])  # degrees
    intruder = get_intruder_position(ownship, dist, hang, vang, h1)

    return ownship, intruder, vang, hang, dist

def gen_data(client, outdir):
    """Generates dataset based on parameters in settings.py

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    """

    screen_shot = mss.mss()

    csv_file = outdir + 'state_data.csv'
    image_dir = outdir + "train/images/"
    for i in range(args.num_train + args.num_valid):
        if i == args.num_train: image_dir = outdir + "valid/images/"
        # Sample random state
        ownship, intruder, vang, hang, z = sample_random_state()

        # Position the aircraft
        zulu_time = c.TIME_OPTIONS[args.location] * 3600
        zulu_time += np.random.uniform(args.daystart * 3600, args.dayend * 3600)
        client.sendDREF("sim/time/zulu_time_sec", zulu_time)
        set_position(client, ownship)
        set_position(client, intruder)

        # Pause and then take the screenshot
        time.sleep(c.PAUSE_2)
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[:, :, :]
        sh, sw, _ = ss.shape
        x_pos, y_pos = get_bb_coords(client, i, sh, sw)

        # Write the screenshot to a file
        print(f"{image_dir}{i}.jpg")
        cv2.imwrite(f"{image_dir}{i}.jpg", ss)
        
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, ownship.e, ownship.n, ownship.u, ownship.h, ownship.p, ownship.r, vang, hang, z, intruder.e, intruder.n, intruder.u, intruder.h, x_pos, y_pos))

def run_data_generation(client, outdir):
    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)

    set_position(client, Aircraft(1, 0, 0, 0, 0, pitch=0, roll=0))
    set_position(client, Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0))

    time.sleep(c.PAUSE_1)

    gen_data(client, outdir)


# code to help obtain new starting positions
def testing_locs(client):
    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)


    o = Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0)
    i = Aircraft(1, 0, 20, 0, 0, pitch=0, roll=0)
    set_position(client, o)
    set_position(client, i)
    time.sleep(10)

    for v in range(25):
        for h in range(40):
            i = get_intruder_position(o, 60.0, h, v, 0)
            set_position(client, i)
            time.sleep(0.01)

    i = get_intruder_position(o, 60.0, 40, 0, 0)
    set_position(client, i)
    time.sleep(2)

    i = get_intruder_position(o, 60.0, 0, 25, 0)
    set_position(client, i)
    time.sleep(2)
    '''

    for p in range(90):
        for r in range(90):
            for h in range(90):
                o = Aircraft(0, 0, 0, 0, h, pitch=p, roll=r)
                i = Aircraft(1, 0, 20, 0, 0, pitch=0, roll=0)
                set_position(client, o)
                i = get_intruder_position(o, 60.0, 38, 22, 0)
                set_position(client, i)
                time.sleep(0.02)'''

    return


    print(o)
    set_position(client, o)
    i = Aircraft(1, 0, 20, 0, 0, pitch=0, roll=0)
    set_position(client, i)
    #time.sleep(2)
    i = get_intruder_position(o, 20, 0, 0, 0)
    print(i)
    set_position(client, i)

def make_yaml_file(outdir):
    data = {
        "train": f"{outdir}/train/images",
        "val": f"{outdir}/valid/images",
        "names": {0: "aircraft"}
    }
    with open(f'{outdir}data.yaml', 'w+') as out:
        yaml.dump(data, out, default_flow_style=False, sort_keys=False)

def prepare_files():
    outdir = args.outdir + "data_" + str(time.time()) + "/"
    args.outdir = outdir
    os.makedirs(outdir)
    os.makedirs(outdir + "train/images/")
    os.makedirs(outdir + "valid/images/")
    os.makedirs(outdir + "train/labels/")
    os.makedirs(outdir + "valid/labels/")

    make_yaml_file(outdir)

    # set metadata
    json_object = json.dumps(vars(args), indent=4)
    with open(outdir + "metadata.json", "w") as outfile:
        outfile.write(json_object)

    csv_file = outdir + 'state_data.csv'
    with open(csv_file, 'w+') as fd:
        fd.write("filename,e0,n0,u0,h0,p0,r0,vang,hang,z,e1,n1,u1,h1,intr_x,intr_y\n")
    return outdir

if __name__ == "__main__":
    client = XPlaneConnect()
    print(sys.argv)
    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--location", dest = "location", default = "Palo Alto", help="Airport Location", type=str)
    parser.add_argument("-r", "--enurange", dest = "enurange", default = 5000.0, help="Distance in meters ENU from location", type=float)
    parser.add_argument("-w", "--weather", dest = "weather", default = 4, help="Cloud Cover (0 = Clear, 1 = Cirrus, 2 = Scattered, 3 = Broken, 4 = Overcast)", type=int)
    parser.add_argument("-ds", "--daystart", dest = "daystart", default = 8.0, help="Start of day in local time (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.add_argument("-de", "--dayend", dest = "dayend", default = 17.0, help="End of day in local time (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.set_defaults(own_h=(0.0,360.0), own_p_max=45.0, own_r_max=45.0)
    parser.set_defaults(intr_h=(0.0,360.0), vfov=40.0, hfov=50.0, radius_range=(20,500))
    parser.set_defaults(num_train=5, num_valid=5)
    parser.set_defaults(daw=20000)
    parser.set_defaults(outdir="../datasets/")

    args = parser.parse_args()
    outdir = prepare_files()

    #testing_locs(client)
    run_data_generation(client, outdir)