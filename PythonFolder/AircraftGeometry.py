import numpy as np
from parapy.core import *
from parapy.geom import *


from aircraft import Wing
from aircraft import Fuselage
from aircraft import Vertical_Tail
from aircraft import Horizontal_Tail
from aircraft import CG_calculations
from aircraft import Propeller_engine
from aircraft import Fan_engine
from aircraft import Seat

import aircraft.Import_Input as I

class AircraftGeometry(GeomBase):



    @Part
    def fuselage(self):
        return Fuselage()

    @Part
    def main_wing(self):
        return Wing()

    @Part
    def vertical_tail(self):
        return Vertical_Tail()

    @Part
    def horizontal_tail(self):
        return Horizontal_Tail()

    @Part
    def propeller(self):
        return Propeller_engine()

    @Part
    def fan(self):
        return Fan_engine(position=translate(self.position,
                                             'x', Wing().x_le_mac -0.5*Wing().mean_aerodynamic_chord,
                                             'y', 0.35*Wing().span/2,
                                             'z', -4))

    @Part
    def fan2(self):
        return Fan_engine(position=translate(self.position,
                                             'x', Wing().x_le_mac -0.5*Wing().mean_aerodynamic_chord,
                                             'y', -0.35*Wing().span/2,
                                             'z', -4))

    @Part
    def cg_range(self):
        return CG_calculations()

    @Part
    def seatt(self):
        return Seat()



if __name__ == '__main__':
    from parapy.gui import display
    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)