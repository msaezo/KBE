import numpy as np
from parapy.core import *
from parapy.geom import *
import Import_Input as I
from airfoil import Airfoil
from wing import Wing
from fuselage import Fuselage
from ref_frame import Frame

if __name__ == '__main__':
    from parapy.gui import display
    obj1 = Fuselage(label="fuselage")
    obj2 = Wing(label="wing")
    display(obj1, obj2)


