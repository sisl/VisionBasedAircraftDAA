
#OUTDIR = "C:/Users/X-Plane/Desktop/VisionBasedAircraftDAA/datasets/"
OUTDIR = "../datasets/"

REGION_CHOICE = "Osh Kosh"

# OWNSHIP POSITION
# Used to determine location of Ownship from region location
# Will be used to determine distance from location in meters in positive or negative direction
# Entered as a float (i.e. with a decimal) in meters >= 0
EAST_RANGE = 5000.0
NORTH_RANGE = 5000.0
UP_RANGE = 500.0

# OWNSHIP POSITION Cont. 
# all in (min, max) form
OWNSHIP_HEADING = (0.0, 360) # degrees
PITCH_RANGE = (-45, 45) # degrees (-90 = straight down, 90 = straight up)
ROLL_RANGE = (-45, 45) # degrees (-90 = full roll left, 90 = full roll right)

# INTRUDER POSITION
# all in (min, max) form
INTRUDER_HEADING = (0.0, 360.0) # degrees
VANG_RANGE = (-20, 20) # degrees, vertical angle from ownship
HANG_RANGE = (-30, 30) # degrees, horizontal angle from ownship
DIST_RANGE = (20, 500) # meters, diagonal distance from ownship

# TIME OF DAY
# Start and end of range of possible time of day in local time, e.g. 8.0 = 8AM, 17.0 = 5PM
# For each sinsoidal trajectory in the run, the time of day will be sampled uniformly
# from this range
TIME_OF_DAY_START = 8.0
TIME_OF_DAY_END = 17.0

# CLOUD COVER
# (higher numbers are cloudier/darker)
# 0 = Clear, 1 = Cirrus, 2 = Scattered, 3 = Broken, 4 = Overcast
CLOUD_COVER = 4

# SAMPLING
# Number of samples desired for dataset
NUM_TRAIN = 5
NUM_VALID = 5

# BOUNDING BOX PARAMS
OFFSET = 0
AW0 = 0
DAW = 18000