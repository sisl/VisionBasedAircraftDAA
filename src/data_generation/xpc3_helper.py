# Helper functions for xpc3 specific to the taxinet problem
# Written by Kyle Julian and Sydney Katz
# Maintained by Sydney Katz (smkatz@stanford.edu)

import numpy as np
import data_generation.xpc3
import time
import pandas as pd

def sendCTRL(client, elev, aileron, rudder, throttle):
    """Sets control surface information (on the main aircraft)

        Args:
            client: XPlane Client
            elev: [-1, 1]
            aileron: [-1, 1]
            rudder: [-1, 1]
            throttle: [-1, 1]
    """
    client.sendCTRL([elev, aileron, rudder, throttle])

def sendBrake(client, brake):
    """Set the parking brake to on or off

        Args:
            client: XPlane Client
            brake: 0 - off; 1 - on
    """
    client.sendDREF("sim/flightmodel/controls/parkbrake", brake)

def getSpeed(client):
    """Get current speed (m/s)

        Args:
            client: XPlane Client
    """
    return client.getDREF("sim/flightmodel/position/groundspeed")[0]


def getBrake(client):
    """Get current brake

        Args:
            client: XPlane Client
    """
    return client.getDREF("sim/flightmodel/controls/parkbrake")[0]

"""Position on Runway"""

def getStartXY():
    """Get Start x and y values in the local coordinate frame"""
    return -25159.26953125, 33689.8125

def rotateToHome(x, y):
    """Rotate to the home coordinate frame.

        Home coordinate frame starts at (0,0) at the start of the runway
        and ends at (0, 2982 at the end of the runway). Thus, the x-value
        in the home coordinate frame corresponds to crosstrack error and
        the y-value corresponds to downtrack position.

        Args:
            x: x-value in local coordinate frame
            y: y-value in local coordinate frame
    """
    rotx = 0.583055934597441 * x + 0.8124320138514389 * y
    roty = -0.8124320138514389 * x + 0.583055934597441 * y
    return rotx, roty

def rotateToLocal(x, y):
    """Rotate to the local coordinate frame.

        Args:
            x: x-value in home coordinate frame
            y: y-value in home coordinate frame
    """
    rotx = 0.583055934597441 * x + -0.8124320138514389 * y
    roty = 0.8124320138514389 * x + 0.583055934597441 * y
    return rotx, roty

def homeToLocal(x, y):
    """Get the local coordinates of the aircraft from the home coordinates.

        Args:
            x: x-value in the home coordinate frame
            y: y-value in the home coordinate frame
    """
    
    # Rotate back
    rotx, roty = rotateToLocal(x, y)

    # Translate back
    startX, startY = getStartXY()
    transx = startX - rotx
    transy = startY - roty

    return transx, transy 

def localToHome(x, y):
    """Get the home coordinates of the aircraft from the local coordinates.

        Args:
            x: x-value in the local coordinate frame
            y: y-value in the local coordinate frame
    """
    
    # Translate to make start x and y the origin
    startX, startY = getStartXY()
    transx = startX - x
    transy = startY - y

    # Rotate to align runway with y axis
    rotx, roty = rotateToHome(transx, transy)
    return rotx, roty

def getHomeState(client):
    """Get the aircraft's current x and y position and heading in the 
    home frame. The x-value represents crosstrack error,the y-value represents
    downtrack position, and theta is the heading error.

        Args:
            client: XPlane Client
    """
    
    psi = client.getDREF("sim/flightmodel/position/psi")[0]
    x = client.getDREF("sim/flightmodel/position/local_x")[0]
    y = client.getDREF("sim/flightmodel/position/local_z")[0]

    # Rotate heading into home coordinates
    theta = 53.7 - psi

    # Get the positions in home coordinates
    rotx, roty = localToHome(x, y)

    return rotx, roty, theta

