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
    airfoil_tip = Input("aircraft\simm_airfoil")

    volume_HT = Input(I.Tail_volume_horizontal)
    Surface_Area = Input(I.Wing_area)
    MAC = Input(Wing().mean_aerodynamic_chord)
    aspect_Ratio_horizontal = Input(I.aspect_Ratio_horizontal)
    taper_Ratio_horizontal = Input(I.taper_Ratio_horizontal)
    sweep_three_quarter_horizontal = Input(I.sweep_three_quarter_horizontal)
    mach_cruise = Input(I.Mach_cruise)

    twist = Input(0) #Hard Coded
    dihedral = Input(0) #Hard Coded
    lift_coefficient = Input(0.3) #Hard Coded

    @Attribute
    def x_tail_horizontal(self):
        return 0.85 * Fuselage().length_fuselage

    @Attribute
    def cg_arm_horizontal(self):
        return self.x_tail_horizontal - CG_calculations().cg_aft

    @Attribute
    def surfaceHorizontalTail(self):
        return self.volume_HT * self.Surface_Area * self.MAC / self.cg_arm_horizontal

    @Attribute
    def spanHorizontalTail(self):
        return sqrt(self.aspect_Ratio_horizontal * self.surfaceHorizontalTail)

    @Attribute
    def rootChordHorizontalTail(self):
        return 2*self.surfaceHorizontalTail / ((1+self.taper_Ratio_horizontal) * self.spanHorizontalTail)

    @Attribute
    def tipChordHorizontalTail(self):
        return self.rootChordHorizontalTail * self.taper_Ratio_horizontal

    @Attribute
    def sweepLeadingEdgeHorizontalTail(self): #self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4 / self.aspect_Ratio_horizontal * (-3 / 4) * (1 - self.taper_Ratio_horizontal) / (1 + self.taper_Ratio_horizontal)))


    @Attribute
    def sweepMidChordHorizontalTail(self):  # self.sweep_three_quarter_horizontal
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_three_quarter_horizontal)) - 4 / self.aspect_Ratio_horizontal * (-1 / 4) * (1 - self.taper_Ratio_horizontal) / (1 + self.taper_Ratio_horizontal)))

    @Attribute #Hard Coded, relate it to the Xcg
    def HT_x_shift(self):
        return CG_calculations().cg_aft + self.cg_arm_horizontal

    @Attribute #Hard Coded, maybe set same hight as wing?
    def HT_z_shift(self):
        return Fuselage().diameter_fuselage_outer*0.8/2

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil_HT, self.tip_airfoil_HT]

    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    @Attribute
    def thickness_to_chord(self):
        cos_halfsweep = np.cos(np.deg2rad(self.sweepMidChordHorizontalTail))
        option_one = (cos_halfsweep**3 * (0.935 - self.mach_drag_divergence * cos_halfsweep) - 0.115 *self.lift_coefficient**1.5)/(cos_halfsweep**2)

        if option_one > 0.18:
            toverc = 0.18
        elif option_one < 0.1:
            toverc = 0.1
        else:
            toverc =option_one

        return toverc

    @Part
    def root_airfoil_HT(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.rootChordHorizontalTail,
                       thickness_factor=self.thickness_to_chord,
                       position=translate(self.position,
                                          "x", self.HT_x_shift,
                                          "Z", self.HT_z_shift),
                       factor=0.14,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil_HT(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.tipChordHorizontalTail,
                       thickness_factor=self.thickness_to_chord,
                       factor=0.24,
                       position=translate(
                           rotate(self.position, "y", np.deg2rad(self.twist)),  # apply twist angle
                           "y", self.spanHorizontalTail/2,
                           "x", self.HT_x_shift + self.spanHorizontalTail/2 * np.tan(np.deg2rad(self.sweepLeadingEdgeHorizontalTail)),
                           "Z", self.HT_z_shift + self.spanHorizontalTail/2 * np.tan(np.deg2rad(self.dihedral))),
                       mesh_deflection=0.0001)

    @Part
    def right_wing_surface_HT(self):
        return LoftedSurface(profiles=self.profiles,

                             mesh_deflection=0.0001)

    @Part
    def left_wing_surface_HT(self):
        return MirroredShape(shape_in=self.right_wing_surface_HT,
                             reference_point=self.position,
                             # Two vectors to define the mirror plane
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=0.0001)



class Vertical_Tail(GeomBase):

    # airfoil profiles
    airfoil_root = Input("aircraft\simm_airfoil")
    airfoil_tip = Input("aircraft\simm_airfoil")

    volume_VT = Input(I.Tail_volume_vertical)
    Surface_Area = Input(I.Wing_area)
    Span = Input(Wing().span)
    aspect_Ratio_vertical = Input(I.aspect_Ratio_vertical)
    taper_Ratio_vertical = Input(I.taper_Ratio_vertical)
    sweep_leading_edge_vertical = Input(I.sweep_leading_edge_vertical)
    mach_cruise = Input(I.Mach_cruise)


    twist_VT = Input(0)  # Hard Coded
    dihedral_VT = Input(0)  # Hard Coded
    lift_coefficient = Input(0.3) #Hard Coded

    @Attribute
    def x_tail_vertical(self):
        return 0.8 * Fuselage().length_fuselage

    @Attribute
    def cg_arm_vertical(self):
        return self.x_tail_vertical - CG_calculations().cg_aft

    @Attribute
    def surfaceVerticalTail(self):
        return self.volume_VT * self.Surface_Area * self.Span / self.cg_arm_vertical

    @Attribute
    def spanVerticalTail(self):
        return sqrt(self.aspect_Ratio_vertical * self.surfaceVerticalTail)

    @Attribute
    def rootChordVerticalTail(self):
        return 2 * self.surfaceVerticalTail / ((1 + self.taper_Ratio_vertical) * self.spanVerticalTail)

    @Attribute
    def tipChordVerticalTail(self):
        return self.rootChordVerticalTail * self.taper_Ratio_vertical

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil_VT, self.tip_airfoil_VT]

    @Attribute #Hard Coded, relate it to the Xcg
    def VT_x_shift(self):
        return CG_calculations().cg_aft + self.cg_arm_vertical

    @Attribute #Hard Coded, relate it to the Xcg
    def VT_z_shift(self):
        return Fuselage().diameter_fuselage_outer*0.9/2


    @Attribute
    def sweepMidChordVerticalTail(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_leading_edge_vertical)) - 4 / self.aspect_Ratio_vertical * (1 / 2) * (1 - self.taper_Ratio_vertical) / (1 + self.taper_Ratio_vertical)))

    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    @Attribute
    def thickness_to_chord(self):
        return 0.1

    @Part
    def root_airfoil_VT(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.rootChordVerticalTail,
                       thickness_factor=self.thickness_to_chord,
                       position=translate(
                           rotate(self.position, "x", np.deg2rad(90)),
                                          "x", self.VT_x_shift,
                                          "Z", self.VT_z_shift),
                       factor=0.14,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil_VT(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.tipChordVerticalTail,
                       thickness_factor=self.thickness_to_chord,
                       factor=0.24,
                       position=translate(
                           rotate(self.position, "x", np.deg2rad(90)),  # apply twist angle
                        
                           "x", self.VT_x_shift + self.spanVerticalTail * np.tan(np.deg2rad(self.sweep_leading_edge_vertical)),
                           "y", self.VT_z_shift + self.spanVerticalTail ),
                       mesh_deflection=0.0001)

    @Part
    def vertical_wing_surface(self):
        return LoftedSurface(profiles=self.profiles,

                             mesh_deflection=0.0001)

