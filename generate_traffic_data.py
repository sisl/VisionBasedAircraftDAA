# TODO: 


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

def set_position(client, ac, e, n, u, psi, pitch=-998, roll=-998):
    ref = [37.46358871459961, -122.11750030517578, 1578.909423828125] #PARAMS
    p = pm.enu2geodetic(e, n, u, ref[0], ref[1], ref[2])
    client.sendPOSI([*p, pitch, roll, psi], ac)


def get_intruder_position(e0, n0, u0, h0, z, hang, vang):
    e1 = z * np.tan(hang * (np.pi / 180))
    n1 = z
    u1 = z * np.tan(vang * (np.pi / 180))

    # Rotate
    n1 = (z / np.cos(hang * (np.pi / 180))) * \
        np.cos((h0 + hang) * (np.pi / 180))
    e1 = (z / np.cos(hang * (np.pi / 180))) * \
        np.sin((h0 + hang) * (np.pi / 180))

    # Translate
    e1 += e0
    n1 += n0
    u1 += u0

    return e1, n1, u1


def sample_random_state():
    # Ownship state
    e0 = np.random.uniform(-5000.0, 5000.0)  # m
    n0 = np.random.uniform(-5000.0, 5000.0)  # m
    u0 = np.random.uniform(-500.0, 500.0)  # m
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


def sample_random_uniform_state():
    # h and tau
    h = np.random.uniform(-300, 300)
    tau = np.random.uniform(0, 40)

    v0 = np.random.uniform(45, 55)
    v1 = np.random.uniform(45, 55)
    theta = np.random.uniform(100 * (np.pi / 180), 260 * (np.pi / 190))

    b = -v1 * np.sin(theta) * tau
    a = b * (v0 - v1 * np.cos(theta)) / (-v1 * np.sin(theta))

    r = np.sqrt(a ** 2 + b ** 2)

    # Ownship state
    e0 = np.random.uniform(-5000.0, 5000.0)  # m
    n0 = np.random.uniform(-5000.0, 5000.0)  # m
    u0 = np.random.uniform(-500.0, 500.0)  # m
    h0 = np.random.uniform(0.0, 360.0)  # degrees

    # Intruder state
    # Rotate
    e1 = a * np.cos((90 - h0) * np.pi / 180) - b * np.sin((90 - h0) * np.pi / 180)
    n1 = a * np.sin((90 - h0) * np.pi / 180) + b * np.cos((90 - h0) * np.pi / 180)

    # Translate
    e1 = e1 + e0
    n1 = n1 + n0
    u1 = h + u0

    h1 = np.random.uniform(0.0, 360.0)  # degrees

    return e0, n0, u0, h0, e1, n1, u1, h1, h, tau, r


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
        client.sendDREF("sim/time/zulu_time_sec", 9.0*3600 + 8*3600)
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


def gen_data_uniform(client, npoints, outdir):
    screen_shot = mss.mss()
    csv_file = outdir + 'state_data.csv'
    with open(csv_file, 'w') as fd:
        fd.write("filename,e0,n0,u0,h0,e1,n1,u1,h1,h,tau,r\n")

    for i in range(npoints):
        # Sample random state
        e0, n0, u0, h0, e1, n1, u1, h1, h, tau, r = sample_random_uniform_state()

        # Position the aircraft
        client.sendDREF("sim/time/zulu_time_sec", 9.0*3600 + 8*3600)
        set_position(client, 0, e0, n0, u0, h0)
        set_position(client, 1, e1, n1, u1, h1)

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
                     (i, e0, n0, u0, h0, e1, n1, u1, h1, h, tau, r))


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

outdir = "/scratch/smkatz/yolo_data/val_data/" # make sure this exists
outdir = "datasets/"

npoints = 10

time.sleep(3)

#state_file = "/home/smkatz/Documents/RiskSensitivePerception/collision_avoidance/data_files/risk_data_states_v3.csv"

#gen_data_uniform(client, npoints, outdir)
#gen_data_from_states(client, state_file, outdir)
#np.random.seed(3)
gen_data(client, npoints, outdir)
