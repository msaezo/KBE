import aircraft.Import_Input as In
import warnings

from parapy.core import *
from parapy.geom import *

from aircraft.energy import Energy1
from aircraft.fuselage import Fuselage
from aircraft.wing import Wing
from aircraft.cg_calculations import CGCalculations


# Hydrogen Based CG  ---- Not sure if imports are correct (hardcoded obviously not) but calculations are.
# Maybe place in a different file so we only run it if necessary.
class CGCalculationsHyd(GeomBase):
    mtow = Input(In.Weight_TO)
    payload_cg_loc = Input(In.Payload_cg_loc)
    tank_length = Input(Energy1().length_tank)  #
    tank_front_loc = Input(Fuselage().length_cockpit)
    vol_needed = Input(Energy1().vol_needed)
    hyd_density = Input(In.hyd_density)
    g_i = Input(0.5)  # gravimetric index taken from report on flying V, cryogenic tank
    mass_oew_fr = Input(In.OEW_mass_fraction)
    mass_payload_fr = Input(In.Payload_mass_fraction)
    max_cg_fuel = Input(CGCalculations().cg_aft)
    min_cg_fuel = Input(CGCalculations().cg_forward)
    x_le_mac = Input(Wing().x_le_mac)
    mean_aerodynamic_chord = Input(Wing().mean_aerodynamic_chord)
    length_fuselage = Input(Fuselage().length_fuselage)

    @Attribute
    def mtom(self):
        return self.mtow / 9.81

    @Attribute
    def mass_oew(self):
        return self.mtom * self.mass_oew_fr

    @Attribute
    def mass_payload(self):
        return self.mtom * self.mass_payload_fr

    @Attribute
    def x_fuel(self):
        return self.tank_length / 2 + self.tank_front_loc

    @Attribute
    def tank_cg_loc(self):
        return self.x_fuel

    @Attribute
    def mass_fuel(self):
        return self.vol_needed * self.hyd_density

    @Attribute
    def mass_tank(self):
        return (self.mass_fuel - self.g_i * self.mass_fuel) / self.g_i

    @Attribute  # Are we missing in this function the weight of the fuselage? or it is included?
    def x_oew(self):  # HERE I ADD THE CENTER OF GRAVITY CONTRIBUTION OF THE TANK WEIGHT
        return ((self.x_le_mac + 0.25 * self.mean_aerodynamic_chord) * self.mass_oew + self.mass_tank
                * self.tank_cg_loc) / (self.mass_oew + self.mass_tank)

    @Attribute
    def x_payload(self):
        return self.payload_cg_loc * self.length_fuselage

    @Attribute
    def cg_forward(self):
        oew_and_payload = (self.x_oew * self.mass_oew
                           + self.x_payload * self.mass_payload) / (self.mass_oew + self.mass_payload)
        oew_and_payload_and_fuel = (self.x_fuel * self.mass_fuel + self.x_oew * self.mass_oew + self.x_payload
                                    * self.mass_payload) / (self.mass_fuel + self.mass_oew + self.mass_payload)
        oew_and_fuel = (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (self.mass_fuel + self.mass_oew)
        min_cg_hyd = min(oew_and_fuel, oew_and_payload_and_fuel, oew_and_payload)
        if min_cg_hyd > self.max_cg_fuel:
            msg = "The most forward center of gravity location for the hydrogen aircraft is less stable than " \
                  "the most after center of gravity location for the kerosene aircraft. Aircraft might be unstable" \
                  "Suggested options:" \
                  "     - Further investigation of stability required"
            warnings.warn(msg)

        return min_cg_hyd

    @Attribute
    def cg_aft(self):
        oew_and_payload = (self.x_oew * self.mass_oew + self.x_payload * self.mass_payload) / (
                self.mass_oew + self.mass_payload)
        oew_and_payload_and_fuel = (self.x_fuel * self.mass_fuel + self.x_oew * self.mass_oew + self.x_payload
                                    * self.mass_payload) / (self.mass_fuel + self.mass_oew + self.mass_payload)
        oew_and_fuel = (self.x_oew * self.mass_oew + self.x_fuel * self.mass_fuel) / (
                self.mass_fuel + self.mass_oew)
        max_cg_hyd = max(oew_and_fuel, oew_and_payload_and_fuel, oew_and_payload)

        if max_cg_hyd > self.max_cg_fuel:
            msg = "The most after center of gravity location for the hydrogen aircraft is less stable than " \
                  "the most after center of gravity location for the kerosene aircraft. Aircraft might be unstable" \
                  "Suggested options:" \
                  "     - Further investigation of stability required"
            warnings.warn(msg)

        elif (max_cg_hyd - self.cg_forward) >= (self.max_cg_fuel - self.min_cg_fuel):
            msg = "The center of gravity range of the hydrogen aircraft is larger than the center of gravity range" \
                  "of the kerosene aircraft. Aircraft might be unstable" \
                  "Suggested options:" \
                  "     - Further investigation of stability required"
            warnings.warn(msg)

        return max_cg_hyd

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
