import numpy as np
from parapy.core import *
from parapy.geom import *
import Import_Input as I
from airfoil import Airfoil
from wing import Wing
from fuselage import Fuselage
from ref_frame import Frame
from empennage import Horizontal_Tail
from empennage import Vertical_Tail


class AircraftGeometry(GeomBase):


    @Part
    def fuselage(self):
        return Fuselage(color="green")

    @Part
    def main_wing(self):
        return Wing(color="yellow")

    @Part
    def vertical_Tail(self):
        return Vertical_Tail(color="purple")

    @Part
    def horizontal_Tail(self):
        return Horizontal_Tail(color="purple")




if __name__ == '__main__':
    from parapy.gui import display
    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)