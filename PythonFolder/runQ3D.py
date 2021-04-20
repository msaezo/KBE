import matlab.engine

eng = matlab.engine.start_matlab()

span = 29.0  # m input total, Q3D puts half of it already
root_chord = 3.5  # m
tip_chord = 1.4  # m
twist_chord = 0.0  # deg positive up
twist_tip = 0.0  # deg positive up
dihedral = 0.0  # deg
sweep = 10.0  # deg

airSpeed = 68.0  # m/s
airDensity = 1.225  # kg/m^3 #make it in accordance with altitude
altitude = 0.0  # m
Reynolds = 1.14e7  # make it in accordance with MAC
Mach = 0.2  # make it in accordance with the flight speed and altitude
AoA = 2.0  # deg
Cl = 0.6  # if Cl is used do not use angle of attack

[CLdes, CDdes] = eng.Q3Drunner(span, root_chord, tip_chord, twist_chord, twist_tip, dihedral, sweep, airSpeed,
                               airDensity, altitude, Reynolds, Mach, AoA, Cl, nargout=2)

eng.quit()

print(CLdes, CDdes)
