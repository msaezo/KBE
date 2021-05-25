import numpy as np
from parapy.core import *
from parapy.geom import *
from math import *

import aircraft.Import_Input as I
from aircraft.airfoil import Airfoil




class Lifting_Surface(GeomBase):


    # airfoil profiles
    airfoil_root = Input("aircraft\simm_airfoil")
    airfoil_tip  = Input("aircraft\simm_airfoil")

    root_chord  = Input(5)
    thickness_to_chord_root = Input(0.1)
    factor_root = Input(0.24)

    tip_chord = Input(1)
    thickness_to_chord_tip = Input(0.1)
    factor_tip = Input(0.24)

    x_shift_root = Input(5)
    y_shift_root = Input(0)
    z_shift_root = Input(1)
    x_shift_tip = Input(6)
    y_shift_tip = Input(2)
    z_shift_tip = Input(2)
    rotate = Input(0)
    twist = Input(0)


    @Part
    def root_airfoil(self):  # root airfoil will receive self.position as default
        return Airfoil(airfoil_name=self.airfoil_root,
                       chord=self.root_chord,
                       thickness_factor=self.thickness_to_chord_root,
                       position=translate(rotate(self.position, "x", np.deg2rad(self.rotate)),
                                          "x", self.x_shift_root,
                                          "y", self.y_shift_root,
                                          "Z", self.z_shift_root),
                       factor=self.factor_root,
                       mesh_deflection=0.0001)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_tip,
                       chord=self.tip_chord,
                       thickness_factor=self.thickness_to_chord_tip,
                       factor=self.factor_tip,
                       position=translate(
                           rotate(self.position, "x", np.deg2rad(self.rotate)),  # apply twist angle
                           "x", self.x_shift_tip,
                           "y", self.y_shift_tip,
                           "z", self.z_shift_tip),
                       mesh_deflection=0.0001)

    @Attribute  # required input for the superclass LoftedSolid
    def profiles(self):
        return [self.root_airfoil, self.tip_airfoil]

    @Part
    def right_wing_surface(self):
        return LoftedSurface(profiles=self.profiles,
                             mesh_deflection=0.0001)

