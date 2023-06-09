import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
from .utils import *
import math
import argparse

def sampler():
    '''returns random encounter information'''

    v0 = np.random.uniform(60, 70) # horizontal velocity of ownship (m/s)
    v1 = np.random.uniform(60, 70) # horizontal velocity of intruder (m/s)
    hmd = np.random.uniform(0, 100) # horizontal miss distance (m)
    vmd = np.random.uniform(-30, 30) # vertical miss distance (m)
    theta_cpa = np.random.uniform(100, 260) # relative heading at closest point of approach
    t_cpa = 40 # time at closest point of approach
    t_tot = 50 # total number of timesteps
    return EncounterDescription(v0, v1, hmd, vmd, theta_cpa, t_cpa, t_tot)


def get_encounter_states(enc_des, dt=1):
    '''
    Parameters
    ----------
    enc_des : EncounterDescription
        properties of the encounter

    Returns
    -------
    Encounter : resulting encounter
    '''

    num_steps = int(enc_des.t_tot / dt)

    # Assumption : ownship starts at origin at "closest point of approach" time
    ownship_2d_cpa = [0.0, 0.0]
    theta_rad = np.deg2rad(enc_des.theta_cpa)
    intruder_2d_cpa = [enc_des.hmd * np.sin(theta_rad),
                       enc_des.hmd * np.cos(theta_rad)]
    '''intruder_2d_cpa = [enc_des.hmd * -np.sin(theta_rad),
                       enc_des.hmd * np.cos(theta_rad)]'''

    # Assumption : default "forward" heading is along y axis
    ownship_heading = [0.0, 1.0]

    # Assumption: Intruder Ship's heading points directly along relative heading vector
    intruder_heading = normalize(
        [np.subtract(intruder_2d_cpa, ownship_2d_cpa)])[0]

    ownship_vel = np.multiply(ownship_heading, enc_des.v0 * dt)
    intruder_vel = np.multiply(intruder_heading, enc_des.v1 * dt)
    timestep_cpa = int(enc_des.t_cpa / dt)

    # Warning: Ships may end up getting closer after "closest point of approach", but we assume we don't care
    ownship_2d = [ownship_2d_cpa + i *
                  ownship_vel for i in range(-timestep_cpa + 1, num_steps-timestep_cpa + 1)]
    intruder_2d = [intruder_2d_cpa + i *
                   intruder_vel for i in range(-timestep_cpa + 1, num_steps-timestep_cpa + 1)]

    x0 = [p[0] for p in ownship_2d]
    y0 = [p[1] for p in ownship_2d]
    z0 = np.zeros(num_steps)
    theta_0 = np.zeros(num_steps)
    v0 = np.full(num_steps, enc_des.v0)
    dh0 = np.zeros(num_steps)
    own_data = np.transpose([x0, y0, z0, v0, dh0, theta_0])

    x1 = [p[0] for p in intruder_2d]
    y1 = [p[1] for p in intruder_2d]
    z1 = np.full(num_steps, enc_des.vmd)
    theta_1 = np.full(num_steps, enc_des.theta_cpa)
    v1 = np.full(num_steps, enc_des.v1)
    dh1 = np.zeros(num_steps)
    intr_data = np.transpose([x1, y1, z1, v1, dh1, theta_1])

    a = np.zeros(num_steps)

    return Encounter(own_data, intr_data, a)


def rotate_and_shift(enc, theta, shift):
    '''
    Rotates encounters by theta and shifts by shift

    Parameters
    ----------
    enc : Encounter
        encounter to be transformed
    theta : float
        angle by which to rotate enc
    shift : list[float]
        x, y, z by which to shift enc

    Returns
    -------
    Encounter : resulting encounter after transformation
    '''

    p0 = enc.own_data[:, 0:3].T
    p1 = enc.intr_data[:, 0:3].T

    # rotate
    theta_rad = np.deg2rad(-theta) # make negative to turn rotation into heading rotation
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    R = np.matrix([[c, -s, 0], [s, c,0], [0,0,1]])
    p0r = np.matmul(R, p0)
    p1r = np.matmul(R, p1)

    # shift
    p0rs = p0r + np.tile(shift, (len(enc.own_data), 1)).T
    p1rs = p1r + np.tile(shift, (len(enc.own_data), 1)).T

    theta_0 = np.full(len(enc.own_data), theta)
    theta_1 = enc.intr_data[:, 5] + theta

    enc.own_data[:, 0:3] = p0rs.T
    enc.intr_data[:, 0:3] = p1rs.T
    enc.own_data[:, 5] = theta_0
    enc.intr_data[:, 5] = theta_1
    return enc


def rotate_and_shift_encs(encs):
    '''Initiates rotation and shifting of encounters by random values each call'''

    new_encs = [rotate_and_shift(enc, np.random.uniform(0.0, 360.0), [np.random.uniform(-5000.0, 5000.0), np.random.uniform(-5000.0,
                                                                   5000.0), np.random.uniform(-500.0, 500.0)]) for enc in encs]
    return new_encs


def get_encounter_set(num_encs):
    '''Calls to get_encounter_states to generate list of encounters'''

    encs = [get_encounter_states(sampler()) for i in range(num_encs)]
    return encs

def plot_10_encs(encs):
    '''Helper function for visualizing a maximum of 10 encounters'''
    cols = 2
    figure, axis = plt.subplots(5, cols)
    for i in range(10 if args.num_encs > 10 else args.num_encs):
        ax = axis[math.floor(i/cols)][i - (math.floor(i/cols))*cols]
        encs[i].create_xy_plot(
            axis[math.floor(i/cols)][i - (math.floor(i/cols))*cols])
        ax.set_aspect('equal', adjustable='datalim')

def generate_new_encounter_set(num_encs, prefix, subfolder):
    encs = get_encounter_set(num_encs=num_encs)
    encs = rotate_and_shift_encs(encs)
    i = 0
    while os.path.exists(os.path.join("encounter_sets", subfolder, f'{prefix}_{i}.csv')):
        i += 1
    path = os.path.join("encounter_sets", subfolder, f'{prefix}_{i}.csv')
    output_file(encs, path=path)
    return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num", dest="num_encs", default=10, help="Specify number of encounters to generate", type=int)
    parser.add_argument("-f", "--filename", dest="outfile", default="encounters", help="Specify name of output file to be placed in the encounter_sets directory without the filetype suffix (e.g. encounters not encounters.txt)", type=str)
    global args
    args = parser.parse_args()

    encs = get_encounter_set(args.num_encs)
    encs = rotate_and_shift_encs(encs)
    output_file(encs, args.outfile)
    print(f"{args.num_encs} encounters generated and saved to encounter_sets/{args.outfile}.csv")
    
    plot_10_encs(encs)
    plt.show()
