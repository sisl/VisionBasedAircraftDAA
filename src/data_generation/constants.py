# Seconds to pause
PAUSE_1 = 3 # before data generation
PAUSE_2 = 0.5 # between each sample

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