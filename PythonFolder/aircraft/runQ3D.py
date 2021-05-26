import math

import matlab.engine
import numpy as np
import warnings
from aircraft import Wing

from parapy.core import *
from parapy.geom import *
import aircraft.Import_Input as In


class Q3D(GeomBase):
    twist_chord = Input(0.0)  # deg positive up
    AoA = Input(2.0)  # deg
    t_zero = Input(288)  # Kelvin
    t_zero_vs = Input(273)  # Kelvin
    s_vis = Input(111)  # Kelvin
    p_zero = Input(101325)  # Pa
    rho_zero = Input(1.225)  # kg/m3
    deltaT = Input(-0.0065)  # K/m
    viscosity_dyn_zero = Input(1.716 * 10 ** (-5))
    span = Input(Wing().span)  # m input total, Q3D puts half of it already
    root_chord = Input(Wing().chord_root)  # m
    tip_chord = Input(Wing().chord_tip)  # m
    MAC = Input(Wing().mean_aerodynamic_chord)  # m

    twist_tip = Input(Wing().twist)  # deg positive up
    dihedral = Input(Wing().dihedral)  # deg
    sweep = Input(Wing().sweep_leading_edge)  # deg

    altitude = Input(Wing().altitude_cruise)  # m
    mach = Input(Wing().mach_cruise)  # make it in accordance with the flight speed and altitude
    cl = Input(Wing().lift_coefficient)  # if Cl is used do not use angle of attack

    @Attribute
    def temperature(self):
        if self.altitude < 11001:
            temp = self.t_zero + self.altitude * self.deltaT
        else:
            temp = self.t_zero + 11000 * self.deltaT
        return temp

    @Attribute
    def pressure(self):
        if self.altitude < 11001:
            press = self.p_zero * np.e ** ((-9.81665 / (287 * self.temperature)) * self.altitude)
        else:
            press = 22632 * (self.temperature / 216.65) ** (-9.81665 / (self.altitude * 287))
        return press

    @Attribute
    def sound_speed(self):
        return np.sqrt(1.4 * 287 * self.temperature)

    @Attribute
    def air_speed(self):
        return self.mach * self.sound_speed

    @Attribute
    def air_density(self):
        return self.pressure / (287 * self.temperature)

    @Attribute
    def viscosity_dyn(self):
        return self.viscosity_dyn_zero * (
                    (self.temperature / self.t_zero_vs) ** (3 / 2) * (self.t_zero_vs + self.s_vis) / \
                    (self.temperature + self.s_vis))  # Sutherland's' Law

    @Attribute
    def reynolds(self):
        return self.air_density * self.air_speed * self.MAC / self.viscosity_dyn

    @Attribute
    def q_three_d(self):

        eng = matlab.engine.start_matlab()

        span = float(self.span)
        root_chord = float(self.root_chord)
        tip_chord = float(self.tip_chord)
        twist_chord = float(self.twist_chord)
        twist_tip = float(self.twist_tip)
        dihedral = float(self.dihedral)
        sweep = float(self.sweep)
        airspeed = float(self.air_speed)
        airdensity = float(self.air_density)
        altitude = float(self.altitude)
        reynolds = float(self.reynolds)
        mach = float(self.mach)
        aoa = float(self.AoA)
        cl = float(self.cl)

        # eng = matlab.engine.start_matlab()
        # run Q3D function
        [cldes, cddes, alpha] = eng.Q3Drunner(span, root_chord, tip_chord, twist_chord, twist_tip, dihedral, sweep,
                                              airspeed,
                                              airdensity, altitude, reynolds, mach, aoa, cl, nargout=3)
        eng.quit()
        res = [cldes, cddes, alpha]
        # print(res)
        return res

    @Attribute
    def cldes(self):
        cldes = self.q_three_d[0]
        return cldes

    @Attribute
    def cddes(self):
        cddes = self.q_three_d[1]
        if math.isnan(cddes):
            msg = "The drag coefficient of the wing calculated by the Q3D program could not be found" \
                  "Action taken: Cd of the wing based on Cl/20" \
                  "Suggested options:" \
                  "     - Change to thinner airfoil" \
                  "     - Increase wing area" \
                  "     - Increase sweep" \
                  "     - Decrease flight altitude"
            warnings.warn(msg, source=None)
        return cddes

    @Attribute
    def alpha(self):
        alphaa = self.q_three_d[2]
        return alphaa
