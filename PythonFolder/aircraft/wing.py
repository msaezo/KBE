import numpy as np



import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *


from aircraft.airfoil import Airfoil
from aircraft.fuselage import Fuselage


# this file makes use of the following files:
# airfoil.py
# Import_Input.xls
# whitcomb.dat
# simm_airfoil.dat
# ref_frame.dat


# from aircraft import Section


class Wing(GeomBase):

    # airfoil profiles
    airfoil_root = Input("aircraft\whitcomb")
    airfoil_tip = Input("aircraft\simm_airfoil")

    mach_cruise = Input(I.Mach_cruise)#I.Mach_cruise)
    altitude_cruise = Input(I.Altitude_cruise)
    weight_TO = Input(I.Weight_TO)
    area_wing = Input(I.Wing_area)
    aspect_ratio = Input(I.Aspect_ratio)
    wing_highlow = Input("low")
    wing_mass_fraction = Input(I.Wing_mass_fraction)
    propulsion_mass_fraction = Input(I.Propulsion_system_mass_fraction)
    wing_cg_loc = Input(I.Wing_cg_loc)
    propulsion_cg_loc = Input(I.Propulsion_system_cg_loc)
    oew_cg_loc = Input(I.OEW_cg_loc)
    fuselage_mass_fraction = Input(I.Fuselage_mass_fraction)
    empennage_mass_fraction = Input(I.Empennage_mass_fraction)
    fixed_equipment_mass_fraction = Input(I.Fixed_equipment_mass_fraction)

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
        if self.mach_cruise < 0.7:
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
        return np.rad2deg(np.arctan(np.tan( np.deg2rad(self.sweep_quarter_chord) ) - 4/self.aspect_ratio *(-1/4) *(1-self.taper_ratio)/(1+self.taper_ratio)))

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
    def dihedral(self):
        if self.wing_highlow == "high":
            dihed = 3-self.sweep_quarter_chord/10 -2
        elif self.wing_highlow == "low":
            dihed = 3 - self.sweep_quarter_chord / 10 + 2
        else :
            dihed=0
        return dihed

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]



    @Attribute
    def x_wing_cg(self):
        wing_sum = self.wing_cg_loc * self.wing_mass_fraction
        propulsion_sum = self.propulsion_cg_loc * self.propulsion_mass_fraction
        return self.mean_aerodynamic_chord * (wing_sum + propulsion_sum) / (
                    self.wing_mass_fraction + self.propulsion_mass_fraction)

    @Attribute
    def x_le_mac(self):
        mass_fuselage = self.fuselage_mass_fraction + self.empennage_mass_fraction + self.fixed_equipment_mass_fraction
        mass_wing = self.wing_mass_fraction + self.propulsion_mass_fraction
        mass_wing_over_mass_fuse = mass_wing / mass_fuselage
        return Fuselage().x_fuselage_cg + self.mean_aerodynamic_chord * (
                    (self.x_wing_cg / self.mean_aerodynamic_chord) * mass_wing_over_mass_fuse - self.oew_cg_loc * (
                    1 + mass_wing_over_mass_fuse))

    @Attribute
    def wing_x_shift(self):
        return self.x_le_mac - self.y_mean_aerodynamic_chord * np.tan(np.deg2rad(self.sweep_leading_edge))


    @Attribute
    def wing_z_shift(self):
        if self.wing_highlow == "high":
            pos = Fuselage().diameter_fuselage_outer * 0.9 / 2
        elif self.wing_highlow == "low":
            pos = -Fuselage().diameter_fuselage_outer * 0.8 / 2
        return pos


    @Part
    def root_airfoil(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.chord_root,
                       thickness_factor=0.14,
                       position=translate(self.position,
                                          "x", self.wing_x_shift,
                                          "Z", self.wing_z_shift),
                       factor=0.14,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.chord_tip,
                       thickness_factor=0.1,
                       factor=0.24,
                       position=translate(
                           rotate(self.position, "y", np.deg2rad(self.twist)),  # apply twist angle
                           "y", self.span/2,
                           "x", self.wing_x_shift + self.span/2 * np.tan(np.deg2rad(self.sweep_leading_edge)),
                           "Z", self.wing_z_shift + self.span/2 * np.tan(np.deg2rad(self.dihedral))),
                       mesh_deflection=0.0001)

    @Part
    def right_wing_surface(self):
        return LoftedSurface(profiles=self.profiles,

                             mesh_deflection=0.0001)

    @Part
    def left_wing_surface(self):
        return MirroredShape(shape_in=self.right_wing_surface,
                             reference_point=self.position,
                             # Two vectors to define the mirror plane
                             vector1=self.position.Vz,
                             vector2=self.position.Vx,
                             mesh_deflection=0.0001)

if __name__ == '__main__':
    from parapy.gui import display
    obj = Wing()
    display(obj)




























