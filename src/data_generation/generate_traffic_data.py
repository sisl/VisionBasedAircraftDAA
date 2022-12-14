import mss
import cv2
import pymap3d as pm
import sys
sys.path.append('..')

from xpc3 import *
import data_generation.constants as c
import numpy as np
import time
from scipy.stats import truncnorm
import time
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
    screen_h, screen_w : int
        height and width of screen in pixels

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

    # Random pitch and roll
    p1 = truncnorm.rvs(-args.own_p_max, args.own_p_max, loc=0, scale=5) # degrees
    r1 = truncnorm.rvs(-args.own_r_max, args.own_r_max, loc=0, scale=10) # degrees

    intruder_obj = Aircraft(1, float(intruder[0]), float(intruder[1]), float(intruder[2]), h, pitch=p1, roll=r1)

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
    p0 = truncnorm.rvs(-args.own_p_max, args.own_p_max, loc=0, scale=5) # degrees
    r0 = truncnorm.rvs(-args.own_r_max, args.own_r_max, loc=0, scale=10) # degrees
    ownship = Aircraft(0, e0, n0, u0, h0, p0, r0)

    # Info about relative position of intruder
    vang = np.random.uniform(-args.vfov/2, args.vfov/2)  # degrees
    hang = np.random.uniform(-args.hfov/2, args.hfov/2)  # degrees
    dist = np.random.gamma(c.DIST_PARAMS[args.ac][0], c.DIST_PARAMS[args.ac][1])  # meters
    while dist < c.DIST_PARAMS[args.ac][2]:
        dist = np.random.gamma(c.DIST_PARAMS[args.ac][0], c.DIST_PARAMS[args.ac][1])
    
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

    screen_shot = mss.mss()
    ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[:, :, :]
    sh, sw, _ = ss.shape
    tl_y = 0

    if os.name == "nt": 
        height = client.getDREF("sim/graphics/view/window_height")[0]
        tl_y = int(sh - height)

    time.sleep(c.PAUSE_2)

    csv_file = os.path.join(outdir, 'state_data.csv')
    image_dir = os.path.join(outdir, "train", "images", "")

    begin = total_images - args.num_train - args.num_valid
    i = begin

    num_scratch = 2

    while i < total_images:
        if i == total_images - args.num_valid: image_dir = os.path.join(outdir, "valid", "images", "")
        # Sample random state
        ownship, intruder, vang, hang, z = sample_random_state()

        # Set time
        local_time = np.random.uniform(args.daystart * 3600, args.dayend * 3600)
        zulu_time = local_time + (c.TIME_OPTIONS[args.location] * 3600)
        client.sendDREF("sim/time/zulu_time_sec", zulu_time)
        client.sendDREF("sim/time/local_date_days", 0)

        # Position aircrafts
        set_position(client, ownship)
        set_position(client, intruder)

        # Pause and then take the screenshot
        time.sleep(c.PAUSE_2)
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[tl_y:, :, :]
        sh, sw, _ = ss.shape
        x_pos, y_pos = get_bb_coords(client, i, sh, sw)

        if num_scratch > 0:
            num_scratch -= 1
            continue

        # Write the screenshot to a file
        print(f"{image_dir}{i}.jpg")
        cv2.imwrite(f"{image_dir}{i}.jpg", ss)
            
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write(f"{i}, {ownship.e}, {ownship.n}, {ownship.u}, {ownship.h}, {ownship.p}, {ownship.r}, {vang}, {hang}, {z}, {intruder.e}, {intruder.n}, {intruder.u}, {intruder.h}, {intruder.p}, {intruder.r}, {x_pos}, {y_pos}, {args.location}, {args.ac}, {args.weather}, {local_time}\n")

        i += 1

