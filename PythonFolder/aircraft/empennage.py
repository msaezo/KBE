import numpy as np
from parapy.core import *
from parapy.geom import *
from math import *

import aircraft.Import_Input as In
from aircraft.fuselage import Fuselage
from aircraft.wing import Wing
from aircraft.cg_calculations import CGCalculations
from aircraft.lifting_surface import LiftingSurface


class VerticalTail(GeomBase):
    # airfoil profiles
    airfoil_root = Input("aircraft/simm_airfoil")
    airfoil_tip = Input("aircraft/simm_airfoil")
    volume_vt = Input(In.Tail_volume_vertical)
    aspect_ratio_vertical = Input(In.aspect_Ratio_vertical)
    taper_ratio_vertical = Input(In.taper_Ratio_vertical)
    sweep_leading_edge_vertical = Input(In.sweep_leading_edge_vertical)
    mach_cruise = Input(In.Mach_cruise)
    twist_VT = Input(0)  # Hard Coded
    dihedral_VT = Input(0)  # Hard Coded
    lift_coefficient = Input(Wing().lift_coefficient)
    surface_area = Input(Wing().area_wing)
    span = Input(Wing().span)
    length_fuselage = Input(Fuselage().length_fuselage)
    length_tail = Input(Fuselage().length_tail)
    cg_aft = Input(CGCalculations().cg_aft)
    diameter_fuselage_outer = Input(Fuselage().diameter_fuselage_outer)

    # get x position of where the vt starts
    @Attribute
    def x_tail_vertical(self):
        return self.length_fuselage-self.length_tail

    # calculate cg arm of vt
    @Attribute
    def cg_arm_vertical(self):
        return self.x_tail_vertical - self.cg_aft

    # use tail volume, wing area and gc arm  to find vt area
    @Attribute
    def surface_vertical_tail(self):
        return self.volume_vt * self.surface_area * self.span / self.cg_arm_vertical

    # find vt surface span
    @Attribute
    def span_vertical_tail(self):
        return sqrt(self.aspect_ratio_vertical * self.surface_vertical_tail)

    # find vt root chord
    @Attribute
    def root_chord_vertical_tail(self):
        return 2 * self.surface_vertical_tail / ((1 + self.taper_ratio_vertical) * self.span_vertical_tail)

    # find vt tip chord
    @Attribute
    def tip_chord_vertical_tail(self):
        return self.root_chord_vertical_tail * self.taper_ratio_vertical

    # create list of airfoil profieles at tip and root, needed for loftedsolid superclass
    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil_vt, self.tip_airfoil_vt]

    # define the x position of the vt
    @Attribute  # Hard Coded, relate it to the Xcg
    def vt_x_shift(self):
        return self.cg_aft + self.cg_arm_vertical

    # define the z position of the vt root, set to 90% of fuselage radius
    @Attribute  # Hard Coded, relate it to the Xcg
    def vt_z_shift(self):
        return self.diameter_fuselage_outer * 0.9 / 2

    # use vt properties and root location to define tip location relative to root location for x
    @Attribute  # Hard Coded, relate it to the Xcg
    def vt_x_shift_tip(self):
        return self.vt_x_shift + self.span_vertical_tail * np.tan(np.deg2rad(self.sweep_leading_edge_vertical))

    # use vt properties and root location to define tip location relative to root location for z
    @Attribute  # Hard Coded, relate it to the Xcg
    def vt_z_shift_tip(self):
        return self.vt_z_shift + self.span_vertical_tail

    # calculate mic chord sweep of VT
    @Attribute
    def sweep_mid_chord_vertical_tail(self):
        return np.rad2deg(np.arctan(
            np.tan(np.deg2rad(self.sweep_leading_edge_vertical)) - 4 / self.aspect_ratio_vertical * (1 / 2) * (
                    1 - self.taper_ratio_vertical) / (1 + self.taper_ratio_vertical)))

    # calculate quarter chord sweep of VT
    @Attribute
    def sweep_cuarter_chord_vertical_tail(self):
        return np.rad2deg(np.arctan(
            np.tan(np.deg2rad(self.sweep_leading_edge_vertical)) - 4 / self.aspect_ratio_vertical * (1 / 4) * (
                    1 - self.taper_ratio_vertical) / (1 + self.taper_ratio_vertical)))

    # Calculate drag divergence mach number
    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    # define t/c, with a max of 0.18
    @Attribute
    def thickness_to_chord(self):
        cos_halfsweep = np.cos(np.deg2rad(self.sweep_mid_chord_vertical_tail))
        option_one = (cos_halfsweep ** 3 * (
                0.935 - self.mach_drag_divergence * cos_halfsweep) - 0.115 * self.lift_coefficient ** 1.5) / (
                             cos_halfsweep ** 2)
        if option_one > 0.18:
            toverc = 0.18
        else:
            toverc = option_one
        return toverc

    # create VT part by using the class LiftingSurface
    @Part
    def vertical_tail(self):
        return LiftingSurface(airfoil_root="aircraft/simm_airfoil",
                              airfoil_tip="aircraft/simm_airfoil",
                              root_chord=self.root_chord_vertical_tail,
                              thickness_to_chord_root=self.thickness_to_chord,
                              factor_root=0.24,
                              tip_chord=self.tip_chord_vertical_tail,
                              thickness_to_chord_tip=self.thickness_to_chord,
                              factor_tip=0.24,
                              x_shift_root=self.vt_x_shift,
                              y_shift_root=0,
                              z_shift_root=self.vt_z_shift,
                              x_shift_tip=self.vt_x_shift_tip,
                              y_shift_tip=self.vt_z_shift_tip,
                              z_shift_tip=0,
                              rotate=90,
                              twist=0)


