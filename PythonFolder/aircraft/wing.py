import numpy as np

import aircraft.Import_Input as In

from parapy.core import *
from parapy.geom import *

from aircraft.airfoil import Airfoil
from aircraft.fuselage import Fuselage
from aircraft.lifting_surface import LiftingSurface


# this file makes use of the following files:
# airfoil.py
# Import_Input.xls
# whitcomb.dat
# simm_airfoil.dat
# ref_frame.dat


# from aircraft import Section


class Wing(GeomBase):
    # airfoil profiles
    airfoil_root = Input("aircraft/whitcomb")
    airfoil_tip = Input("aircraft/simm_airfoil")
    mach_cruise = Input(In.Mach_cruise)  # In.Mach_cruise)
    altitude_cruise = Input(In.Altitude_cruise)
    weight_to = Input(In.Weight_TO)
    wing_loading = Input(In.Wing_loading)
    aspect_ratio = Input(In.Aspect_ratio)
    wing_highlow = Input("low")
    wing_mass_fraction = Input(In.Wing_mass_fraction)
    propulsion_mass_fraction = Input(In.Propulsion_system_mass_fraction)
    wing_cg_loc = Input(In.Wing_cg_loc)
    propulsion_cg_loc = Input(In.Propulsion_system_cg_loc)
    oew_cg_loc = Input(In.OEW_cg_loc)
    fuselage_mass_fraction = Input(In.Fuselage_mass_fraction)
    empennage_mass_fraction = Input(In.Empennage_mass_fraction)
    fixed_equipment_mass_fraction = Input(In.Fixed_equipment_mass_fraction)
    x_fuselage_cg = Input(Fuselage().x_fuselage_cg)
    diameter_fuselage_outer = Input(Fuselage().diameter_fuselage_outer)

    # some other parameters
    twist = Input(-5)
    is_mirrored = Input(True)

    # find the wing area correspondig to MTOW and wing loading
    @Attribute
    def area_wing(self):
        return self.weight_to / (9.81 * self.wing_loading)

    # find atmospheric conditions
    @Attribute
    def temperature(self):
        if self.altitude_cruise < 11001:
            temp = 288 + self.altitude_cruise * (-0.0065)
        else:
            temp = 288 + 11000 * (-0.0065)
        return temp

    @Attribute
    def pressure_static(self):
        if self.altitude_cruise < 11001:
            press = 101325 * np.e ** ((-9.81665 / (287 * self.temperature)) * self.altitude_cruise)
        else:
            press = 22632 * (self.temperature / 216.65) ** (-9.81665 / (self.altitude_cruise * 287))
        return press

    @Attribute
    def sound_speed(self):
        return np.sqrt(1.4 * 287 * self.temperature)

    @Attribute
    def air_speed(self):
        return self.mach_cruise * self.sound_speed

    @Attribute
    def air_density(self):
        return self.pressure_static / (287 * self.temperature)

    @Attribute
    def dynamic_pressure(self):
        return 0.7 * self.pressure_static * self.mach_cruise ** 2

    # find drag divergence mach number
    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    # find critical mach number
    @Attribute
    def mach_critical(self):
        return self.mach_drag_divergence - 0.18

    # find quarter chord sweep based of drag divergence
    @Attribute
    def sweep_quarter_chord(self):
        if self.mach_cruise < 0.7:
            sweep = np.rad2deg(np.arccos(1))
        else:
            sweep = np.rad2deg(np.arccos(0.75 * 0.935 / self.mach_drag_divergence))
        return sweep

    # find span
    @Attribute
    def span(self):
        return np.sqrt(self.area_wing * self.aspect_ratio)

    # find taper ratio
    @Attribute
    def taper_ratio(self):
        return 0.2 * (2 - np.deg2rad(self.sweep_quarter_chord))

    # find root and tip chords
    @Attribute
    def chord_root(self):
        return 2 * self.area_wing / (self.span * (1 + self.taper_ratio))

    @Attribute
    def chord_tip(self):
        return self.taper_ratio * self.chord_root

    # leading edge sweep from quarter chord sweep
    @Attribute
    def sweep_leading_edge(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_quarter_chord))
                                    - 4 / self.aspect_ratio * (-1 / 4) * (1 - self.taper_ratio) / (
                                            1 + self.taper_ratio)))

    # Find MAC (used for positioning the wing
    @Attribute
    def mean_aerodynamic_chord(self):
        return self.chord_root * 2 / 3 * (1 + self.taper_ratio + self.taper_ratio ** 2) / (1 + self.taper_ratio)

    # find y position of LEMAC
    @Attribute
    def y_mean_aerodynamic_chord(self):
        return self.span / 2 * (self.chord_root - self.mean_aerodynamic_chord) / (self.chord_root - self.chord_tip)

    # estimate CL of the wing
    @Attribute
    def lift_coefficient(self):
        return self.weight_to / (self.dynamic_pressure * self.area_wing)

    # set dihedral based on wing position
    @Attribute
    def dihedral(self):
        if self.wing_highlow == "high":
            dihed = 3 - self.sweep_quarter_chord / 10 - 2
        elif self.wing_highlow == "low":
            dihed = 3 - self.sweep_quarter_chord / 10 + 2
        else:
            dihed = 0
        return dihed

    # set list of airfoils for the superclass
    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]

    # determine the cg location of the wing
    @Attribute
    def x_wing_cg(self):
        wing_sum = self.wing_cg_loc * self.wing_mass_fraction
        propulsion_sum = self.propulsion_cg_loc * self.propulsion_mass_fraction
        return self.mean_aerodynamic_chord * (wing_sum + propulsion_sum) / (
                self.wing_mass_fraction + self.propulsion_mass_fraction)

    # determing the x position of the LEMAC
    @Attribute
    def x_le_mac(self):
        mass_fuselage = self.fuselage_mass_fraction + self.empennage_mass_fraction + self.fixed_equipment_mass_fraction
        mass_wing = self.wing_mass_fraction + self.propulsion_mass_fraction
        mass_wing_over_mass_fuse = mass_wing / mass_fuselage
        return self.x_fuselage_cg + self.mean_aerodynamic_chord * (
                (self.x_wing_cg / self.mean_aerodynamic_chord) * mass_wing_over_mass_fuse - self.oew_cg_loc
                * (1 + mass_wing_over_mass_fuse))

    # set the x position of the wing
    # XLEMAC minus the sweep between root and MAC
    @Attribute
    def wing_x_shift(self):
        return self.x_le_mac - self.y_mean_aerodynamic_chord * np.tan(np.deg2rad(self.sweep_leading_edge))

    # determne the Z-position of the wing, dependent on configuraton
    @Attribute
    def wing_z_shift(self):
        if self.wing_highlow == "high":
            pos = self.diameter_fuselage_outer * 0.9 / 2
        elif self.wing_highlow == "low":
            pos = -self.diameter_fuselage_outer * 0.8 / 2
        return pos

    # set the location of the tip profile based on all the calculated properties
    @Attribute
    def wing_x_shift_tip(self):
        return self.wing_x_shift + self.span / 2 * np.tan(np.deg2rad(self.sweep_leading_edge))

    @Attribute
    def wing_y_shift_tip(self):
        return self.span / 2

    @Attribute
    def wing_z_shift_tip(self):
        return self.wing_z_shift + self.span / 2 * np.tan(np.deg2rad(self.dihedral))

    # create the wing parts by using the Lifting Surface class
    @Part
    def right_wing_surface(self):
        return LiftingSurface(airfoil_root=self.airfoil_root,
                              airfoil_tip=self.airfoil_tip,
                              root_chord=self.chord_root,
                              thickness_to_chord_root=0.14,
                              factor_root=0.14,
                              tip_chord=self.chord_tip,
                              thickness_to_chord_tip=0.1,
                              factor_tip=0.24,
                              x_shift_root=self.wing_x_shift,
                              y_shift_root=0,
                              z_shift_root=self.wing_z_shift,
                              x_shift_tip=self.wing_x_shift_tip,
                              y_shift_tip=self.wing_y_shift_tip,
                              z_shift_tip=self.wing_z_shift_tip,
                              rotate=0,
                              twist=self.twist)

    @Part
    def left_wing_surface(self):
        return LiftingSurface(airfoil_root=self.airfoil_root,
                              airfoil_tip=self.airfoil_tip,
                              root_chord=self.chord_root,
                              thickness_to_chord_root=0.14,
                              factor_root=0.14,
                              tip_chord=self.chord_tip,
                              thickness_to_chord_tip=0.1,
                              factor_tip=0.24,
                              x_shift_root=self.wing_x_shift,
                              y_shift_root=0,
                              z_shift_root=self.wing_z_shift,
                              x_shift_tip=self.wing_x_shift_tip,
                              y_shift_tip=-self.wing_y_shift_tip,
                              z_shift_tip=self.wing_z_shift_tip,
                              rotate=0,
                              twist=self.twist)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