def run_data_generation(client, outdir, total_images):
    """Begin data generation by calling gen_data"""

    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)

    # Set starting position of ownship and intruder
    set_position(client, Aircraft(1, 0, 50, 0, 0, pitch=0, roll=0))
    set_position(client, Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0))
    client.sendVIEW(85)

    # Pause to allow time for user to switch to XPlane window
    time.sleep(c.PAUSE_1)

    # Begin
    gen_data(client, outdir, total_images)
    

def main(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--location", dest="location", default = "Palo Alto", help="Airport Location (Options: Palo Alto, Osh Kosh, Boston, and Reno Tahoe)", type=str)
    parser.add_argument("-enr", "--enrange", dest="enrange", default = 5000.0, help="Distance in meters east/north from location", type=float)
    parser.add_argument("-ur", "--urange", dest="urange", default=1000.0, help="Distance in meters vertically from location", type=float)
    parser.add_argument("-w", "--weather", dest="weather", default = 0, help="Cloud Cover (0 = Clear, 1 = Cirrus, 2 = Scattered, 3 = Broken, 4 = Overcast)", type=int)
    parser.add_argument("-ds", "--daystart", dest="daystart", default = 8.0, help="Start of day in local time (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.add_argument("-de", "--dayend", dest="dayend", default = 17.0, help="End of day in local time (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.add_argument("-nt", "--train", dest="num_train", default=5, help="Number of samples for training dataset", type=int)
    parser.add_argument("-nv", "--valid", dest="num_valid", default=5, help="Number of samples for validation dataset", type=int)
    parser.add_argument('--append', dest="append", help="Use this flag in conjunction with --name to add data to an existing dataset", action='store_true')
    parser.add_argument("--name", dest="datasetname", default=None, help="Name of dataset to be generated", type=str)
    parser.add_argument("-ac", "--craft", dest="ac", help="Specify intruder aircraft type ('Cessna Skyhawk', 'Boeing 737-800`, or `King Air C90`)", required=True)
    parser.add_argument("-aw", "--allweather", dest="allweather", help="Use this flag to run this command for every weather type", action='store_true')
    parser.add_argument("--newac", dest="newac", help="Use this flag to indicate that a new aircraft is being used in this instance.", action='store_true')
    parser.set_defaults(own_h=(0.0,360.0), own_p_max=30.0, own_r_max=45.0)
    parser.set_defaults(intr_h=(0.0,360.0), vfov=40.0, hfov=50.0)
    global args
    args = parser.parse_args()

    if args.newac:
        ready = input(f"Enter 'y' once you have adjusted the intruder aircraft to a {args.ac}.\n")
        assert ready == 'y'

    client = XPlaneConnect()
    client.socket.settimeout(None)
    version = client.getDREF("sim/version/xplane_internal_version")[0]
    if version <= 110000: raise RuntimeError("X-Plane version must be >11")
    client.sendVIEW(85)

    client.sendDREF("sim/weather/cloud_type[1]", 0)
    client.sendDREF("sim/weather/cloud_type[2]", 0)
    client.sendDREF("sim/weather/cloud_base_msl_m[0]", 4572) # lowest clouds at about 15000ft
    client.sendDREF("sim/weather/cloud_tops_msl_m[0]", 5182) # upper end of clouds at about 17000ft

    if args.weather is None:
        cloud0 = 0
    else:
        cloud0 = args.weather
    
    client.sendDREF("sim/weather/cloud_type[0]", cloud0)

    if args.allweather:
        if args.datasetname is None:
            stamp = time.time()
            foldername = "data_" + str(stamp)
            args.datasetname = foldername

        for w in range(6):
            client.sendDREF("sim/weather/cloud_type[0]", w)
            args.weather = w
            outdir, total_images = prepare_files(args)
            run_data_generation(client, outdir, total_images)
            run_labeling(outdir)
            args.append = True
    else:
        outdir, total_images = prepare_files(args)
        run_data_generation(client, outdir, total_images)
        run_labeling(outdir)

if __name__ == "__main__":
    main()