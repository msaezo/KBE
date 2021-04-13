import numpy as np
from parapy.core import *
from parapy.geom import *
#from parapy.core import *
#from parapy.geom import *
import Import_Input as I
from airfoil import Airfoil

# this file makes use of the afollowing files:
# airfoil.py
# Import_Input.xls
# whitcomb.dat
# simm_airfoil.dat
# ref_frame.dat


# from aircraft import Section


class Wing(GeomBase):

    # airfoil profiles
    airfoil_root = Input("whitcomb")
    airfoil_tip = Input("simm_airfoil")

    # imported parameters from input file
    mach_cruise = Input(I.Mach_cruise)
    altitude_cruise = Input(I.Altitude_cruise)
    weight_TO = Input(I.Weight_TO)
    area_wing = Input(I.Wing_area)
    aspect_ratio = Input(I.Aspect_ratio)
    wing_highlow = Input("low")

    # some other parameters
    twist = Input(-5)
    is_mirrored = Input(True)


    @Attribute
    def pressure(self):
        return 101325*(1-(0.0065*self.altitude_cruise)/288)**(9.81/(287*0.0065))

    @Attribute
    def dynamic_pressure(self):
        return 0.7*self.pressure*self.mach_cruise**2

    @Attribute
    def mach_drag_divergence(self):
        return self.mach_cruise + 0.03

    @Attribute
    def sweep_quarter_chord(self):
        if self.mach_cruise <0.7:
            sweep = np.rad2deg(np.arccos(1))
        else:
            sweep = np.rad2deg(np.arccos(0.75*0.935/self.mach_drag_divergence))
        return sweep

    @Attribute
    def span(self):
        return np.sqrt(self.area_wing*self.aspect_ratio)

    @Attribute
    def taper_ratio(self):
        return 0.2*(2-np.deg2rad(self.sweep_quarter_chord))

    @Attribute
    def chord_root(self):
        return 2*self.area_wing/(self.span*(1+self.taper_ratio))

    @Attribute
    def chord_tip(self):
        return self.taper_ratio*self.chord_root

    @Attribute
    def sweep_leading_edge(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_quarter_chord))- 4/self.aspect_ratio *(-1/4) *(1-self.taper_ratio)/(1+self.taper_ratio)))

    @Attribute
    def sweep_mid_chord(self):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(self.sweep_quarter_chord)) - 4 / self.aspect_ratio * (1 / 4) * (1 - self.taper_ratio) / (1 + self.taper_ratio)))

    @Attribute
    def mean_aerodynamic_chord(self):
        return self.chord_root * 2/3 * (1+self.taper_ratio +self.taper_ratio**2)/(1+self.taper_ratio)

    @Attribute
    def y_mean_aerodynamic_chord(self):
        return self.span/2 * (self.chord_root-self.mean_aerodynamic_chord)/(self.chord_root-self.chord_tip)

    @Attribute
    def lift_coefficient(self):
        return self.weight_TO/(self.dynamic_pressure*self.area_wing)

    @Attribute
    def thickness_to_chord(self):
        cos_halfsweep = np.cos(np.deg2rad(self.sweep_mid_chord))
        option_one = (cos_halfsweep**3 * (0.935 - self.mach_drag_divergence * cos_halfsweep) - 0.115 *self.lift_coefficient**1.5)/(cos_halfsweep**2)

        if option_one > 0.18:
            toverc = 0.18
        elif option_one < 0.1:
            toverc = 0.1
        else:
            toverc =option_one

        return toverc

    @Attribute
    def dihedral(self):
        if self.wing_highlow == "high":
            dihed = 3-self.sweep_quarter_chord/10 -2
        elif self.wing_highlow == "low":
            dihed = 3 - self.sweep_quarter_chord / 10 + 2
        return dihed

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]




    @Part
    def root_airfoil(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.chord_root,
                       thickness_factor=self.thickness_to_chord,
                       factor=0.14,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.chord_tip,
                       thickness_factor=self.thickness_to_chord,
                       factor=0.24,
                       position=translate(
                           rotate(self.position, "y", np.deg2rad(self.twist)),  # apply twist angle
                           "y", self.span/2,
                           "x", self.span/2 * np.tan(np.deg2rad(self.sweep_leading_edge)),
                           "Z", self.span/2 * np.tan(np.deg2rad(self.dihedral))),  # apply sweep
                       mesh_deflection=0.0001)

    @Part
    def right_wing(self):
        return LoftedSurface(profiles=self.profiles,
                             hidden=not (__name__ == '__main__'),
                             mesh_deflection=0.0001)

    @Part
    def left_wing(self):
        return MirroredShape(shape_in=self.right_wing,
                             reference_point=self.position,
                             # Two vectors to define the mirror plane
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=0.0001)

if __name__ == '__main__':
    from parapy.gui import display
    obj = Wing()
    display(obj)




