class HorizontalTail(GeomBase):

    airfoil_root = Input("aircraft/simm_airfoil")
    airfoil_tip = Input("aircraft/simm_airfoil")
    volume_ht = Input(In.Tail_volume_horizontal)
    aspect_ratio_horizontal = Input(In.aspect_Ratio_horizontal)
    taper_ratio_horizontal = Input(In.taper_Ratio_horizontal)
    sweep_three_quarter_horizontal = Input(In.sweep_three_quarter_horizontal)
    mach_cruise = Input(In.Mach_cruise)
    twist = Input(0)  # Hard Coded
    dihedral = Input(0)  # Hard Coded
    lift_coefficient = Input(0.3)  # Hard Coded
    surface_area = Input(Wing().area_wing)
    mac = Input(Wing().mean_aerodynamic_chord)
    length_fuselage = Input(Fuselage().length_fuselage)
    cg_aft = Input(CGCalculations().cg_aft)
    diameter_fuselage_outer = Input(Fuselage().diameter_fuselage_outer)
    x_tail_vertical = Input(VerticalTail().x_tail_vertical)
    root_chord_vertical_tail = Input(VerticalTail().root_chord_vertical_tail)
    tail_config = Input(In.configuration)
    x_tip_vertical = Input(VerticalTail().vt_x_shift_tip)
    z_tip_vertical = Input(VerticalTail().vt_z_shift_tip)
    span_vertical = Input(VerticalTail().span_vertical_tail)
    sweep_vertical = Input(VerticalTail().sweep_leading_edge_vertical)

    # Define x location of HT depending on configuration
    # Only the string 'T-tail', 't-tail', 'T_tail' or 't_tail' will give a t-tail,
    # any other sting will present a normal configuration
    @Attribute
    def x_tail_horizontal(self):
        if self.tail_config == 'T-tail' or self.tail_config == 'T_tail' or self.tail_config == 't-tail' or \
                self.tail_config == 't_tail':
            x_pos = self.x_tip_vertical - 0.2*self.span_vertical * np.tan(np.deg2rad(self.sweep_vertical))
        else:
            x_pos = self.x_tail_vertical + 0.2*self.root_chord_vertical_tail
        return x_pos

    # cCalculate HT cg arm
    @Attribute
    def cg_arm_horizontal(self):
        return self.x_tail_horizontal - self.cg_aft

    # Calculate HT srface area from tail volume, wing area and geometric properties such as MAC and cg arm
    @Attribute
    def surface_horizontal_tail(self):
        return self.volume_ht * self.surface_area * self.mac / self.cg_arm_horizontal

    # find span of HT
    @Attribute
    def span_horizontal_tail(self):
        return sqrt(self.aspect_ratio_horizontal * self.surface_horizontal_tail)

    # find HT root chord
    @Attribute
    def root_chord_horizontal_tail(self):
        return 2 * self.surface_horizontal_tail / ((1 + self.taper_ratio_horizontal) * self.span_horizontal_tail)

    # find HT tip chord
    @Attribute
    def tip_chord_horizontal_tail(self):
        return self.root_chord_horizontal_tail * self.taper_ratio_horizontal

    # find LE sweep of HT
    @Attribute
    def sweep_leading_edge_horizontal_tail(self):  # self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4
                                    / self.aspect_ratio_horizontal * (-3 / 4)
                                    * (1 - self.taper_ratio_horizontal) / (1 + self.taper_ratio_horizontal)))

    # find quarter chord seep of HT
    @Attribute
    def sweep_cuarter_chord_horizontal_tail(self):  # self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(
            np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4 / self.aspect_ratio_horizontal * (-2 / 4) * (
                    1 - self.taper_ratio_horizontal) / (1 + self.taper_ratio_horizontal)))

    # find mid chord sweep of HT
    @Attribute
    def sweep_mid_chord_horizontal_tail(self):  # self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4
                                    / self.aspect_ratio_horizontal * (-1 / 4)
                                    * (1 - self.taper_ratio_horizontal) / (1 + self.taper_ratio_horizontal)))

    # find x position of HT
    @Attribute
    def ht_x_shift(self):
        return self.x_tail_horizontal

    # find z position of HT
    # dependent on t-tail config or not
    # if t-tail -> 80% up of the span of vt
    # if conventional, 80% of fuselage radius
    @Attribute  # Hard Coded, maybe set same height as wing?
    def ht_z_shift(self):
        if self.tail_config == 'T-tail' or self.tail_config == 'T_tail' or self.tail_config == 't-tail' or \
                self.tail_config == 't_tail':
            z_pos = self.z_tip_vertical - 0.2*self.span_vertical
        else:
            z_pos = self.diameter_fuselage_outer/2 * 0.8
        return z_pos

    # z-position of tip relative to chord of HT
    @Attribute
    def ht_z_shift_tip(self):
        return self.ht_z_shift + self.span_horizontal_tail / 2 * np.tan(np.deg2rad(self.dihedral))

    # x_position of tip relative to chord of HT
    @Attribute
    def ht_x_shift_tip(self):
        return self.ht_x_shift + self.span_horizontal_tail / 2 * np.tan(
            np.deg2rad(self.sweep_leading_edge_horizontal_tail))

    # y-position of tip relative to chord of HT (half span)
    @Attribute
    def ht_y_shift_tip(self):
        return self.span_horizontal_tail / 2

    # profile set of airfoils as input for SUperclass LoftedSolid later on
    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil_ht, self.tip_airfoil_ht]

    # calculate Mach drag divergence
    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    # minimum T/c = 0.1, max is 0.18
    @Attribute
    def thickness_to_chord(self):
        cos_halfsweep = np.cos(np.deg2rad(self.sweep_mid_chord_horizontal_tail))
        option_one = (cos_halfsweep ** 3 * (0.935 - self.mach_drag_divergence * cos_halfsweep)
                      - 0.115 * self.lift_coefficient ** 1.5) / (cos_halfsweep ** 2)
        if option_one > 0.18:
            toverc = 0.18
        elif option_one < 0.1:
            toverc = 0.1
        else:
            toverc = option_one

        return toverc

    # create right wing part
    @Part
    def right_wing_surface_ht(self):
        return LiftingSurface(airfoil_root="aircraft/simm_airfoil",
                              airfoil_tip="aircraft/simm_airfoil",
                              root_chord=self.root_chord_horizontal_tail,
                              thickness_to_chord_root=self.thickness_to_chord,
                              factor_root=0.24,
                              tip_chord=self.tip_chord_horizontal_tail,
                              thickness_to_chord_tip=self.thickness_to_chord,
                              factor_tip=0.24,
                              x_shift_root=self.ht_x_shift,
                              y_shift_root=0,
                              z_shift_root=self.ht_z_shift,
                              x_shift_tip=self.ht_x_shift_tip,
                              y_shift_tip=self.ht_y_shift_tip,
                              z_shift_tip=self.ht_z_shift_tip,
                              rotate=0,
                              twist=self.twist)

    # create left wing part
    @Part
    def left_wing_surface_ht(self):
        return LiftingSurface(airfoil_root="aircraft/simm_airfoil",
                              airfoil_tip="aircraft/simm_airfoil",
                              root_chord=self.root_chord_horizontal_tail,
                              thickness_to_chord_root=self.thickness_to_chord,
                              factor_root=0.24,
                              tip_chord=self.tip_chord_horizontal_tail,
                              thickness_to_chord_tip=self.thickness_to_chord,
                              factor_tip=0.24,
                              x_shift_root=self.ht_x_shift,
                              y_shift_root=0,
                              z_shift_root=self.ht_z_shift,
                              x_shift_tip=self.ht_x_shift_tip,
                              y_shift_tip=-self.ht_y_shift_tip,
                              z_shift_tip=self.ht_z_shift_tip,
                              rotate=0,
                              twist=self.twist)
