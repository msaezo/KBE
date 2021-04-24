import numpy as np
import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *


from aircraft.fuselage import Fuselage
from aircraft.wing import Wing



#Kerosene Based CG
class CG_calculations(GeomBase):

    payload_cg_loc = Input(I.Payload_cg_loc)
    fuel_cg_loc = Input(I.Fuel_cg_loc)
    mass_oew = Input(I.OEW_mass_fraction)
    mass_payload = Input(I.Payload_mass_fraction)
    mass_fuel = Input(I.Fuel_mass_fraction)

    @Attribute
    def x_oew(self):
        return Wing().x_le_mac+0.25*Wing().mean_aerodynamic_chord

    @Attribute
    def x_payload(self):
        return self.payload_cg_loc*Fuselage().length_fuselage

    @Attribute
    def x_fuel(self):
        return Wing().x_le_mac + self.fuel_cg_loc*Wing().mean_aerodynamic_chord

    @Attribute
    def cg_forward(self):
        OEW_and_payload = (self.x_oew*self.mass_oew + self.x_payload*self.mass_payload)/(self.mass_oew + self.mass_payload)
        OEW_and_payload_and_fuel = (self.x_fuel*self.mass_fuel + self.x_oew*self.mass_oew + self.x_payload*self.mass_payload)/(self.mass_fuel + self.mass_oew + self.mass_payload)
        OEW_and_fuel = (self.x_oew*self.mass_oew + self.x_fuel*self.mass_fuel)/(self.mass_fuel + self.mass_oew)
        return min(OEW_and_fuel, OEW_and_payload_and_fuel, OEW_and_payload)

    @Attribute
    def cg_aft(self):
        OEW_and_payload = (self.x_oew*self.mass_oew + self.x_payload*self.mass_payload)/(self.mass_oew + self.mass_payload)
        OEW_and_paylod_and_fuel = (self.x_fuel*self.mass_fuel + self.x_oew*self.mass_oew + self.x_payload*self.mass_payload)/(self.mass_fuel + self.mass_oew + self.mass_payload)
        OEW_and_fuel = (self.x_oew*self.mass_oew + self.x_fuel*self.mass_fuel)/(self.mass_fuel + self.mass_oew)
        return max(OEW_and_fuel, OEW_and_paylod_and_fuel, OEW_and_payload)

    @Part
    def cg_front(self):
        return LineSegment(start=Point(self.cg_forward, -4, 0),
                           end=Point(self.cg_forward, 4, 0),
                           color='green',
                           line_thickness=2)

    @Part
    def cg_rear(self):
        return LineSegment(start=Point(self.cg_aft, -4, 0),
                           end=Point(self.cg_aft, 4, 0),
                           color='green',
                           line_thickness=2)



#Hydrogen Based CG  ---- Not sure if imports are correct (hardcoded obviously not) but calculations are.
#Maybe place in a different file so we only run it if necessary.
class CG_calculations(GeomBase):
    payload_cg_loc = Input(I.Payload_cg_loc)
    fuel_cg_loc = # here should be the middle point of the tanks
    tank_cg_loc = # here should be the middle point of the tanks
    mass_fuel   = # output from range calculation
    g_i         = Input(0.5) # gravimetric index taken from report on flying V, cryogenic tank
    mass_oew = Input(I.OEW_mass_fraction)
    mass_payload = Input(I.Payload_mass_fraction)

    @Attribute
    def mass_tank(self):
        return (self.mass_fuel-self.g_i*self.mass_fuel)/self.g_i

    @Attribute           # Are we missing in this function the weight of the fuselage? or it is included?
    def x_oew(self):     #  HERE I ADD THE CENTER OF GRAVITY CONTRIBUTION OF THE TANK WEIGHT
        return ((Wing().x_le_mac+0.25*Wing().mean_aerodynamic_chord)*self.mass_oew + self.mass_tank *\
                self.tank_cg_loc)/(self.mass_oew + self.mass_tank)

    @Attribute
    def x_payload(self):
        return self.payload_cg_loc * Fuselage().length_fuselage

    @Attribute
    def x_fuel(self):
        return Wing().x_le_mac + self.fuel_cg_loc * Wing().mean_aerodynamic_chord

    @Attribute
    def cg_forward(self):
        OEW_and_payload = (self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                    self.mass_oew + self.mass_payload)
        OEW_and_payload_and_fuel = (
                                               self.x_fuel * self.mass_fuel + self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                                               self.mass_fuel + self.mass_oew + self.mass_payload)
        OEW_and_fuel = (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (
                    self.mass_fuel + self.mass_oew)
        return min(OEW_and_fuel, OEW_and_payload_and_fuel, OEW_and_payload)

    @Attribute
    def cg_aft(self):
        OEW_and_payload = (self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                    self.mass_oew + self.mass_payload)
        OEW_and_paylod_and_fuel = (
                                              self.x_fuel * self.mass_fuel + self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                                              self.mass_fuel + self.mass_oew + self.mass_payload)
        OEW_and_fuel = (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (
                    self.mass_fuel + self.mass_oew)
        return max(OEW_and_fuel, OEW_and_paylod_and_fuel, OEW_and_payload)

    @Part
    def cg_front(self):
        return LineSegment(start=Point(self.cg_forward, -4, 0),
                           end=Point(self.cg_forward, 4, 0),
                           color='green',
                           line_thickness=2)

    @Part
    def cg_rear(self):
        return LineSegment(start=Point(self.cg_aft, -4, 0),
                           end=Point(self.cg_aft, 4, 0),
                           color='green',
                           line_thickness=2)