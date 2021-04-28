import numpy as np
from parapy.core import *
from parapy.geom import *
from math import *

import aircraft.Import_Input as I
from aircraft.airfoil import Airfoil
from aircraft.fuselage import Fuselage
from aircraft.wing import Wing
from aircraft.cg_calculations import CG_calculations

class Horizontal_Tail(GeomBase):

    # airfoil profiles
    airfoil_root = Input("aircraft\simm_airfoil")
    airfoil_tip  = Input("aircraft\simm_airfoil")

    volume_ht                      = Input(I.Tail_volume_horizontal)
    surface_area                   = Input(Wing().area_wing)
    mac                            = Input(Wing().mean_aerodynamic_chord)
    aspect_ratio_horizontal        = Input(I.aspect_Ratio_horizontal)
    taper_ratio_horizontal         = Input(I.taper_Ratio_horizontal)
    sweep_three_quarter_horizontal = Input(I.sweep_three_quarter_horizontal)
    mach_cruise                    = Input(I.Mach_cruise)

    twist            = Input(0) #Hard Coded
    dihedral         = Input(0) #Hard Coded
    lift_coefficient = Input(0.3) #Hard Coded

    @Attribute
    def x_tail_horizontal(self):
        return 0.85 * Fuselage().length_fuselage

    @Attribute
    def cg_arm_horizontal(self):
        return self.x_tail_horizontal - CG_calculations().cg_aft

    @Attribute
    def surface_horizontal_tail(self):
        return self.volume_ht * self.surface_area * self.mac / self.cg_arm_horizontal

    @Attribute
    def span_horizontal_tail(self):
        return sqrt(self.aspect_ratio_horizontal * self.surface_horizontal_tail)

    @Attribute
    def root_chord_horizontal_tail(self):
        return 2*self.surface_horizontal_tail / ((1+self.taper_ratio_horizontal) * self.span_horizontal_tail)

    @Attribute
    def tip_chord_horizontal_tail(self):
        return self.root_chord_horizontal_tail * self.taper_ratio_horizontal

    @Attribute
    def sweep_leading_edge_horizontal_tail(self): #self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4
                                    / self.aspect_ratio_horizontal * (-3 / 4)
                                    * (1 - self.taper_ratio_horizontal) / (1 + self.taper_ratio_horizontal)))

    @Attribute
    def sweep_cuarter_chord_horizontal_tail(self):  # self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(
            np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4 / self.aspect_ratio_horizontal * (-2 / 4) * (
                        1 - self.taper_ratio_horizontal) / (1 + self.taper_ratio_horizontal)))

    @Attribute
    def sweep_mid_chord_horizontal_tail(self):  # self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4
                                    / self.aspect_ratio_horizontal * (-1 / 4)
                                    * (1 - self.taper_ratio_horizontal) / (1 + self.taper_ratio_horizontal)))

    @Attribute #Hard Coded, relate it to the Xcg
    def ht_x_shift(self):
        return CG_calculations().cg_aft + self.cg_arm_horizontal

    @Attribute #Hard Coded, maybe set same hight as wing?
    def ht_z_shift(self):
        return Fuselage().diameter_fuselage_outer*0.8/2

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil_ht, self.tip_airfoil_ht]

    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    # minimum T/c = 0.1, max is 0.18
    @Attribute
    def thickness_to_chord(self):
        cos_halfsweep = np.cos(np.deg2rad(self.sweep_mid_chord_horizontal_tail))
        option_one = (cos_halfsweep**3 * (0.935 - self.mach_drag_divergence * cos_halfsweep)
                      - 0.115 *self.lift_coefficient**1.5)/(cos_halfsweep**2)
        if option_one > 0.18:
            toverc = 0.18
        elif option_one <0.1:
            toverc = 0.1
        else:
            toverc =option_one

        return toverc

    @Part
    def root_airfoil_ht(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.root_chord_horizontal_tail,
                       thickness_factor=self.thickness_to_chord,
                       position=translate(self.position,
                                          "x", self.ht_x_shift,
                                          "Z", self.ht_z_shift),
                       factor=0.24,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil_ht(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.tip_chord_horizontal_tail,
                       thickness_factor=self.thickness_to_chord,
                       factor=0.24,
                       position=translate(
                           rotate(self.position, "y", np.deg2rad(self.twist)),  # apply twist angle
                           "y", self.span_horizontal_tail/2,
                           "x", self.ht_x_shift + self.span_horizontal_tail/2 * np.tan(np.deg2rad(self.sweep_leading_edge_horizontal_tail)),
                           "Z", self.ht_z_shift + self.span_horizontal_tail/2 * np.tan(np.deg2rad(self.dihedral))),
                       mesh_deflection=0.0001)

    @Part
    def right_wing_surface_ht(self):
        return LoftedSurface(profiles=self.profiles,
                             mesh_deflection=0.0001)

    @Part
    def left_wing_surface_ht(self):
        return MirroredShape(shape_in=self.right_wing_surface_ht,
                             reference_point=self.position,
                             # Two vectors to define the mirror plane
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=0.0001)



class Vertical_Tail(GeomBase):

    # airfoil profiles
    airfoil_root = Input("aircraft\simm_airfoil")
    airfoil_tip  = Input("aircraft\simm_airfoil")

    volume_vt                   = Input(I.Tail_volume_vertical)
    surface_area                = Input(Wing().area_wing)
    span                        = Input(Wing().span)
    aspect_ratio_vertical       = Input(I.aspect_Ratio_vertical)
    taper_ratio_vertical        = Input(I.taper_Ratio_vertical)
    sweep_leading_edge_vertical = Input(I.sweep_leading_edge_vertical)
    mach_cruise                 = Input(I.Mach_cruise)

    twist_VT         = Input(0)  # Hard Coded
    dihedral_VT      = Input(0)  # Hard Coded
    lift_coefficient = Input(Wing().lift_coefficient)

    @Attribute
    def x_tail_vertical(self):
        return 0.8 * Fuselage().length_fuselage

    @Attribute
    def cg_arm_vertical(self):
        return self.x_tail_vertical - CG_calculations().cg_aft

    @Attribute
    def surface_vertical_tail(self):
        return self.volume_vt * self.surface_area * self.span / self.cg_arm_vertical

    @Attribute
    def span_vertical_tail(self):
        return sqrt(self.aspect_ratio_vertical * self.surface_vertical_tail)

    @Attribute
    def root_chord_vertical_tail(self):
        return 2 * self.surface_vertical_tail / ((1 + self.taper_ratio_vertical) * self.span_vertical_tail)

    @Attribute
    def tip_chord_vertical_tail(self):
        return self.root_chord_vertical_tail * self.taper_ratio_vertical

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil_vt, self.tip_airfoil_vt]

    @Attribute #Hard Coded, relate it to the Xcg
    def vt_x_shift(self):
        return CG_calculations().cg_aft + self.cg_arm_vertical

    @Attribute #Hard Coded, relate it to the Xcg
    def vt_z_shift(self):
        return Fuselage().diameter_fuselage_outer*0.9/2

    @Attribute
    def sweep_mid_chord_vertical_tail(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_leading_edge_vertical)) - 4 / self.aspect_ratio_vertical * (1 / 2) * (1 - self.taper_ratio_vertical) / (1 + self.taper_ratio_vertical)))

    @Attribute
    def sweep_cuarter_chord_vertical_tail(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_leading_edge_vertical)) - 4 / self.aspect_ratio_vertical * (1 / 4) * (1 - self.taper_ratio_vertical) / (1 + self.taper_ratio_vertical)))

    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    @Attribute
    def thickness_to_chord(self):
        cos_halfsweep = np.cos(np.deg2rad(self.sweep_mid_chord_vertical_tail))
        option_one = (cos_halfsweep**3 * (0.935 - self.mach_drag_divergence * cos_halfsweep) - 0.115 *self.lift_coefficient**1.5)/(cos_halfsweep**2)

        if option_one > 0.18:
            toverc = 0.18
        else:
            toverc =option_one

        return toverc


    @Part
    def root_airfoil_vt(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.root_chord_vertical_tail,
                       thickness_factor=self.thickness_to_chord,
                       position=translate(
                           rotate(self.position, "x", np.deg2rad(90)),
                                          "x", self.vt_x_shift,
                                          "Z", self.vt_z_shift),
                       factor=0.24,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil_vt(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.tip_chord_vertical_tail,
                       thickness_factor=self.thickness_to_chord,
                       factor=0.24,
                       position=translate(
                           rotate(self.position, "x", np.deg2rad(90)),  # apply twist angle

                           "x", self.vt_x_shift + self.span_vertical_tail * np.tan(np.deg2rad(self.sweep_leading_edge_vertical)),
                           "y", self.vt_z_shift + self.span_vertical_tail),
                       mesh_deflection=0.0001)

    @Part
    def vertical_wing_surface(self):
        return LoftedSurface(profiles=self.profiles,

                             mesh_deflection=0.0001)

