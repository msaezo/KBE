import numpy as np
import aircraft.Import_Input as In

from parapy.core import *
from parapy.geom import *

from aircraft.fuselage import Fuselage
from aircraft.wing import Wing


# Kerosene Based CG calculations
class CGCalculations(GeomBase):
    payload_cg_loc = Input(In.Payload_cg_loc)
    fuel_cg_loc = Input(In.Fuel_cg_loc)
    mass_oew = Input(In.OEW_mass_fraction)
    mass_payload = Input(In.Payload_mass_fraction)
    mass_fuel = Input(In.Fuel_mass_fraction)
    mean_aerodynamic_chord = Input(Wing().mean_aerodynamic_chord)
    x_le_mac = Input(Wing().x_le_mac)
    length_fuselage = Input(Fuselage().length_fuselage)

    # estimate the oew cg location
    @Attribute
    def x_oew(self):
        return self.x_le_mac + 0.25 * self.mean_aerodynamic_chord

    # estimate the payload cg location
    @Attribute
    def x_payload(self):
        return self.payload_cg_loc * self.length_fuselage

    # estimate the fuel cg location
    @Attribute
    def x_fuel(self):
        return self.x_le_mac + self.fuel_cg_loc * self.mean_aerodynamic_chord

    # calculate all possible combinations of OEW, payload and fuel
    @Attribute
    def oew_and_payload(self):
        return (self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (self.mass_oew + self.mass_payload)

    @Attribute
    def oew_and_payload_and_fuel(self):
        return (self.x_fuel * self.mass_fuel + self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / \
               (self.mass_fuel + self.mass_oew + self.mass_payload)

    @Attribute
    def oew_and_fuel(self):
        return (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (self.mass_fuel + self.mass_oew)

    # the minimum of the aforementioned combinations is the most forward possible cg
    @Attribute
    def cg_forward(self):
        return min(self.oew_and_fuel, self.oew_and_payload_and_fuel, self.oew_and_payload)

    # the maximum of the aforementioned combinations is the most aft possible cg
    @Attribute
    def cg_aft(self):
        return max(self.oew_and_fuel, self.oew_and_payload_and_fuel, self.oew_and_payload)

    # create a visual representation of the front and aft cg locations in blue for the kerosene based aircraft
    @Part
    def cg_front(self):
        return LineSegment(start=Point(self.cg_forward, -4, 0),
                           end=Point(self.cg_forward, 4, 0),
                           line_thickness=2,
                           color='blue')

    @Part
    def cg_rear(self):
        return LineSegment(start=Point(self.cg_aft, -4, 0),
                           end=Point(self.cg_aft, 4, 0),
                           line_thickness=2,
                           color='blue')
