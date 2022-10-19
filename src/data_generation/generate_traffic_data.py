# DONE: move xpc3 and helper to src folder
# DONE: aircraft object
# DONE: added utility funtion for printing location of aircraft
# TODO: intruder position
# DONE: get refs for airports -- PA, BOS, osh kosh, tahoe -- make 0,0,0 be in the air (query for y_agl using getdref, or use getposi)
# TODO: sliders for screen size? 

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

def get_intruder_position(e0, n0, u0, h0, z, hang, vang, p0, r0):
    """Generates intruder position based on ownship and relative angles
    
    Parameters
    ----------
    e0, n0, u0 : float
        eastward, northward, and upward distance of ownship from origin location in meters 
    h0 : float
        heading of ownship in degrees
    z : int
        diagonal distance of intruder from ownship in meters
    hang, vang : float
        horizontal and vertical angle of intruder from ownship in degrees
    p0, r0 : int
        pitch and roll of ownship in degrees
    
    Returns
    -------
    e1, n1, u1 : float
        eastward, northward, an dupward position of intruder from origin in meters
    """

    # shift the intruder by z in the direction that the ownship is facing

    e1 = z * np.tan(np.rad2deg(hang + r0))
    n1 = z
    u1 = z * np.tan(np.rad2deg(vang + p0))

    # Rotate
    n1 = (z / np.cos(np.rad2deg(hang))) * \
        np.cos(np.rad2deg(h0 + hang))
    e1 = (z / np.cos(np.rad2deg(hang))) * \
        np.sin(np.rad2deg(h0 + hang))

    # Translate
    e1 += e0
    n1 += n0
    u1 += u0

    return e1, n1, u1

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
    z : int
        diagonal distance of intruder from ownship in meters
    """

    # Ownship state
    e0 = np.random.uniform(-s.EAST_RANGE, s.EAST_RANGE)  # meters
    n0 = np.random.uniform(-s.NORTH_RANGE, s.NORTH_RANGE)  # meters
    u0 = np.random.uniform(-s.UP_RANGE, s.UP_RANGE)  # meters
    h0 = np.random.uniform(s.OWNSHIP_HEADING[0], s.OWNSHIP_HEADING[1])  # degrees
    p0 = truncnorm.rvs(s.PITCH_RANGE[0], s.PITCH_RANGE[1], loc=0, scale=30) # degrees
    r0 = truncnorm.rvs(s.ROLL_RANGE[0], s.ROLL_RANGE[1], loc=0, scale=30) # degrees
    ownship = Aircraft(0, e0, n0, u0, h0, p0, r0)

    # Info about relative position of intruder
    vang = np.random.uniform(s.VANG_RANGE[0], s.VANG_RANGE[1])  # degrees
    hang = np.random.uniform(s.HANG_RANGE[0], s.HANG_RANGE[1])  # degrees
    z = np.random.uniform(s.DIST_RANGE[0], s.DIST_RANGE[1])  # meters
    # while z < 20.0:
    #     z = np.random.gamma(2, 200)  # meters

    # Intruder state
    e1, n1, u1 = get_intruder_position(e0, n0, u0, h0, z, hang, vang, p0, r0)
    h1 = np.random.uniform(s.INTRUDER_HEADING[0], s.INTRUDER_HEADING[1])  # degrees
    intruder = Aircraft(1, e1, n1, u1, h1)

    return ownship, intruder, vang, hang, z

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

    #printOwnshipPosition(client)
    theta = client.getDREF("sim/flightmodel/position/theta")
    #phi = client.getDREF("sim/flightmodel/position/phi")[0]
    #psi = client.getDREF("sim/flightmodel/position/psi")[0]
    #print("ref: [%.14f, %.14f, %.14f]" % (theta, phi, psi))
    print(theta)

    print("After shifting")
    set_position(client, Aircraft(0, 500, 500, 0, 0, pitch=0, roll=0))
    #printOwnshipPosition(client)

if __name__ == "__main__":
    testing_locs()
   # run_data_generation()