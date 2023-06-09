import numpy as np
from constants import Advisories, g

class BasicController:
    def compute_euclidean(x, y):
        '''Helper function to compute euclidean distance between ownship and intruder'''
        return np.sqrt(np.sum((x-y)**2))

    def getStateForPolicy(self, s_own, s_int, a_prev):
        '''Returns controller state based on encounter state'''
        return (s_own, s_int)

    def getActionFromPolicy(self, state):
        '''Looks at vertical and horizontal distance between crafts to determine ownship advisory'''
        (s_own, s_intr_hat) = state
        y_diff = s_own[2] - s_intr_hat[2]  # vertical distance
        h_diff = BasicController.compute_euclidean(np.array(s_own[0], s_own[1]), np.array(
            s_intr_hat[0], s_intr_hat[1]))  # horizontal distance

        # within 600 feet vertically and 2.1 nmi horizontally
        if abs(y_diff) <= 182.9 and h_diff <= 3889.2:
            if y_diff > 0:  # own is above intr
                return Advisories.CL1500
            else:
                return Advisories.DES1500

        if abs(y_diff) > 182.9:
            return Advisories.COC

        return Advisories.COC
