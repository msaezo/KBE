import numpy as np
from parapy.core import *
from parapy.geom import *


from aircraft import Wing
from aircraft import Fuselage

import aircraft.Import_Input as I

class AircraftGeometry(GeomBase):


    @Part
    def fuselage(self):
        return Fuselage(color="green")

    @Part
    def main_wing(self):
        return Wing(color="yellow")




if __name__ == '__main__':
    from parapy.gui import display
    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)