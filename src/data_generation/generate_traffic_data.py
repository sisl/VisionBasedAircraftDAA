# TODO: intruder position
# TODO: clean up file
# TODO: 1920x1080 screen resolution before taking pictures

import mss
import cv2
import pymap3d as pm

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

def get_intruder_position(ownship, r, hang, vang):
    inclination = np.deg2rad(90-vang)
    azimuth = np.deg2rad(90-hang)

    # Set initial cartesian coordinates
    e1 = r * np.sin(inclination) * np.cos(azimuth) + ownship.e
    n1 = r * np.sin(inclination) * np.sin(azimuth) + ownship.n
    u1 = r * np.cos(inclination) + ownship.u

    # Rotate according to Tate Bryant Convention
    intruder = np.array([e1, n1, u1]).reshape(-1, 1)
    intruder = np.matmul(rot_matrix('z', ownship.h), intruder)
    intruder = np.matmul(rot_matrix('x', ownship.p), intruder)
    intruder = np.matmul(rot_matrix('y', ownship.r), intruder)
    return Aircraft(1, float(intruder[0]), float(intruder[1]), float(intruder[2]), 0)

'''OLD. Delete?
def get_intruder_position(e0, n0, u0, h0, r, hang, vang, p0, r0):
    """Generates intruder position based on ownship and relative angles
    
    Parameters
    ----------
    e0, n0, u0 : float
        eastward, northward, and upward distance of ownship from origin location in meters 
    h0 : float
        heading of ownship in degrees
    z : int
        diagonal distance of intruder from ownship in meters (as the crow flies?)
    hang, vang : float
        horizontal and vertical angle of intruder from ownship in degrees
    p0, r0 : int
        pitch and roll of ownship in degrees
    
    Returns
    -------
    e1, n1, u1 : float
        eastward, northward, an dupward position of intruder from origin in meters
    """

    inclination = np.deg2rad(vang)
    azimuth = np.deg2rad(hang)
    e1 = r * np.sin(inclination) * np.cos(azimuth)
    n1 = r * np.sin(inclination) * np.sin(azimuth)
    u1 = r * np.cos(inclination)

    # Rotate
    intruder = np.array([e1, n1, u1]).reshape(-1,1)
    intruder = np.matmul(rot_matrix('y', r0), intruder)
    intruder = np.matmul(rot_matrix('x', p0), intruder)
    intruder = np.matmul(rot_matrix('z', h0), intruder)
    return intruder[0], intruder[1], intruder[2]


    # BELOW THIS IS WHAT WAS HERE BEFORE
    e1 = z * np.tan(np.rad2deg(hang))
    n1 = z
    u1 = z * np.tan(np.rad2deg(vang))

    # Rotate
    n1 = (z / np.cos(np.rad2deg(hang))) * \
        np.cos(np.rad2deg(h0 + hang))
    e1 = (z / np.cos(np.rad2deg(hang))) * \
        np.sin(np.rad2deg(h0 + hang))

    # Translate
    e1 += e0
    n1 += n0
    u1 += u0

    return e1, n1, u1'''

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
    intruder = get_intruder_position(ownship, dist, hang, vang)
    h1 = np.random.uniform(s.INTRUDER_HEADING[0], s.INTRUDER_HEADING[1])  # degrees

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
        fd.write("filename,e0,n0,u0,h0,vang,hang,z,e1,n1,u1,h1\n")

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
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[12:-12, :, :]

        # Write the screenshot to a file
        print('%simgs/%d.jpg' % (s.OUTDIR, i))
        cv2.imwrite('%simgs/%d.jpg' % (s.OUTDIR, i), ss)
        
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, ownship.e, ownship.n, ownship.u, ownship.h, vang, hang, z, intruder.e, intruder.n, intruder.u, intruder.h))

def run_data_generation():
    client = XPlaneConnect()
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

# code to help obtain new starting positions
def testing_locs():
    client = XPlaneConnect()
    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)

    o = Aircraft(0, 0, 0, 0, 14, pitch=-30, roll=30)
    print(o)
    i = Aircraft(1, 0, 10, 0, 0, pitch=0, roll=0)
    i = get_intruder_position(o, 20, -30, 30)
    print(i)
    set_position(client, i)

if __name__ == "__main__":
    testing_locs()
    #run_data_generation()