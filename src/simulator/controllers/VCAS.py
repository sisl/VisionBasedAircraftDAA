import matplotlib.pyplot as plt
import numpy as np
import h5py
import math
from scipy.interpolate import RegularGridInterpolator


class VCAS:
    def __init__(self, nA=9):
        self.interp_dict = []
        self.nA = nA
        self.setupPolicy()

    def setupPolicy(self):
        '''Pre-loads interpolation dictionary for use as advisory policy'''
        acts = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        vels = np.concatenate((np.linspace(-100, -60, 5), np.linspace(-50, -35, 4),
                               np.linspace(-30, 30, 21), np.linspace(35, 50, 4), np.linspace(60, 100, 5)))
        hs = np.concatenate((np.linspace(-8000, -4000, 5), np.linspace(-3000, -1250, 8), np.linspace(-1000, -800, 3), np.linspace(-700, -150, 12),
                            np.linspace(-100, 100, 9), np.linspace(150, 700, 12), np.linspace(800, 1000, 3), np.linspace(1250, 3000, 8), np.linspace(4000, 8000, 5)))
        vowns = vels
        vints = vels
        taus = np.linspace(0, 40, 41)
        q_dims = (len(hs), len(vowns), len(vints),
                  len(acts), len(taus), len(acts))

        q_r = np.zeros(q_dims)
        f = h5py.File("controllers/vcas_values.h5", 'r')
        Q = np.array(f['q'])
        f.close()
        Q = Q.T
        print(Q.shape)
        # Fill in q_r
        q_r = np.reshape(Q, q_dims, order="F")

        # Define Interpolators
        interp_dict = {}
        for i in range(len(acts)):
            interp_dict[i] = RegularGridInterpolator(
                (hs, vowns, vints, acts, taus), q_r[:, :, :, :, :, i], method='linear', bounds_error=False)
        self.interp_dict = interp_dict

    def getActionFromPolicy(self, state):
        '''Returns the action with the highest q-value for the current state'''
        best_action = 0
        best_val = -math.inf
        for i in range(self.nA):
            interp_a = self.interp_dict[i]  # Interpolators start at 1
            curr_val = interp_a(state)
            if curr_val > best_val:
                best_val = curr_val
                best_action = i
        return best_action

    def plot_example(self):
        '''Helper function for generating visualizations of the q-values associated with different states'''
        taus = np.linspace(0, 40, 41)
        hs = np.concatenate((np.linspace(-8000, -4000, 5), np.linspace(-3000, -1250, 8), np.linspace(-1000, -800, 3), np.linspace(-700, -150, 12),
                            np.linspace(-100, 100, 9), np.linspace(150, 700, 12), np.linspace(800, 1000, 3), np.linspace(1250, 3000, 8), np.linspace(4000, 8000, 5)))

        colors = ['white', 'cyan', 'lightgreen', 'dodgerblue',
                  'lime', 'blue', 'forestgreen', 'navy', 'darkgreen']

        while True:
            i0 = input("vowns: ")
            if (i0 == "q"):
                return
            i1 = input("vints: ")
            i2 = input("a_prev: ")
            x_mat = [[] for _ in range(9)]
            y_mat = [[] for _ in range(9)]
            for i in range(len(taus)):
                for l in range(len(hs)):
                    # [h, vown, vint, a_prev, tau]
                    state = [hs[l], float(i0), float(i1), float(i2), taus[i]]
                    a = self.getActionFromPolicy(state)
                    x_mat[a].append(taus[i])
                    y_mat[a].append(hs[l])
            for i in range(len(x_mat)):
                plt.scatter(x_mat[i], y_mat[i], c=colors[i])
            plt.show()

    def getStateForPolicy(self, s_own, s_int, a_prev):
        '''Calculates policy state based on 3D coordinates and velocities of the aircrafts'''
        HNMAC = 100
        ft_per_m = 3.28
        [x0, y0, z0, v0, dh0] = s_own[0:5] * ft_per_m
        [x1, y1, z1, v1, dh1] = s_int[0:5] * ft_per_m
        theta0 = s_own[5]
        theta1 = s_int[5]
        # print(dh0, dh1)

        h = z1 - z0
        dt = 0.1
        r0 = np.array([x0, y0])
        r0_next = r0 + v0 * dt * \
            np.array([-np.sin(np.deg2rad(theta0)), np.cos(np.deg2rad(theta0))])
        r1 = np.array([x1, y1])
        r1_next = r0 + v1 * dt * \
            np.array([-np.sin(np.deg2rad(theta1)), np.cos(np.deg2rad(theta1))])

        r = np.linalg.norm(r0 - r1)
        r_next = np.linalg.norm(r0_next - r1_next)

        r_dot = (r - r_next) / dt
        tau = 0 if r < HNMAC else (r - HNMAC) / r_dot
        if tau < 0:
            tau = math.inf

        # h = relative altitude, dh0/dh1 = change in altitude
        state = [h, dh0, dh1, a_prev, tau]
        return state
