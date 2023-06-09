from constants import Advisories, g
from encounter_model.utils import Encounter
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
from clearml import Task

# import controllers
from controllers.VCAS import VCAS
from controllers.BasicController import BasicController

# import perception systems
from perception.XPlanePerception import XPlanePerception
from perception.PerfectPerception import PerfectPerception

import argparse
from evaluation import runEval
from encounter_model.straight_line_model import generate_new_encounter_set

def get_next_own_state(x0_prime, y0_prime, s_own, action):
    '''Gets next ownship state based on current state and advisory provided'''

    a0 = 0
    dh0 = s_own[4]
    if action == Advisories.COC:  # flatten out
        if dh0 > 0:
            a0 = -dh0 if dh0 < g/3 else -g/3
        elif dh0 < 0:
            a0 = -dh0 if dh0 > -g/3 else g/3
    elif action in [Advisories.DNC, Advisories.DND]:  # flatten out
        if dh0 > 0:
            a0 = -min(g/3, dh0)
        elif dh0 < 0:
            a0 = min(g/3, -dh0)
    elif action in [Advisories.CL1500, Advisories.SCL1500]:  # climb
        if dh0 < 7.62:
            a0 = min(g/3, 7.62-dh0)
    elif action in [Advisories.DES1500, Advisories.SDES1500]:  # descend
        if dh0 > -7.62:
            a0 = -min(g/3, 7.62+dh0)
    elif action == Advisories.SDES2500:  # descend faster
        if dh0 > -12.7:
            a0 = -min(g/2.5, 12.7+dh0)
    elif action == Advisories.SCL2500:  # climb faster
        if dh0 < 12.7:
            a0 = min(g/2.5, 12.7-dh0)

    z0 = s_own[2]
    dh0_prime = a0 + dh0
    z0_prime = a0 + dh0 + z0

    v0, theta0 = s_own[3], s_own[5]

    s_own_prime = np.array(
        [x0_prime, y0_prime, z0_prime, v0, dh0_prime, theta0])

    return s_own_prime


def run_simulator(encs):
    '''Runs simulation'''
    if args.clearml:
        task_name = "MAC run simulation with single eval"
        task = Task.init(project_name="simulation", task_name=task_name, continue_last_task=True)

    output_encs = []
    controller = VCAS()
    perceptor = XPlanePerception(args)
    enc_num = 1

    for enc in encs:
        # for choosing one encounter to run
        if args.enc_idx is not None and enc_num != args.enc_idx:
            enc_num += 1
            continue
        print(f"Simulating encounter #{enc_num}")
        enc_prime = Encounter()
        diverged = False
        s_own_prime = 0
        action = Advisories.COC

        # set time
        perceptor.set_time()
        
        for t in range(enc.get_ttot()):
            # PERCEPTION: prepare state attributes and perceive
            s_own = s_own_prime if diverged else enc.get_ownship_state(t)
            a_prev = enc_prime.get_a_prev(t)
            s_intr_hat = perceptor.perceiveIntruderState(
                s_own, enc.get_intruder_state(t), args.enc_idx)
            
            if s_intr_hat is None:
                # intruder not detected by perception system
                action = Advisories.COC
            else: 
                # CONTROLLER: retrieve action from controller policy
                state = controller.getStateForPolicy(s_own, s_intr_hat, a_prev)
                action = controller.getActionFromPolicy(state)

            enc_prime.append_timestep(
                s_own,  enc.get_intruder_state(t), action) # current state and resulting action

            # check if diverged from encounter or encounter is complete
            if (action != Advisories.COC):
                diverged = True
            if t == enc.get_ttot() - 1:
                break

            # perform action and get new states
            x0_prime, y0_prime = enc.get_ownship_state(
                t + 1)[0], enc.get_ownship_state(t + 1)[1]
            s_own_prime = get_next_own_state(x0_prime, y0_prime,
                                             s_own, action)
            
        output_encs.append(enc_prime)
        perceptor.evalEnc(enc_prime, enc_num, args)
        if args.clearml: 
            task.get_logger().report_table(title='single results',series='singleresults',csv=f"./{args.fname}.csv")
        enc_num += 1
    
    del perceptor

    output_encs = np.array(output_encs)
    runEval(output_encs)
    if args.clearml:
        task.get_logger().report_table(title='simulation results',series='results',csv='./eval_results.csv')
    del controller
    # plot graphs
    return
    if args.enc_idx is not None:
        perceptor.make_gif('encounter' + str(args.enc_idx) + '.gif')
        output_encs[0].create_tz_plot(plt)
        plt.xlabel("Time (s)")
        plt.ylabel("Altitude relative to origin (m)")
        plt.show()
    else: 
        cols = 2
        total = 10
        figure, axis = plt.subplots(5, cols)
        for i in range(total):
            output_encs[i].create_tz_plot(
                axis[math.floor(i/cols)][i - (math.floor(i/cols))*cols])
        plt.show()


def import_encounter_set(dir):
    '''Converts encounter.csv file to a list of encounter objects'''

    df = pd.read_csv(dir)
    num_encs = df.enc_number.max()
    encs_list = []
    for i in range(1, num_encs + 1):
        enc_row = df[df.enc_number == i]
        encs_list.append(Encounter(enc_row[enc_row.columns[2:8]].to_numpy(),
                                   enc_row[enc_row.columns[8:14]].to_numpy(), enc_row['advisory'].to_numpy()))
    return encs_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--enc_idx", dest="enc_idx", default=None, type=int)
    parser.add_argument("-w", "--weather", dest="weather", default=0, type=int)
    parser.add_argument("-t", "--time", dest="time", default=None, help="Local time at which encounters should start (e.g. 8.0 = 8AM, 17.0 = 5PM)", type=float)
    parser.add_argument("-l", "--location", dest="location", default = "Palo Alto", help="Airport Location (Options: Palo Alto, Osh Kosh, Boston, and Reno Tahoe)", type=str)
    parser.add_argument("-tod", "--tod", dest="time_window", default = "morning", help="morning, midday, earlyafternoon, or lateafternoon", type=str)
    parser.add_argument("-m", "--model", dest="model_path", default="../../models/baseline.pt", help="path to model", type=str)
    parser.add_argument("-f", "--outfilename", dest="fname", default="per_enc_eval", help="Outfile name for encounter simulation results, without filetype suffix.", type=str)
    parser.add_argument("-xp", dest="xp", help="Use this flag to enable XPlane customization.", action='store_true')
    parser.add_argument("-c", dest="clearml", help="Use clearml", action='store_true')
    parser.add_argument("-ed", "--encsdir", dest="encs_dir", default="./encounter_sets/simulation_encs", help="path to encounters for simulation", type=str)
    global args
    args = parser.parse_args()

    ## BULK SIMULATION VARIABLE SETUP
    ## (will override associated command line args)
    args.craft = "Boeing 737-800"
    args.encs_dir = generate_new_encounter_set(30, 'encset', 'simulation_encs')
    args.model_path = "../../models/baseline.pt"
    args.fname = 'per_enc_eval'

    encs = import_encounter_set(args.encs_dir)
    run_simulator(encs)

