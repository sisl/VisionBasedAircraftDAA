'''
def set_position(client, ac, e, n, u, yaw, pitch=-998, roll=-998):
    """Sets position of aircraft in XPlane

    Parameters
    ----------
    client : SocketKind.SOCK_DGRAM
        XPlaneConnect socket
    ac : int
        number of aircraft to position
    e : float
        eastward distance from origin location in meters
    n : float
        northward distance from origin location in meters
    u : float
        upward distance from origin location in meters
    yaw : float
        aircraft heading in degrees
    pitch : int (optional)
    roll : int (optional)
    """

    ref = s.REGION_OPTIONS[s.REGION_CHOICE]
    p = pm.enu2geodetic(e, n, u, ref[0], ref[1], ref[2]) #east, north, up
    client.sendPOSI([*p, pitch, roll, yaw], ac)'''