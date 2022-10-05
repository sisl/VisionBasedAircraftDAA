
OUTDIR = "/Users/elysiasmyers/Desktop/STANFORD/VisionBasedAircraftDAA/datasets/"

REGION_CHOICE = "Palo Alto"

# Latitude, Longitiude, and Altitude of different region locations
REGION_OPTIONS = {
    "Palo Alto": [37.46358871459961, -122.11750030517578, 1578.909423828125]
}

# OWNSHIP LOCATION
# Used to determine location of Ownship from region location
# Will be used to determine distance from location in meters in positive or negative direction
# Entered as a float (i.e. with a decimal) in meters >= 0
EAST_RANGE = 5000.0
NORTH_RANGE = 5000.0
UP_RANGE = 500.0

# TIME OF DAY
# Start and end of range of possible time of day in local time, e.g. 8.0 = 8AM, 17.0 = 5PM
# For each sinsoidal trajectory in the run, the time of day will be sampled uniformly
# from this range
TIME_OF_DAY_START = 8.0
TIME_OF_DAY_END = 11.0