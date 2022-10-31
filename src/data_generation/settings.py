
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
NUM_SAMPLES = 10

# BOUNDING BOX PARAMS
OFFSET = -36
AW0 = 0
DAW = 18000



'''------CONSTANTS BELOW THIS LINE (Unlikely to need changing)-------'''
# Seconds to pause
PAUSE_1 = 3 # before data generation
PAUSE_2 = 0.05 # between each sample

# Latitude, Longitiude, and Altitude of different region locations
# about 1500m agl
REGION_OPTIONS = {
    "Palo Alto": [37.46358871459961, -122.11750030517578, 1502.0],
    "Boston": [42.37415695190430, -71.01775360107422, 1502.24971318244934],
    "Osh Kosh": [43.98562240600586, -88.55644226074219, 1739.03918457031250],
    "Reno Tahoe": [39.51367568969727, -119.76921844482422, 2845.42443847656250]
}

# shifted 500m north and 500m east
REGION_OPTIONS_SHIFTED = {
    "Palo Alto": [37.46809387207031, -122.11184692382812, 1502.19499897956848],
    "Boston": [42.37865447998047, -71.01168823242188, 1502.24971318244934],
    "Osh Kosh": [43.99011993408203, -88.55020904541016, 1739.03918457031250],
    "Reno Tahoe": [39.51817703247070, -119.76340484619141, 2845.42443847656250],
}

# Hours behind Zulu (UTC) time for each region
TIME_OPTIONS = {
    "Palo Alto": 8,
    "Boston": 5,
    "Osh Kosh": 5,
    "Reno Tahoe": 8
}