def setHomeState(client, x, y, theta):
    """Set the aircraft's state using coordinates in the home frame.
    This is equivalent to setting the crosstrack error (x), downtrack
    position (y), and heading error (theta).

        Args:
            client: XPlane Client
            x: desired crosstrack error [-10, 10] (meters)
            y: desired downtrack position [0, 2982] (meters)
            theta: desired heading error [-180, 180] (degrees)
    """

    localx, localz = homeToLocal(x, y)

    client.sendDREF("sim/flightmodel/position/local_x", localx)
    client.sendDREF("sim/flightmodel/position/local_z", localz)
    client.sendDREF("sim/flightmodel/position/psi", 53.7 - theta)

    # Place perfectly on the ground
    # Pause for a bit for it to move
    time.sleep(0.02)
    curr_agly = client.getDREF("sim/flightmodel/position/y_agl")[0]
    curr_localy = client.getDREF("sim/flightmodel/position/local_y")[0]
    client.sendDREF("sim/flightmodel/position/local_y",
                    curr_localy - curr_agly)

def getPercDownRunway(client):
    """Get the percent down the runway of the main aircraft

        Args:
            client: XPlane Client
    """

    x = client.getDREF("sim/flightmodel/position/local_x")[0]
    y = client.getDREF("sim/flightmodel/position/local_z")[0]
    _, yhome = localToHome(x, y)
    return (yhome / 2982) * 100

"""Utility"""

def reset(client, cteInit=0, heInit=0, dtpInit=0, noBrake=True):
    """Resets the aircraft and resets forces, fuel, etc.

        Args:
            client: XPlane Client
            cteInit: initial crosstrack error (meters)
            heInit: initial heading error (degrees)
            dtpInit: initial downtrack position (meters)
    """
    
    client.pauseSim(True)
    # lat,lon, alt, pitch, roll, heading = getStartPosition(cteInit, heInit, drInit); 

    # Turn off joystick "+" mark from screen
    client.sendDREF("sim/operation/override/override_joystick", 1)

    # Zero out control inputs
    sendCTRL(client,0,0,0,0)

    # Set parking brake
    if noBrake:
        sendBrake(client,0)
    else:
        sendBrake(client,1)

    # Zero out moments and forces
    initRef = "sim/flightmodel/position/"
    drefs = []
    refs = ['theta','phi','psi','local_vx','local_vy','local_vz','local_ax','local_ay','local_az',
    'Prad','Qrad','Rrad','q','groundspeed',
    'indicated_airspeed','indicated_airspeed2','true_airspeed','M','N','L','P','Q','R','P_dot',
    'Q_dot','R_dot','Prad','Qrad','Rrad']
    for ref in refs:
        drefs += [initRef+ref]
    values = [0]*len(refs)
    client.sendDREFs(drefs,values)

    # Set position and orientation
    # Set known good start values
    client.sendPOSI([47.196890, -119.33260, 362.14444, 0.31789625, 0.10021035, 53.7, 1], 0)
    # Fine-tune position
    # Setting position with lat/lon gets you within 0.3m. Setting local_x, local_z is more accurate)
    setHomeState(client, cteInit, dtpInit, heInit)

    # Fix the plane if you "crashed" or broke something
    client.sendDREFs(["sim/operation/fix_all_systems"], [1])

    # Set fuel mixture for engine
    client.sendDREF("sim/flightmodel/engine/ENGN_mixt", 0.61)

    # Set speed of aircraft to be 5 m/s in current heading direction
    heading = 53.7 - heInit
    client.sendDREF("sim/flightmodel/position/local_vx", 5.0*np.sin(heading*np.pi/180.0))
    client.sendDREF("sim/flightmodel/position/local_vz", -5.0*np.cos(heading*np.pi/180.0))

    # Reset fuel levels
    client.sendDREFs(["sim/flightmodel/weight/m_fuel1","sim/flightmodel/weight/m_fuel2"],[232,232])

