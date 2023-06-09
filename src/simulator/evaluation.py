from encounter_model.utils import Encounter
import numpy as np

def output_to_file(msg, reset=False):
    '''Prints evaluation to output file'''

    permission = 'a'
    if reset: permission = 'w'
    with open(f"eval_results.csv", permission) as outfile:
        outfile.write(msg)

def output_enc_result(msg, fname, reset=False):
    permission = 'a'
    if reset: permission = 'w'
    with open(f"{fname}", permission) as outfile:
        outfile.write(msg)

'''returns number of NMACs'''
def evalNMACs(simulated_encs: list[Encounter]):
    nmacs = 0
    for se in simulated_encs:
        own_data = se.own_data
        intr_data = se.intr_data
        
        # check vertical distances within 100 feet (30.5 m)
        z_dists = own_data[:, 2] - intr_data[:, 2]
        z_nmac_idxs = [i for i in range(len(z_dists)) if abs(z_dists[i]) < 30.5]

        # check horizontal distances within 500 feet (152.4 m)
        xy_dists = own_data[:, 0:2] - intr_data[:, 0:2]
        xy_dists = [np.sqrt(xy[0]**2 + xy[1]**2) for xy in xy_dists]
        xy_nmac_idxs = [i for i in range(len(xy_dists)) if abs(xy_dists[i]) < 152.4]

        # check for NMACs (both vertically and horizontal too close)
        for z in z_nmac_idxs:
            if z in xy_nmac_idxs:
                nmacs += 1
                break

    print(f"NMACs: {nmacs} out of {len(simulated_encs)} encounters resulted in near mid-air collisions\n")
    output_to_file(f'{nmacs}\n')
    return nmacs

def evalSingleAlertFrequency(enc: Encounter, fname):
    alert_count = 0
    timestep_count = 0
    alerts = enc.advisories
    alert_count += np.count_nonzero(alerts)
    timestep_count = enc.get_ttot()
    output_enc_result(f'{alert_count / timestep_count},', fname)

def evalSingleNMAC(enc: Encounter, fname):
    own_data = enc.own_data
    intr_data = enc.intr_data
        
    # check vertical distances within 100 feet (30.5 m)
    z_dists = own_data[:, 2] - intr_data[:, 2]
    z_nmac_idxs = [i for i in range(len(z_dists)) if abs(z_dists[i]) < 30.5]

    # check horizontal distances within 500 feet (152.4 m)
    xy_dists = own_data[:, 0:2] - intr_data[:, 0:2]
    xy_dists = [np.sqrt(xy[0]**2 + xy[1]**2) for xy in xy_dists]
    xy_nmac_idxs = [i for i in range(len(xy_dists)) if abs(xy_dists[i]) < 152.4]

    # check for NMACs (both vertically and horizontal too close)
    for z in z_nmac_idxs:
        if z in xy_nmac_idxs:
            output_enc_result(f"1\n", fname)
            return
    output_enc_result(f"0\n", fname)


'''returns fraction of timesteps that had a non-COC alert'''
def evalAlertFrequency(simulated_encs: list[Encounter]):
    alert_count = 0
    coc_count = 0
    timestep_count = 0
    for se in simulated_encs:
        alerts = se.advisories
        alert_count += np.count_nonzero(alerts)
        coc_count += len(alerts)
        timestep_count += se.get_ttot()

    alert_frac = alert_count / timestep_count
    print(f"Alerts: The pilot saw an advisory {alert_frac * 100}% of the time.\n")
    output_to_file(f"{alert_frac},")
    return alert_frac

def runEval(encs, when, args):
    print ("EVALUATION")
    output_to_file(f'{when},{len(encs)},{args.weather},{args.location},{args.time_window},')
    evalAlertFrequency(encs)
    evalNMACs(encs)

def evalSingle(enc, enc_num, args):
    fname = 'v5_per_enc_eval.csv'
    if args.yolov8:
        fname = 'per_enc_eval.csv'
    output_enc_result(f'{enc_num},{args.weather},{args.location},{args.time_window},', fname)
    evalSingleAlertFrequency(enc, fname)
    evalSingleNMAC(enc, fname)
