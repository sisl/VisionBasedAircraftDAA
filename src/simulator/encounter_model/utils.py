import numpy as np
import matplotlib.pyplot as plt
import os

class EncounterDescription:
    '''Class used to organize metadata about the encounter set as it is generated'''

    def __init__(self, v0, v1, hmd, vmd, theta_cpa, t_cpa, t_tot):
        self.v0 = v0  # ownship horizontal speed (m/s)
        self.v1 = v1  # intruder horizontal speed (m/s)
        self.hmd = hmd  # horizontal miss distance (m)
        self.vmd = vmd  # vertical miss displacement (m)
        # relative heading at closest point of approach (degrees)
        self.theta_cpa = theta_cpa
        # time into encounter closest point of approach occurs (seconds)
        self.t_cpa = t_cpa
        self.t_tot = t_tot  # total time of the encounter (seconds)


class Encounter:
    '''Class used to organize information about each encounter'''

    def __init__(self, own_data=None, intr_data=None, a=None):
        # matrix of ownship data for each time step ([x, y, z, v, dh, theta])
        self.own_data = own_data
        # matrix of intruder data for each time step ([x, y, z, v, dh, theta])
        self.intr_data = intr_data
        self.advisories = a  # array of advisories

    def __str__(self):
        return f"ownship: \n{np.around(self.own_data, decimals=1)}\n, intruder: \n{np.around(self.intr_data, decimals=1)}\n, advisories: \n{self.advisories}"

    def retrieve_data(self):
        '''returns matrix of the ownship and intruder data'''
        advisories = [[a] for a in self.advisories]

        joined = np.hstack((self.own_data, self.intr_data, advisories))
        return (joined)

    def get_ttot(self):
        '''returns number of timesteps in each encounter'''

        return len(self.own_data)

    def append_timestep(self, s_own, s_intr, a):
        '''Adding a timestep of data to the encounter'''

        if self.own_data is None or self.intr_data is None or self.advisories is None:
            self.own_data = [s_own]
            self.intr_data = [s_intr]
            self.advisories = [a]
        else:
            self.own_data = np.append(self.own_data, [s_own], axis=0)
            self.intr_data = np.append(self.intr_data, [s_intr], axis=0)
            self.advisories = np.append(self.advisories, [a], axis=0)

    def get_ownship_state(self, index):
        '''Retrieves ownship data'''

        return self.own_data[index]

    def get_intruder_state(self, index):
        '''Retrieves intruder data'''

        return self.intr_data[index]

    def get_a_prev(self, index):
        '''Retrieves previous advisory issued'''

        if index > 0 and self.advisories is not None and index <= len(self.advisories):
            return self.advisories[index - 1]
        else:
            return 0

    def create_xy_plot(self, axis):
        '''Helper function for outputting groundtrack plot of aircraft encounter (view form above)'''

        own, = axis.plot(self.own_data[:, 0], self.own_data[:, 1], 'r', label=self.own_data[0,5])
        intr, = axis.plot(self.intr_data[:, 0], self.intr_data[:, 1], 'b', label=self.intr_data[0,5])
        axis.legend(handles=[own, intr])

    def create_tz_plot(self, axis):
        '''Helper function for outputting vertical profile plot of encounter'''

        own, = axis.plot([t for t in range(self.get_ttot())],
                  self.own_data[:, 2], 'r-', label="ownship")
        detected_x = [t for t in range(self.get_ttot()) if self.advisories[t] != 0]
        detected_y = [self.own_data[t, 2] for t in detected_x]
        detect, = axis.plot(detected_x, detected_y, 'ro', label="intruder was detected by ownship")
        intr, = axis.plot([t for t in range(self.get_ttot())],
                  self.intr_data[:, 2], 'b-', label="intruder")
        axis.legend(handles=[own, intr, detect])

def output_file(encs, name):
    '''Helper function for outputting encounter set to csv file'''
    
    csv_file = os.path.join("..", "encounter_sets", name + '.csv')
    with open(csv_file, 'w+') as fd:
        fd.write("enc_number,t,x0,y0,z0,v0,dh0,theta0,x1,y1,z1,v1,dh1,theta1,advisory\n")
    with open(csv_file, 'a') as fd:
        num = 1
        for enc in encs:
            enc_data = enc.retrieve_data()
            for t in range(len(enc_data)):
                fd.write(
                    f"{str(num)},{t},{','.join([str(s) for s in enc_data[t]])}\n")
            num += 1
