import mss
import cv2
import pymap3d as pm

from xpc3 import *
from xpc3_helper import *
import data_generation.constants as c
import numpy as np
import time
from scipy.stats import truncnorm
import time
import sys
import os
import argparse
from data_generation.helpers import *
from data_generation.label_traffic_data import run_labeling

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
    client.sendPOSI([*p, aircraft.p, aircraft.r, aircraft.h], aircraft.id)

def mult_matrix_vec(m, v):
    """4x4 matrix transform of an XYZW coordinate - this matches OpenGL matrix conventions"""

    m = np.reshape(m, (4, 4)).T
    return np.matmul(m, v)
    
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
    #screen_w = client.getDREF("sim/graphics/view/window_width")[0]
    #screen_h = client.getDREF("sim/graphics/view/window_height")[0]

    final_x = screen_w * (acf_ndc[0] * 0.5 + 0.5)
    final_y = screen_h * (acf_ndc[1] * 0.5 + 0.5)

    return final_x, screen_h - final_y

def rot_matrix(axis, theta):
    """Returns the rotation matrix for a given theta about a give access"""

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
    """Get position of intrudor according to ownship and parameters
    
    Parameters
    ----------
    ownship : Aircraft
        object storing the positional information of ownship
    r : int
        radial distance to intruder from ownship
    hang, vang : float
        horizontal and vertical angles to intruder from ownship
    h : float
        heading of intruder in degrees

    Returns
    -------
    Aircraft
        object storing positional information of intruder
    """

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
    e0 = np.random.uniform(-args.enrange, args.enrange)  # meters
    n0 = np.random.uniform(-args.enrange, args.enrange)  # meters
    u0 = np.random.uniform(-args.urange, args.urange)  # meters
    h0 = np.random.uniform(args.own_h[0], args.own_h[1])  # degrees
    p0 = truncnorm.rvs(-args.own_p_max, args.own_p_max, loc=0, scale=10) # degrees
    r0 = truncnorm.rvs(-args.own_r_max, args.own_r_max, loc=0, scale=10) # degrees
    ownship = Aircraft(0, e0, n0, u0, h0, p0, r0)

    # Info about relative position of intruder
    vang = np.random.uniform(-args.vfov/2, args.vfov/2)  # degrees
    hang = np.random.uniform(-args.hfov/2, args.hfov/2)  # degrees
    dist = np.random.gamma(args.radius_params[0], args.radius_params[1])  # meters
    while dist < 20:
        dist = np.random.gamma(args.radius_params[0], args.radius_params[1])
    
    # Intruder state
    h1 = np.random.uniform(args.intr_h[0], args.intr_h[1])  # degrees
    intruder = get_intruder_position(ownship, dist, hang, vang, h1)

    return ownship, intruder, vang, hang, dist

def gen_data(client, outdir, total_images):
    """Generates dataset based on parameters in settings.py

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    outdir : str
        path to directory where data is placed
    total_images : int
        number of images total in the dataset
    """

    set_position(client, Aircraft(1, 0, 100, 0, 0, pitch=0, roll=0))
    set_position(client, Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0))
    screen_shot = mss.mss()
    ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[:, :, :]
    sh, sw, _ = ss.shape
    tl_y = 0

    if os.name == "nt": 
        height = client.getDREF("sim/graphics/view/window_height")[0]
        tl_y = int(sh - height)

    csv_file = os.path.join(outdir, 'state_data.csv')
    image_dir = os.path.join(outdir, "train", "images", "")

    for i in range(total_images - args.num_train - args.num_valid, total_images):
        if i == total_images - args.num_valid: image_dir = os.path.join(outdir, "valid", "images", "")
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
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[tl_y:, :, :]
        sh, sw, _ = ss.shape
        x_pos, y_pos = get_bb_coords(client, i, sh, sw)

        # Write the screenshot to a file
        print(f"{image_dir}{i}.jpg")
        cv2.imwrite(f"{image_dir}{i}.jpg", ss)
        
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, ownship.e, ownship.n, ownship.u, ownship.h, ownship.p, ownship.r, vang, hang, z, intruder.e, intruder.n, intruder.u, intruder.h, x_pos, y_pos))

def run_data_generation(client, outdir, total_images):
    """Begin data generation by calling gen_data"""

    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)

    # Set starting position of ownship and intruder
    set_position(client, Aircraft(1, 0, 50, 0, 0, pitch=0, roll=0))
    set_position(client, Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0))

    # Pause to allow time for user to switch to XPlane window
    time.sleep(c.PAUSE_1)

    # Begin
    gen_data(client, outdir, total_images)

if __name__ == "__main__":
    client = XPlaneConnect()
    client.socket.settimeout(None)
    print(sys.argv)
    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--location", dest="location", default = "Palo Alto", help="Airport Location (Options: Palo Alto, Osh Kosh, Boston, and Reno Tahoe)", type=str)
    parser.add_argument("-enr", "--enrange", dest="enrange", default = 5000.0, help="Distance in meters east/north from location", type=float)
    parser.add_argument("-ur", "--urange", dest="urange", default=500.0, help="Distance in meters vertically from location", type=float)
    parser.add_argument("-w", "--weather", dest="weather", default = 4, help="Cloud Cover (0 = Clear, 1 = Cirrus, 2 = Scattered, 3 = Broken, 4 = Overcast)", type=int)
    parser.add_argument("-ds", "--daystart", dest="daystart", default = 8.0, help="Start of day in local time (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.add_argument("-de", "--dayend", dest="dayend", default = 17.0, help="End of day in local time (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.add_argument("-nt", "--train", dest="num_train", default=5, help="Number of samples for training dataset", type=int)
    parser.add_argument("-nv", "--valid", dest="num_valid", default=5, help="Number of samples for validation dataset", type=int)
    parser.add_argument('--label', dest="label", help="Use this flag to run data generation and labeling with the same call", action=argparse.BooleanOptionalAction)
    parser.add_argument('--append', dest="append", help="Use this flag in conjunction with --name to add data to an existing dataset", action=argparse.BooleanOptionalAction)
    parser.add_argument("-name", "--name", dest="datasetname", default=None, help="Name of dataset to be generated", type=str)

    parser.set_defaults(own_h=(0.0,360.0), own_p_max=30.0, own_r_max=60.0)
    parser.set_defaults(intr_h=(0.0,360.0), vfov=40.0, hfov=50.0, radius_params=(2,200))
    parser.set_defaults(daw=20000)

    args = parser.parse_args()
    outdir, total_images = prepare_files(args)
    print(args)

    run_data_generation(client, outdir, total_images)
    if args.label: run_labeling(outdir)