from encounter_model.utils import Encounter
import numpy as np

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

    print(f"NMACs: {nmacs} out of {len(simulated_encs)} encounters resulted in near mid-air collisions")

    return nmacs

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
    print(f"Alerts: The pilot saw an advisory {alert_frac * 100}% of the time.")

    return alert_frac

def runEval(encs):
    print ("EVALUATION")
    evalAlertFrequency(encs)
    evalNMACs(encs)
