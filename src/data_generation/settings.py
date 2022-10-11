
OUTDIR = "/Users/elysiasmyers/Desktop/STANFORD/VisionBasedAircraftDAA/datasets/"
#OUTDIR = "C:/Users/X-Plane/Desktop/VisionBasedAircraftDAA/datasets/"

REGION_CHOICE = "Palo Alto"

# OWNSHIP POSITION
# Used to determine location of Ownship from region location
# Will be used to determine distance from location in meters in positive or negative direction
# Entered as a float (i.e. with a decimal) in meters >= 0
EAST_RANGE = 5000.0
NORTH_RANGE = 5000.0
UP_RANGE = 500.0

# OWNSHIP POSITION Cont. 
# all in (min, max) form
OWNSHIP_HEADING = (0.0, 360.0) # degrees
PITCH_RANGE = (-90, 90) # degrees (-90 = straight down, 90 = straight up)
ROLL_RANGE = (-90, 90) # degrees (-90 = full roll left, 90 = full roll right)

# INTRUDER POSITION
# all in (min, max) form
INTRUDER_HEADING = (0.0, 360.0) # degrees
VANG_RANGE = (-25.0, 25.0) # degrees, vertical angle from ownship
HANG_RANGE = (-38.0, 38.0) # degrees, horizontal angle from ownship
DIST_RANGE = (20, 2000) # meters, diagonal distance from ownship

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



'''------CONSTANTS BELOW THIS LINE (Unlikely to need changing)-------'''
# Seconds to pause
PAUSE_1 = 3 # before data generation
PAUSE_2 = 0.05 # between each sample

# Latitude, Longitiude, and Altitude of different region locations
REGION_OPTIONS = {
    "Palo Alto": [37.46358871459961, -122.11750030517578, 1578.909423828125]
}

# Hours behind Zulu (UTC) time for each region
TIME_OPTIONS = {
    "Palo Alto": 8
}