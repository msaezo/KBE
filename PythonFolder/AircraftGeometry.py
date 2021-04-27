from parapy.core import *
from parapy.geom import *

from aircraft import Wing
from aircraft import Fuselage
from aircraft import Vertical_Tail
from aircraft import Horizontal_Tail
from aircraft import CG_calculations
from aircraft import CG_calculations_hyd

from aircraft import Propulsion_System
from aircraft import Q3D
from aircraft import Drag
from aircraft import Energy
from aircraft import Tanks
from aircraft import new_fuselage1
from aircraft import new_fuselage2

import xlrd
import warnings
from math import *


class AircraftGeometry(Base):

    #######################################################################################################
    #####                                                                                             #####
    #####   This is where we open the input file and parse the values to variables with the same name #####
    #####                                                                                             #####
    #######################################################################################################

    workbook = xlrd.open_workbook('aircraft\KBE_Input.xls')
    worksheet = workbook.sheet_by_name('Input')

    # Fuselage parameters
    for i in range(2, 16):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Wing parameters
    for i in range(18, 23):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Engine parameters
    for i in range(25, 30):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # CG parameters
    for i in range(32, 41):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")
    for i in range(42, 50):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Landing gear parameters
    for i in range(52, 55):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Empenage parameters
    for i in range(57, 65):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Flight parameters
    for i in range(67, 72):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    ###############################################################################
    #####                                                                     #####
    ##### Inputting the variables to parapy with the proper naming convention #####
    #####                                                                     #####
    ###############################################################################

    # imported parameters from input file
    n_pax                     = Input(Number_of_passengers)
    width_aisle               = Input(Width_aisle)
    width_seat                = Input(Width_seat)
    width_armrest             = Input(Width_armrest)
    clearance_seat            = Input(Seat_clearance)
    length_cockpit            = Input(Length_cockpit)
    length_tailcone_over_diam = Input(Length_tailcone_over_Diameter_Fuselage)
    length_nosecone_over_diam = Input(Length_nosecone_over_Diameter_Fuselage)
    length_tail_over_diam     = Input(Length_Tail_over_Diameter_Fuselage)
    height_floor              = Input(Height_floor)
    height_shoulder           = Input(Height_shoulder)
    luggage_per_pax           = Input(Luggage_per_pax)
    weight_cargo              = Input(Cargo)
    kcc                       = Input(Kcc)

    mach_cruise     = Input(Mach_cruise)
    altitude_cruise = Input(Altitude_cruise)
    weight_TO       = Input(Weight_TO)
    wing_loading    = Input(Wing_loading)
    aspect_ratio    = Input(Aspect_ratio)
    wing_highlow    = Input("low")

    n_engines          = Input(N_engines)
    thrust_to          = Input(Thrust_TO)
    turbine_inlet_temp = Input(Temp_T_4)
    phi                = Input(Phi)
    bypass_ratio       = Input(BPR)

    wing_mass_fraction            = Input(Wing_mass_fraction)
    propulsion_mass_fraction      = Input(Propulsion_system_mass_fraction)
    fuselage_mass_fraction        = Input(Fuselage_mass_fraction)
    empennage_mass_fraction       = Input(Empennage_mass_fraction)
    fixed_equipment_mass_fraction = Input(Fixed_equipment_mass_fraction)
    mass_oew                      = Input(OEW_mass_fraction)
    mass_payload                  = Input(Payload_mass_fraction)
    mass_fuel                      = Input(Fuel_mass_fraction)

    wing_cg_loc            = Input(Wing_cg_loc)
    propulsion_cg_loc      = Input(Propulsion_system_cg_loc)
    fuselage_cg_loc        = Input(Fuselage_cg_loc)
    empennage_cg_loc       = Input(Empennage_cg_loc)
    fixed_equipment_cg_loc = Input(Fixed_equipment_cg_loc)
    oew_cg_loc             = Input(OEW_cg_loc)
    payload_cg_loc         = Input(Payload_cg_loc)
    fuel_cg_loc            = Input(Fuel_cg_loc)

    volume_HT                      = Input(Tail_volume_horizontal)
    volume_VT                      = Input(Tail_volume_vertical)
    aspect_Ratio_horizontal        = Input(aspect_Ratio_horizontal)
    aspect_Ratio_vertical          = Input(aspect_Ratio_vertical)
    taper_Ratio_horizontal         = Input(taper_Ratio_horizontal)
    taper_Ratio_vertical           = Input(taper_Ratio_vertical)
    sweep_three_quarter_horizontal = Input(sweep_three_quarter_horizontal)
    sweep_leading_edge_vertical    = Input(sweep_leading_edge_vertical)

    range          = Input(Range)
    efficiency     = Input(total_efficiency)
    energy_density = Input(energy_density)
    hyd_density    = Input(hyd_density)
    skinfric_coeff = Input(eq_skinfriction_coefficient)

    #######################################################################
    #####                                                             #####
    ##### Declaring input warnings if it is out of recommended bounds #####
    #####                                                             #####
    #######################################################################
    @Attribute
    def warnings_inputs(self):

        if self.mach_cruise < 0.75 or self.mach_cruise > 0.92:
            msg = "The mach number on the Input File might be outside of bounds for typical transport aviation." \
                  "Suggested options:" \
                  "     - Change mach_cruise between the bounds" \
                  "     - 0.75 and 0.92"
            warnings.warn(msg)


        pax_average = 0.0012*self.weight_TO/9.81 + 86.01
        if self.n_pax <= pax_average*0.75 or self.n_pax >= pax_average*1.25:
            msg = "The number of passengers on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change passengers using the following approximation" \
                  "     - n_pax = 0.0012 * MTOW [kg] + 86.01"
            warnings.warn(msg)

        wing_loading_average = 0.0005*self.weight_TO/9.81 + 547.52
        if self.wing_loading <= wing_loading_average*0.77 or self.wing_loading >= wing_loading_average*1.23:
            msg = "The wing loading on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change wing_loading using the following approximation" \
                  "     - wing_loading = 0.0005 * MTOW [kg] + 547.52"
            warnings.warn(msg)

        if self.aspect_ratio < 7.73 or self.aspect_ratio > 9.44:
            msg = "The aspect ratio on the Input File might be outside of bounds for the typical transportation aircraft. " \
                  "Suggested options:" \
                  "     - Change to aspect_ratio between the following bounds" \
                  "     - 7.73 to 9.44"
            warnings.warn(msg)

        span = sqrt(self.aspect_ratio*self.weight_TO/9.81/self.wing_loading)
        if span >= 80 or span <= 22:
            msg = "The wing span resulting from the Input File might be outside of bounds for the typical transportation aircraft. " \
                  "Suggested options:" \
                  "     - Change the aspect ratio between the bounds" \
                  "     - Change the wing loading"
            warnings.warn(msg)

        range_average = 0.0323 * self.weight_TO / 9.81 + 2819.4
        if self.range < range_average * 0.60 or self.range > range_average * 1.40:
            msg = "The range on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change range using the following approximation" \
                  "     - range = 0.0323 * MTOW [kg] + 2819.4"
            warnings.warn(msg)
        finish = 'Look in terminal for warnings'
        return finish

    #Some attributes to easily check in parapy GUI
    @Attribute
    def volume_needed(self):
        return Energy().vol_needed

    @Attribute
    def cl_in(self):
        return Wing().lift_coefficient

    @Attribute
    def cl_out(self):
        return Q3D().cldes

    @Attribute
    def cd_out(self):
        return Q3D().cddes

    @Attribute
    def aLpha(self):
        return Q3D().alpha

    @Attribute
    def reynolds(self):
        return Q3D().reynolds

    @Attribute
    def cd_total(self):
        return Drag().drag_coefficient_total

    @Attribute
    def drag_total(self):
        return Drag().drag

    # Variable input for new fuselage depending on tank size
    # if tanks dont fit inside fuselage use new profiles that do fit
    # else reuse old profiles and recreate fuselage as is
    @Attribute
    def new_fuselage_input(self):
        if Tanks().tank_max_dim > Fuselage().diameter_fuselage_inner / 2:
            input = [Fuselage().outer_profile_set[0],
                     Fuselage().outer_profile_set[1],
                     new_fuselage1().new_profile_first.composed_crv,
                     new_fuselage1().new_profile_set[0].composed_crv,
                     new_fuselage1().new_profile_set[1].composed_crv,
                     new_fuselage1().new_profile_set[2].composed_crv,
                     new_fuselage1().new_profile_set[3].composed_crv,
                     new_fuselage1().new_profile_set[4].composed_crv,
                     Fuselage().outer_profile_set[8],
                     Fuselage().outer_profile_set[9],
                     Fuselage().outer_profile_set[10]]
        else:
            input = [Fuselage().outer_profile_set[0],
                     Fuselage().outer_profile_set[1],
                     Fuselage().outer_profile_set[2],
                     Fuselage().outer_profile_set[3],
                     Fuselage().outer_profile_set[4],
                     Fuselage().outer_profile_set[5],
                     Fuselage().outer_profile_set[6],
                     Fuselage().outer_profile_set[7],
                     Fuselage().outer_profile_set[8],
                     Fuselage().outer_profile_set[9],
                     Fuselage().outer_profile_set[10]]
        return input

    ##########################################
    #####                                #####
    ##### Creating the parts for the GUI #####
    #####                                #####
    ##########################################

    @Part
    def tanks(self):
        return Tanks(range          = self.range,
                     efficiency     = self.efficiency,
                     energy_density = self.energy_density,
                     surface = Wing().area_wing)

    @Part
    def fuselage(self):
        return Fuselage(n_pax           = self.n_pax,
                        width_aisle     = self.width_aisle,
                        width_seat      = self.width_seat,
                        width_armrest   = self.width_armrest,
                        clearance_seat  = self.clearance_seat,
                        length_cockpit  = self.length_cockpit,
                        height_floor    = self.height_floor,
                        height_shoulder = self.height_shoulder,
                        luggage_per_pax = self.luggage_per_pax,
                        weight_cargo    = self.weight_cargo,
                        kcc             = self.kcc,
                        length_tailcone_over_diam     = self.length_tailcone_over_diam,
                        length_nosecone_over_diam     = self.length_nosecone_over_diam,
                        length_tail_over_diam         = self.length_tail_over_diam,
                        fuselage_mass_fraction        = self.fuselage_mass_fraction,
                        empennage_mass_fraction       = self.empennage_mass_fraction,
                        fixed_equipment_mass_fraction = self.fixed_equipment_mass_fraction,
                        fuselage_cg_loc               = self.fuselage_cg_loc,
                        empennage_cg_loc              = self.empennage_cg_loc,
                        fixed_equipment_cg_loc        = self.fixed_equipment_cg_loc)

    @Part
    def main_wing(self):
        return Wing(mach_cruise       = self.mach_cruise,
                    altitude_cruise   = self.altitude_cruise,
                    weight_TO         = self.weight_TO,
                    wing_loading      = self.wing_loading,
                    aspect_ratio      = self.aspect_ratio,
                    wing_highlow      = self.wing_highlow,
                    wing_cg_loc       = self.wing_cg_loc,
                    propulsion_cg_loc = self.propulsion_cg_loc,
                    oew_cg_loc        = self.oew_cg_loc,
                    wing_mass_fraction            =self.wing_mass_fraction,
                    propulsion_mass_fraction      =self.propulsion_mass_fraction,
                    fuselage_mass_fraction        =self.fuselage_mass_fraction,
                    empennage_mass_fraction       =self.empennage_mass_fraction,
                    fixed_equipment_mass_fraction =self.fixed_equipment_mass_fraction)

    @Part
    def vertical_tail(self):
        return Vertical_Tail(volume_vt                   = self.volume_VT,
                             aspect_ratio_vertical       = self.aspect_Ratio_vertical,
                             taper_ratio_vertical        = self.taper_Ratio_vertical,
                             sweep_leading_edge_vertical = self.sweep_leading_edge_vertical,
                             mach_cruise                 = self.mach_cruise,
                             surface_area = Wing().area_wing,
                             span         = Wing().span  )

    @Part
    def horizontal_tail(self):
        return Horizontal_Tail(volume_ht                      = self.volume_HT,
                               aspect_ratio_horizontal        = self.aspect_Ratio_horizontal,
                               taper_ratio_horizontal         = self.taper_Ratio_horizontal,
                               sweep_three_quarter_horizontal = self.sweep_three_quarter_horizontal,
                               mach_cruise                    = self.mach_cruise,
                               surface_area = Wing().area_wing,
                               mac          = Wing().mean_aerodynamic_chord)

    @Part
    def prop_system(self):
        return Propulsion_System(thrust_to          = self.thrust_to,
                                 n_engines          = self.n_engines,
                                 bypass_ratio       = self.bypass_ratio,
                                 turbine_inlet_temp = self.turbine_inlet_temp,
                                 phi                = self.phi)

    @Part
    def cg_range(self):
        return CG_calculations(payload_cg_loc  = self.payload_cg_loc,
                               fuel_cg_loc     = self.fuel_cg_loc,
                               mass_oew        = self.mass_oew,
                               mass_payload    = self.mass_payload,
                               mass_fuel       = self.mass_fuel)

    @Part
    def cg_range_hyd(self):
        return CG_calculations_hyd(payload_cg_loc  = self.payload_cg_loc,
                                   mass_oew_fr     = self.mass_oew,
                                   mass_payload_fr = self.mass_payload)

    @Part
    def newprofile(self):
        return new_fuselage2(input_profile_set = self.new_fuselage_input)

    @Part
    def testprofile(self):
        return new_fuselage1()


if __name__ == '__main__':
    from parapy.gui import display

    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)
