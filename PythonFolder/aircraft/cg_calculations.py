import numpy as np
import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *

from aircraft.fuselage import Fuselage
from aircraft.wing import Wing


# Kerosene Based CG
class CG_calculations(GeomBase):
    payload_cg_loc = Input(I.Payload_cg_loc)
    fuel_cg_loc = Input(I.Fuel_cg_loc)
    mass_oew = Input(I.OEW_mass_fraction)
    mass_payload = Input(I.Payload_mass_fraction)
    mass_fuel = Input(I.Fuel_mass_fraction)

    @Attribute
    def x_oew(self):
        return Wing().x_le_mac + 0.25 * Wing().mean_aerodynamic_chord

    @Attribute
    def x_payload(self):
        return self.payload_cg_loc * Fuselage().length_fuselage

    @Attribute
    def x_fuel(self):
        return Wing().x_le_mac + self.fuel_cg_loc * Wing().mean_aerodynamic_chord

    @Attribute
    def cg_forward(self):
        oew_and_payload = (self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                    self.mass_oew + self.mass_payload)
        oew_and_payload_and_fuel = (self.x_fuel * self.mass_fuel + self.x_oew * self.mass_oew
                                    + self.x_payload * self.mass_payload) \
                                   /  (self.mass_fuel + self.mass_oew + self.mass_payload)
        oew_and_fuel = (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (self.mass_fuel + self.mass_oew)
        return min(oew_and_fuel, oew_and_payload_and_fuel, oew_and_payload)

    @Attribute
    def cg_aft(self):
        oew_and_payload = (self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                    self.mass_oew + self.mass_payload)
        oew_and_payload_and_fuel = ( self.x_fuel * self.mass_fuel
                                     + self.x_oew * self.mass_oew
                                     + self.x_payload * self.mass_payload) \
                                   / (self.mass_fuel + self.mass_oew + self.mass_payload)
        oew_and_fuel = (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (self.mass_fuel + self.mass_oew)
        return max(oew_and_fuel, oew_and_payload_and_fuel, oew_and_payload)

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


