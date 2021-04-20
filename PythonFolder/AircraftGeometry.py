
from parapy.core import *
from parapy.geom import *


from aircraft import Wing
from aircraft import Fuselage
from aircraft import Vertical_Tail
from aircraft import Horizontal_Tail
from aircraft import CG_calculations
from aircraft import Propeller_engine
from aircraft import Fan_engine
from aircraft import Propulsion_System




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
    def prop_system(self):
        return Propulsion_System()

    @Part
    def cg_range(self):
        return CG_calculations()




if __name__ == '__main__':
    from parapy.gui import display
    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)