# TODO: move xpc3 and helper to src folder
# TODO: aircraft object
# TODO: intruder position
# TODO: get refs for airports -- PA, BOS, osh kosh, tahoe -- make 0,0,0 be in the air (query for y_agl using getdref, or use getposi)
# TODO: sliders for screen size? 

'''from settings import *
from xpc3 import *
from xpc3_helper import *
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.stats import truncnorm'''
import mss
import cv2
import pymap3d as pm

from data_generation.xpc3 import *
import data_generation.settings as settings
from data_generation.xpc3_helper import *
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.stats import truncnorm


class Aircraft:
    def __init__(self, east, north, up, heading, pitch=-998, roll=-998):
        self.e = east
        self.n = north
        self.u = up
        self.h = heading
        self.p = pitch
        self.r = roll

def set_position(client, ac, e, n, u, yaw, pitch=-998, roll=-998):
    """Sets position of aircraft in XPlane

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    ac : int
        number of aircraft to position
    e : float
        eastward distance from origin location in meters
    n : float
        northward distance from origin location in meters
    u : float
        upward distance from origin location in meters
    yaw : float
        aircraft heading in degrees
    pitch : int (optional)
    roll : int (optional)
    """

    ref = settings.REGION_OPTIONS[settings.REGION_CHOICE]
    p = pm.enu2geodetic(e, n, u, ref[0], ref[1], ref[2]) #east, north, up
    client.sendPOSI([*p, pitch, roll, yaw], ac)


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
    e0 = np.random.uniform(-settings.EAST_RANGE, settings.EAST_RANGE)  # meters
    n0 = np.random.uniform(-settings.NORTH_RANGE, settings.NORTH_RANGE)  # meters
    u0 = np.random.uniform(-settings.UP_RANGE, settings.UP_RANGE)  # meters
    h0 = np.random.uniform(settings.OWNSHIP_HEADING[0], settings.OWNSHIP_HEADING[1])  # degrees
    p0 = truncnorm.rvs(settings.PITCH_RANGE[0], settings.PITCH_RANGE[1], loc=0, scale=30) # degrees
    r0 = truncnorm.rvs(settings.ROLL_RANGE[0], settings.ROLL_RANGE[1], loc=0, scale=30) # degrees
    ownship = Aircraft(e0, n0, u0, h0, p0, r0)

    # Info about relative position of intruder
    vang = np.random.uniform(settings.VANG_RANGE[0], settings.VANG_RANGE[1])  # degrees
    hang = np.random.uniform(settings.HANG_RANGE[0], settings.HANG_RANGE[1])  # degrees
    z = np.random.uniform(settings.DIST_RANGE[0], settings.DIST_RANGE[1])  # meters
    # while z < 20.0:
    #     z = np.random.gamma(2, 200)  # meters

    # Intruder state
    e1, n1, u1 = get_intruder_position(e0, n0, u0, h0, z, hang, vang, p0, r0)
    h1 = np.random.uniform(settings.INTRUDER_HEADING[0], settings.INTRUDER_HEADING[1])  # degrees
    intruder = Aircraft(e1, n1, u1, h1)

    return ownship, intruder, vang, hang, z

def gen_data(client):
    """Generates dataset based on parameters in settings.py

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    """

    screen_shot = mss.mss()
    csv_file = settings.OUTDIR + 'state_data.csv'
    with open(csv_file, 'w') as fd:
        fd.write("filename,e0,n0,u0,h0,vang,hang,z,e1,n1,u1,h1\n")

    for i in range(settings.NUM_SAMPLES):
        # Sample random state
        #e0, n0, u0, h0, p0, r0, vang, hang, z, e1, n1, u1, h1 = sample_random_state()
        ownship, intruder, vang, hang, z = sample_random_state()
        e0, n0, u0, h0, p0, r0 = ownship.e, ownship.n, ownship.u, ownship.h, ownship.p, ownship.r
        e1, n1, u1, h1 = intruder.e, intruder.n, intruder.u, intruder.h

        # Position the aircraft
        zulu_time = settings.TIME_OPTIONS[settings.REGION_CHOICE] * 3600
        zulu_time += np.random.uniform(settings.TIME_OF_DAY_START * 3600, settings.TIME_OF_DAY_END * 3600)
        client.sendDREF("sim/time/zulu_time_sec", zulu_time)
        set_position(client, 0, e0, n0, u0, h0, p0, r0)
        set_position(client, 1, e1, n1, u1, h1)

        # Pause and then take the screenshot
        time.sleep(settings.PAUSE_2)
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[12:-12, :, :]

        # Write the screenshot to a file
        print('%simgs/%d.jpg' % (settings.OUTDIR, i))
        cv2.imwrite('%simgs/%d.jpg' % (settings.OUTDIR, i), ss)
        
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, e0, n0, u0, h0, vang, hang, z, e1, n1, u1, h1))

def run_data_generation():
    client = XPlaneConnect()
    client.pauseSim(True)
    client.sendDREF("sim/operation/override/override_joystick", 1)

    set_position(client, 1, 0, 1200, 10, 90, roll=0, pitch=0)
    set_position(client, 0, 0, 1200, 10, 90, roll=0, pitch=0)

    time.sleep(settings.PAUSE_1)

    gen_data(client)


if __name__ == "__main__":
    run_data_generation()