def saveState(client, folder, filename='test.csv'):
    """Save the current state of the simulator to a CSV file.
        
        Pulls all relevant DREFs and stores them in a CSV.
        Can use loadState to set simulator back to a saved state.

        Args:
            client: XPlane Client
            folder: path to save to
            filename: name of file to save to
    """

    # Position/orientation/speeds/turn rates/etc datarefs
    drefs = []
    initRef = "sim/flightmodel/position/"
    refs = ['theta','phi','psi','local_x','local_y','local_z','local_vx','local_vy','local_vz','local_ax','local_ay',
    'local_az','Prad','Qrad','Rrad','q','groundspeed'
    'indicated_airspeed','indicated_airspeed2','M','N','L','P','Q','R','P_dot',
    'Q_dot','R_dot','Prad','Qrad','Rrad']
    for ref in refs:
        drefs += [initRef+ref]

    # Engine related datarefs
    initRef = "sim/flightmodel/engine/"
    refs = ['ENGN_N2_','ENGN_N1_','ENGN_EGT','ENGN_ITT','ENGN_CHT','ENGN_EGT_c','ENGN_ITT_c',
            'ENGN_CHT_C','ENGN_FF_','ENGN_EPR','ENGN_MPR','ENGN_oil_press_psi',
            'ENGN_oil_press','ENGN_oil_press','ENGN_power','ENGN_prop','ENGN_TRQ',
            'ENGN_thro','ENGN_thro_use',
            'POINT_thrust','POINT_tacrad','ENGN_mixt','ENGN_prop','ENGN_propmode']
    for ref in refs:
        drefs += [initRef+ref]

    # Force related dataref
    initRef = "sim/flightmodel/forces/"
    refs = ['fside_prop','fnrml_prop','faxil_prop','L_prop','M_prop','N_prop',
            'L_total','M_total','N_total']
    for ref in refs:
        drefs += [initRef+ref]

    # parking brake, time of day, and fuel level data ref
    drefs += ["sim/flightmodel/controls/parkbrake"]
    drefs += ["sim/time/zulu_time_sec"]
    drefs += ["sim/flightmodel/weight/m_fuel1","sim/flightmodel/weight/m_fuel2"]

    # Get the datarefs
    values = client.getDREFs(drefs)
    valuesFilt = []
    drefsFilt = []
    for i,val in enumerate(values):
        if len(val)>0:
            valuesFilt += [val[0]]
            drefsFilt += [drefs[i]]

    # Get position and controller settings
    valuesFilt += client.getPOSI()
    valuesFilt += client.getCTRL()
    drefsFilt += ["lat","lon","alt","pitch","roll","heading","gear"]
    drefsFilt += ["elev","aileron","rudder","throttle","gear","flaps","speedbrakes"]
    values = np.array(valuesFilt).reshape((1,len(valuesFilt)))

    # Save to CSV
    outData = pd.DataFrame(values,index=[0],columns=drefsFilt)
    csv_file = folder + "/"+filename
    outData.to_csv(csv_file,index=False,index_label=False)


def loadState(client, folder, filename='test.csv'):
    """Read csv file of saved simulator state, load the simulator with saved values

        Args:
            client: XPlane Client
            folder: path to file with the state
            filename: name of file with the state
    """

    # Read CSV file
    tab = pd.read_csv(folder + "/" +filename)
    drefs = list(tab.columns)
    values = list(tab.values[0])

    # Separate out values
    pos = values[-14:-7]
    ctrl = values[-7:]
    values = values[:-14]
    drefs = drefs[:-14]

    # Send values to simulator
    client.sendPOSI(pos)
    client.sendDREFs(drefs,values)
    ctrl[4] = int(ctrl[4]); ctrl[5] = int(ctrl[5]); ctrl[6] = int(ctrl[6]);
    ctrl[3]*=3
    client.sendCTRL(ctrl)
    time.sleep(0.05)