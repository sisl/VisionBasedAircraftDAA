# DONE: intruder position
# TODO: clean up file
# TODO: 1920x1080 screen resolution before taking pictures

import mss
import cv2
import pymap3d as pm
import json

from xpc3 import *
from xpc3_helper import *
import data_generation.settings as s
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.stats import truncnorm


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
    ref = s.REGION_OPTIONS[s.REGION_CHOICE]
    p = pm.enu2geodetic(aircraft.e, aircraft.n, aircraft.u, ref[0], ref[1], ref[2]) #east, north, up
    client.sendPOSI([*p, aircraft.p, aircraft.r, aircraft.h], aircraft.id)

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
    e0 = np.random.uniform(-s.EAST_RANGE, s.EAST_RANGE)  # meters
    n0 = np.random.uniform(-s.NORTH_RANGE, s.NORTH_RANGE)  # meters
    u0 = np.random.uniform(-s.UP_RANGE, s.UP_RANGE)  # meters
    h0 = np.random.uniform(s.OWNSHIP_HEADING[0], s.OWNSHIP_HEADING[1])  # degrees
    p0 = truncnorm.rvs(s.PITCH_RANGE[0], s.PITCH_RANGE[1], loc=0, scale=10) # degrees
    r0 = truncnorm.rvs(s.ROLL_RANGE[0], s.ROLL_RANGE[1], loc=0, scale=10) # degrees
    ownship = Aircraft(0, e0, n0, u0, h0, p0, r0)

    # Info about relative position of intruder
    vang = np.random.uniform(s.VANG_RANGE[0], s.VANG_RANGE[1])  # degrees
    hang = np.random.uniform(s.HANG_RANGE[0], s.HANG_RANGE[1])  # degrees
    dist = np.random.uniform(s.DIST_RANGE[0], s.DIST_RANGE[1])  # meters
    
    # Intruder state
    h1 = np.random.uniform(s.INTRUDER_HEADING[0], s.INTRUDER_HEADING[1])  # degrees
    intruder = get_intruder_position(ownship, dist, hang, vang, h1)

    return ownship, intruder, vang, hang, dist

def gen_data(client):
    """Generates dataset based on parameters in settings.py

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    """

    screen_shot = mss.mss()
    csv_file = s.OUTDIR + 'state_data.csv'
    with open(csv_file, 'w') as fd:
        fd.write("filename,e0,n0,u0,h0,p0,r0,vang,hang,z,e1,n1,u1,h1\n")

    for i in range(s.NUM_SAMPLES):
        # Sample random state
        ownship, intruder, vang, hang, z = sample_random_state()

        # Position the aircraft
        zulu_time = s.TIME_OPTIONS[s.REGION_CHOICE] * 3600
        zulu_time += np.random.uniform(s.TIME_OF_DAY_START * 3600, s.TIME_OF_DAY_END * 3600)
        client.sendDREF("sim/time/zulu_time_sec", zulu_time)
        set_position(client, ownship)
        set_position(client, intruder)

        # Pause and then take the screenshot
        time.sleep(s.PAUSE_2)
        time.sleep(1)
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[12:-12, :, :]

        # Write the screenshot to a file
        print('%simgs/%d.jpg' % (s.OUTDIR, i))
        cv2.imwrite('%simgs/%d.jpg' % (s.OUTDIR, i), ss)
        
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, ownship.e, ownship.n, ownship.u, ownship.h, ownship.p, ownship.r, vang, hang, z, intruder.e, intruder.n, intruder.u, intruder.h))

def run_data_generation(client):
    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)

    set_position(client, Aircraft(1, 0, 0, 0, 0, pitch=0, roll=0))
    set_position(client, Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0))

    time.sleep(s.PAUSE_1)

    gen_data(client)

def printOwnshipPosition(client):
    lat = client.getDREF("sim/flightmodel/position/latitude")[0]
    lon = client.getDREF("sim/flightmodel/position/longitude")[0]
    elev = client.getDREF("sim/flightmodel/position/elevation")[0]
    y_agl = client.getDREF("sim/flightmodel/position/y_agl")[0]
    print("Lat: %.14f" % lat)
    print("Lon: %.14f" % lon)
    print("Elevation: %.14f" % elev)
    print("y_agl: %.14f" % y_agl)
    print("ref: [%.14f, %.14f, %.14f]" % (lat, lon, elev))

def get_fov(client):
    hfov = client.getDREF("sim/graphics/view/field_of_view_deg")
    vfov = client.getDREF("sim/graphics/view/vertical_field_of_view_deg")
    return hfov, vfov

def set_metadata(client):
    hfov, vfov = get_fov(client)
    data = {
        "hfov": hfov[0],
        "vfov": vfov[0]
    }

    json_object = json.dumps(data, indent=4)
 
    # Writing to sample.json
    with open("metadata.json", "w") as outfile:
        outfile.write(json_object)


# code to help obtain new starting positions
def testing_locs(client):
    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)
    get_fov(client)

    o = Aircraft(0, 0, 0, 0, 0, pitch=0, roll=0)
    set_position(client, o)

    for p in range(90):
        for r in range(90):
            for h in range(90):
                o = Aircraft(0, 0, 0, 0, h, pitch=p, roll=r)
                i = Aircraft(1, 0, 20, 0, 0, pitch=0, roll=0)
                set_position(client, o)
                i = get_intruder_position(o, 60.0, 10, 10, 0)
                set_position(client, i)
                time.sleep(0.02)

    return


    print(o)
    set_position(client, o)
    i = Aircraft(1, 0, 20, 0, 0, pitch=0, roll=0)
    set_position(client, i)
    #time.sleep(2)
    i = get_intruder_position(o, 20, 0, 0, 0)
    print(i)
    set_position(client, i)

if __name__ == "__main__":
    client = XPlaneConnect()
    set_metadata(client)

    #testing_locs(client)
    run_data_generation(client)