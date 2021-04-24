# This file is supposed to:
# 1. select the input file (the excel file)
# 2. call Aircraft Geometry
# 3. Check whether "troublemaker" parameters meet the expected values (if problems, warnings should pop)
# 4. If they do meet the expected values, create an output file with CAD, input parameters and some key parameters
# 5. If they do not meet the expected values:
#   5.a. Take action depending on which "troublemaker" parameter failed
#   5.b. Run Aircraft Geometry
#   5.c. Go back to step 3 and repeat

# "Troublemaker" Parameters:
#   - Cd: Nan               -- Action:
#       - Decrease flight altitude          (might not be good)
#       - Increase wing area                (might not be good)
#       - Assume L/D ratio of 20            (best solution till now)
#       - WARNING: -Nan detected, action point taken -
#   - Tank diameter > value -- Action       (the value should be the one we have currently, more modifies too much fus)
#       - Decrease range                    (good option, but not preferable)
#       - Give options to user              (input different airfoil,...)
#       - WARNING: - Tank diameter too big, action point taken -
#   - C.G.Range Hydrogen  > C.G. Range Kerosene   -- Just give warning
#       - WARNING: - Problems might arise due to higher C.G. range than before -
#   - Any other?

# Some other doubts I have at the moment, or improvements for future.
#   - Include the drag of the fuselage, theoretically we could extend it and drag would not increase (good that tank is limited by the fus length)
#   - Fuel weight defined twice? once in fuel mass fraction (guessing kerosene) twice range (guessing hydrogen)
#   - Cargo not included at all
from parapy.core import *
from parapy.geom import *

from AircraftGeometry import AircraftGeometry


AircraftGeometry()