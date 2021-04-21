import matlab.engine
import numpy as np
from aircraft import Wing

from parapy.core import *
from parapy.geom import *
import aircraft.Import_Input as I

class Q3D(GeomBase):
    twist_chord = Input(0.0)  # deg positive up
    AoA      = Input(2.0)  # deg
    T_zero   = Input(288) #Kelvin
    P_zero   = Input(101325) #Pa
    Rho_zero = Input(1.225) #kg/m3
    deltaT   = Input(-0.0065) #K/m
    viscosity_dyn_zero = Input(1.81*10**(-5))
    span       = Input(Wing().span)  # m input total, Q3D puts half of it already
    root_chord = Input(Wing().chord_root)  # m
    tip_chord  = Input(Wing().chord_tip)  # m
    MAC        = Input(Wing().mean_aerodynamic_chord) # m

    twist_tip = Input(Wing().twist)  # deg positive up
    dihedral  = Input(Wing().dihedral)  # deg
    sweep     = Input(Wing().sweep_leading_edge)  # deg

    altitude = Input(Wing().altitude_cruise)  # m
    Mach     = Input(Wing().mach_cruise)  # make it in accordance with the flight speed and altitude
    Cl       = Input(Wing().lift_coefficient) # if Cl is used do not use angle of attack

    @Attribute
    def temperature(self):
        if self.altitude <11001:
            temp = self.T_zero + self.altitude*self.deltaT
        else:
            temp = self.T_zero + 11000*self.deltaT
        return temp

    @Attribute
    def pressure(self):
        if self.altitude <11001:
            press = self.P_zero * (np.e) ** ((-9.81665 / (287 * self.temperature)) * (self.altitude))
        else:
            press = 22632 * (self.temperature / 216.65) ** (-9.81665 / (self.altitude * 287))
        return press

    @Attribute
    def soundSpeed(self):
        return np.sqrt(1.4*287*self.temperature)

    @Attribute
    def airSpeed(self):
        return self.Mach *self.soundSpeed

    @Attribute
    def airDensity(self):
        return  self.pressure/(287*self.temperature)

    @Attribute
    def viscosity_dyn(self):
        return self.viscosity_dyn_zero*(self.temperature/self.T_zero)**0.7

    @Attribute
    def Reynolds(self):
        return self.airDensity*self.airSpeed*self.MAC/self.viscosity_dyn

    @Attribute
    def QThreeD(self):

        eng = matlab.engine.start_matlab()

        span        = float(self.span)
        root_chord  = float(self.root_chord)
        tip_chord   = float(self.tip_chord)
        twist_chord = float(self.twist_chord)
        twist_tip   = float(self.twist_tip)
        dihedral    = float(self.dihedral)
        sweep       = float(self.sweep)
        airSpeed    = float(self.airSpeed)
        airDensity  = float(self.airDensity)
        altitude    = float(self.altitude)
        Reynolds    = float(self.Reynolds)
        Mach        = float(self.Mach)
        AoA         = float(self.AoA)
        Cl          = float(self.Cl)

        # eng = matlab.engine.start_matlab()
        # run Q3D function
        [CLdes, CDdes] = eng.Q3Drunner(span, root_chord, tip_chord, twist_chord, twist_tip, dihedral, sweep, airSpeed,
                                      airDensity, altitude, Reynolds, Mach, AoA, Cl, nargout=2)
        eng.quit()
        res = [CLdes, CDdes]
        # print(res)
        return res


    @Attribute
    def CLdes(self):
        CLdes = self.QThreeD[0]
        return CLdes

    @Attribute
    def CDdes(self):
        CDdes = self.QThreeD[1]
        return CDdes




# span=30.0
# root_chord = 5.0
# tip_chord = 1.0
# twist_chord =0.0
# twist_tip = -5.0
# dihedral = 2.0
# sweep = 30.0
# airSpeed = 60.0
# airDensity =1.225
# altitude = 11000.0
# Reynolds = 20000000.
# Mach = 0.8
# AoA = 2.0
# Cl = 0.8
#
# eng = matlab.engine.start_matlab()
#
#
#
# # run Q3D function
# [CLdes, CDdes] = eng.Q3Drunner(span, root_chord, tip_chord, twist_chord, twist_tip, dihedral, sweep, airSpeed,
#                               airDensity, altitude, Reynolds, Mach, AoA,Cl, nargout=2)
# eng.quit()
