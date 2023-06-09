from enum import IntEnum

# ADVISORY INDICES


class Advisories(IntEnum):
    COC = 0  # clear of conflict
    DNC = 1  # do not climb
    DND = 2  # do not descend
    DES1500 = 3  # descend at 1500 fpm
    CL1500 = 4  # climb at 1500 fpm
    SDES1500 = 5  # descend at 1500 fpm but faster(?)
    SCL1500 = 6  # climb at 1500 fpm but faster(?)
    SDES2500 = 7  # descend at 2500 fpm but faster(?)
    SCL2500 = 8  # descend at 1500 fpm but faster(?)


g = 10.0  # m/s2
