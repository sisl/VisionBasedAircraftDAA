# DONE: git ignore the datasets / extra files
# TODO: config file for parameters

import settings
from xpc3 import *
from xpc3_helper import *
from PIL import Image
import numpy as np
import time
import matplotlib.pyplot as plt
import mss
import cv2
import os
import pymap3d as pm
import pandas as pd

def rads_to_degs(degs):
    return degs * (np.pi / 180)

def set_position(client, ac, e, n, u, psi, pitch=-998, roll=-998):
    ref = settings.REGION_OPTIONS[settings.REGION_CHOICE]
    p = pm.enu2geodetic(e, n, u, ref[0], ref[1], ref[2]) #east, north, up, 
    client.sendPOSI([*p, pitch, roll, psi], ac) #psi=ya (heading)


def get_intruder_position(e0, n0, u0, h0, z, hang, vang):
    e1 = z * np.tan(rads_to_degs(hang))
    n1 = z
    u1 = z * np.tan(rads_to_degs(vang))

    # Rotate
    n1 = (z / np.cos(rads_to_degs(hang))) * \
        np.cos(rads_to_degs(h0 + hang))
    e1 = (z / np.cos(rads_to_degs(hang))) * \
        np.sin(rads_to_degs(h0 + hang))

    # Translate
    e1 += e0
    n1 += n0
    u1 += u0

    return e1, n1, u1

def sample_random_state():
    # Ownship state
    e0 = np.random.uniform(-settings.EAST_RANGE, settings.EAST_RANGE)  # m
    n0 = np.random.uniform(-settings.NORTH_RANGE, settings.NORTH_RANGE)  # m
    u0 = np.random.uniform(-settings.UP_RANGE, settings.UP_RANGE)  # m
    h0 = np.random.uniform(0.0, 360.0)  # degrees

    # Info about relative position of intruder
    vang = np.random.uniform(-25.0, 25.0)  # degrees
    hang = np.random.uniform(-38.0, 38.0)  # degrees
    z = np.random.uniform(20, 2000)  # meters
    # while z < 20.0:
    #     z = np.random.gamma(2, 200)  # meters

    # Intruder state
    e1, n1, u1 = get_intruder_position(e0, n0, u0, h0, z, hang, vang)
    h1 = np.random.uniform(0.0, 360.0)  # degrees

    return e0, n0, u0, h0, vang, hang, z, e1, n1, u1, h1

def gen_data(client, npoints, outdir):
    screen_shot = mss.mss()
    csv_file = outdir + 'state_data.csv'
    print("0")
    with open(csv_file, 'w') as fd:
        fd.write("filename,e0,n0,u0,h0,vang,hang,z,e1,n1,u1,h1\n")

    for i in range(npoints):
        # Sample random state
        e0, n0, u0, h0, vang, hang, z, e1, n1, u1, h1 = sample_random_state()

        # Position the aircraft
        #client.sendDREF("sim/time/zulu_time_sec", 9.0*3600 + 8*3600)
        zulu_time = np.random.uniform(settings.TIME_OF_DAY_START * 3600, settings.TIME_OF_DAY_END * 3600)
        client.sendDREF("sim/time/zulu_time_sec", zulu_time)
        set_position(client, 0, e0, n0, u0, h0)
        set_position(client, 1, e1, n1, u1, h1)

        # Pause and then take the screenshot
        time.sleep(0.05)
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[12:-12, :, :]

        # Deal with screen tearing
        ss_sum = np.reshape(np.sum(ss, axis=-1), -1)
        ind = 0
        while np.min(ss_sum) == 0 and ind < 10:
            # print("Screen tearing detected. Trying again...")
            ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[12:-12, :, :]
            ss_sum = np.reshape(np.sum(ss, axis=-1), -1)
            ind += 1

        if np.min(ss_sum) == 0:
            print("Screen tearing on i = ", i)

        # Write the screenshot to a file
        print('%simgs/%d.jpg' % (outdir, i))
        cv2.imwrite('%simgs/%d.jpg' % (outdir, i), ss)
        
        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, e0, n0, u0, h0, vang, hang, z, e1, n1, u1, h1))


def gen_data_from_states(client, state_file, outdir):
    states = pd.read_csv(state_file)
    
    screen_shot = mss.mss()
    csv_file = outdir + 'state_data.csv'
    with open(csv_file, 'w') as fd:
        fd.write("filename,e0,n0,u0,h0,vang,hang,z,e1,n1,u1,h1\n")

    for i in range(len(states)):
        # Position the aircraft
        client.sendDREF("sim/time/zulu_time_sec", 9.0*3600 + 8*3600)
        set_position(client, 0, states['e0'][i], states['n0'][i], states['u0'][i], states['h0'][i])
        set_position(client, 1, states['e1'][i], states['n1'][i], states['u1'][i], states['h1'][i])

        # Pause and then take the screenshot
        time.sleep(0.1)
        ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[12:-12, :, :]

        # Deal with screen tearing
        ss_sum = np.reshape(np.sum(ss, axis=-1), -1)
        ind = 0
        while np.min(ss_sum) == 0 and ind < 10:
            # print("Screen tearing detected. Trying again...")
            ss = np.array(screen_shot.grab(screen_shot.monitors[0]))[
                12:-12, :, :]
            ss_sum = np.reshape(np.sum(ss, axis=-1), -1)
            ind += 1

        if np.min(ss_sum) == 0:
            print("Screen tearing on i = ", i)

        # Write the screenshot to a file
        cv2.imwrite('%simgs/%d.jpg' % (outdir, i), ss)

        # Write to csv file
        with open(csv_file, 'a') as fd:
            fd.write("%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                     (i, states['e0'][i], states['n0'][i], states['u0'][i], states['h0'][i], states['vang'][i], states['hang'][i], states['z'][i], states['e1'][i], states['n1'][i], states['u1'][i], states['h1'][i]))


client = XPlaneConnect()
client.pauseSim(True)
client.sendDREF("sim/operation/override/override_joystick", 1)
set_position(client, 1, 0, 1200, 10, 90, roll=0, pitch=0)
set_position(client, 0, 0, 1200, 10, 90, roll=0, pitch=0)

npoints = 10

time.sleep(3)

#state_file = "/home/smkatz/Documents/RiskSensitivePerception/collision_avoidance/data_files/risk_data_states_v3.csv"

#gen_data_from_states(client, state_file, outdir)
#np.random.seed(3)
gen_data(client, npoints, settings.OUTDIR)