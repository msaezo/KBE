from parapy.core import *

from aircraft import Wing
from aircraft import Fuselage
from aircraft import VerticalTail
from aircraft import HorizontalTail
from aircraft import CGCalculations
from aircraft import CGCalculationsHyd
from aircraft import SeatRow
from aircraft import PropulsionSystem
from aircraft import Q3D
from aircraft import Drag
from aircraft import Energy1
from aircraft import Tanks
from aircraft import NewFuselage1
from aircraft import NewFuselage2
from aircraft import FanEngine
from aircraft import NewFuselageProfile
from parapy.exchange.step import STEPWriter

import os
import xlrd
import warnings
from math import *

DIR = os.path.dirname(__file__)


class AircraftGeometry(Base):
    # This is where we open the input file and parse the values to variables with the same name
    # Name is the name of the variable and Value is simply the value assigned tyo it in the spreadsheet
    # For-loops  for each block in the excel sheet

    workbook = xlrd.open_workbook('aircraft/KBE_Input.xls')
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
    # Empenage parameters
    for i in range(52, 61):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")
    # Flight parameters
    for i in range(63, 68):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Here   we reassign the variable imported from excel to a new name that is PEP8 proof
    n_pax = Input(Number_of_passengers)
    width_aisle = Input(Width_aisle)
    width_seat = Input(Width_seat)
    width_armrest = Input(Width_armrest)
    clearance_seat = Input(Seat_clearance)
    length_cockpit = Input(Length_cockpit)
    length_tailcone_over_diam = Input(Length_tailcone_over_Diameter_Fuselage)
    length_nosecone_over_diam = Input(Length_nosecone_over_Diameter_Fuselage)
    length_tail_over_diam = Input(Length_Tail_over_Diameter_Fuselage)
    height_floor = Input(Height_floor)
    height_shoulder = Input(Height_shoulder)
    luggage_per_pax = Input(Luggage_per_pax)
    weight_cargo = Input(Cargo)
    kcc = Input(Kcc)

    mach_cruise = Input(Mach_cruise)
    altitude_cruise = Input(Altitude_cruise)
    weight_to = Input(Weight_TO)
    wing_loading = Input(Wing_loading)
    aspect_ratio = Input(Aspect_ratio)
    wing_highlow = Input("low")

    n_engines = Input(N_engines)
    thrust_to = Input(Thrust_TO)
    turbine_inlet_temp = Input(Temp_T_4)
    phi = Input(Phi)
    bypass_ratio = Input(BPR)

    wing_mass_fraction = Input(Wing_mass_fraction)
    propulsion_mass_fraction = Input(Propulsion_system_mass_fraction)
    fuselage_mass_fraction = Input(Fuselage_mass_fraction)
    empennage_mass_fraction = Input(Empennage_mass_fraction)
    fixed_equipment_mass_fraction = Input(Fixed_equipment_mass_fraction)
    mass_oew = Input(OEW_mass_fraction)
    mass_payload = Input(Payload_mass_fraction)
    mass_fuel = Input(Fuel_mass_fraction)

    wing_cg_loc = Input(Wing_cg_loc)
    propulsion_cg_loc = Input(Propulsion_system_cg_loc)
    fuselage_cg_loc = Input(Fuselage_cg_loc)
    empennage_cg_loc = Input(Empennage_cg_loc)
    fixed_equipment_cg_loc = Input(Fixed_equipment_cg_loc)
    oew_cg_loc = Input(OEW_cg_loc)
    payload_cg_loc = Input(Payload_cg_loc)
    fuel_cg_loc = Input(Fuel_cg_loc)

    volume_HT = Input(Tail_volume_horizontal)
    volume_VT = Input(Tail_volume_vertical)
    aspect_Ratio_horizontal = Input(aspect_Ratio_horizontal)
    aspect_Ratio_vertical = Input(aspect_Ratio_vertical)
    taper_Ratio_horizontal = Input(taper_Ratio_horizontal)
    taper_Ratio_vertical = Input(taper_Ratio_vertical)
    sweep_three_quarter_horizontal = Input(sweep_three_quarter_horizontal)
    sweep_leading_edge_vertical = Input(sweep_leading_edge_vertical)
    tail_config = Input(configuration)

    range = Input(Range)
    efficiency = Input(total_efficiency)
    energy_density = Input(energy_density)
    hyd_density = Input(hyd_density)
    skinfric_coeff = Input(eq_skinfriction_coefficient)

    # Declaring input warnings if it is out of the recommended bounds
    @Attribute
    def warnings_inputs(self):
        # Mach is recommended to be between 0.7 and 0.92 as that related most to common airliner or transport operation
        # Important as supersonic behaviour is not specifically well modelled in Q3D
        # and too low mach has large impact on design
        if self.mach_cruise < 0.7 or self.mach_cruise > 0.92:
            msg = "The mach number on the Input File might be outside of bounds for typical transport aviation." \
                  "Suggested options:" \
                  "     - Change mach_cruise between the bounds" \
                  "     - 0.70 and 0.92"
            warnings.warn(msg)

        # empirical relation to warn if MTOW and number of pax diverge too much to make sense
        pax_average = 0.0012 * self.weight_to / 9.81 + 86.01
        if self.n_pax <= pax_average * 0.75 or self.n_pax >= pax_average * 1.25:
            msg = "The number of passengers on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change passengers using the following approximation" \
                  "     - n_pax = 0.0012 * MTOW [kg] + 86.01"
            warnings.warn(msg)

        # empirical relation to warn if the wing loading and MTOW diverge too much compared to existing aircraft
        wing_loading_average = 0.0005 * self.weight_to / 9.81 + 547.52
        if self.wing_loading <= wing_loading_average * 0.77 or self.wing_loading >= wing_loading_average * 1.23:
            msg = "The wing loading on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change wing_loading using the following approximation" \
                  "     - wing_loading = 0.0005 * MTOW [kg] + 547.52"
            warnings.warn(msg)

        # Warning if the aspect ratio diverges too much compared to common airliner configurations
        if self.aspect_ratio < 7.73 or self.aspect_ratio > 9.44:
            msg = "The aspect ratio on the Input File might be outside of bounds for the typical transportation" \
                  "aircraft. Suggested options:" \
                  "     - Change to aspect_ratio between the following bounds" \
                  "     - 7.73 to 9.44"
            warnings.warn(msg)

        # empirical relation to warn if the aircraft range and MTOW diverge too much compared to existing aircraft
        range_average = 0.0323 * self.weight_to / 9.81 + 2819.4
        if self.range < range_average * 0.60 or self.range > range_average * 1.40:
            msg = "The range on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change range using the following approximation" \
                  "     - range = 0.0323 * MTOW [kg] + 2819.4"
            warnings.warn(msg)
        finish = 'Look in terminal for warnings'
        return finish

    # Calcuates the cg range of the fossil fuel aircraft
    @Attribute
    def cg_calc(self):
        return CGCalculations(payload_cg_loc=self.Payload_cg_loc,
                              fuel_cg_loc=self.Fuel_cg_loc,
                              mass_oew=self.OEW_mass_fraction,
                              mass_payload=self.Payload_mass_fraction,
                              mass_fuel=self.Fuel_mass_fraction)

    # Calculates the attributes of one turbofan engine
    # Required as the dimensions are required for the placement of the the entire propulsion system
    @Attribute
    def turbofan(self):
        return FanEngine(thrust_to=self.thrust_to,
                         n_engines=self.n_engines,
                         bypass_ratio=self.bypass_ratio,
                         turbine_inlet_temp=self.turbine_inlet_temp,
                         phi=self.phi)

    # Creating the fuselage part from the Fuselage class
    @Part
    def fuselage(self):
        return Fuselage(n_pax=self.n_pax,
                        width_aisle=self.width_aisle,
                        width_seat=self.width_seat,
                        width_armrest=self.width_armrest,
                        clearance_seat=self.clearance_seat,
                        length_cockpit=self.length_cockpit,
                        height_floor=self.height_floor,
                        height_shoulder=self.height_shoulder,
                        luggage_per_pax=self.luggage_per_pax,
                        weight_cargo=self.weight_cargo,
                        kcc=self.kcc,
                        length_tailcone_over_diam=self.length_tailcone_over_diam,
                        length_nosecone_over_diam=self.length_nosecone_over_diam,
                        length_tail_over_diam=self.length_tail_over_diam,
                        fuselage_mass_fraction=self.fuselage_mass_fraction,
                        empennage_mass_fraction=self.empennage_mass_fraction,
                        fixed_equipment_mass_fraction=self.fixed_equipment_mass_fraction,
                        fuselage_cg_loc=self.fuselage_cg_loc,
                        empennage_cg_loc=self.empennage_cg_loc,
                        fixed_equipment_cg_loc=self.fixed_equipment_cg_loc)

    # creating the main wing part from the Wing class
    @Part
    def main_wing(self):
        return Wing(mach_cruise=self.mach_cruise,
                    altitude_cruise=self.altitude_cruise,
                    weight_to=self.weight_to,
                    wing_loading=self.wing_loading,
                    aspect_ratio=self.aspect_ratio,
                    wing_highlow=self.wing_highlow,
                    wing_cg_loc=self.wing_cg_loc,
                    propulsion_cg_loc=self.propulsion_cg_loc,
                    oew_cg_loc=self.oew_cg_loc,
                    wing_mass_fraction=self.wing_mass_fraction,
                    propulsion_mass_fraction=self.propulsion_mass_fraction,
                    fuselage_mass_fraction=self.fuselage_mass_fraction,
                    empennage_mass_fraction=self.empennage_mass_fraction,
                    fixed_equipment_mass_fraction=self.fixed_equipment_mass_fraction,
                    x_fuselage_cg=self.fuselage.x_fuselage_cg,
                    diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer)

    # creating a visual representation of the petrol based cg range using the CGCalculations class
    @Part
    def cg_range(self):
        return CGCalculations(payload_cg_loc=self.payload_cg_loc,
                              fuel_cg_loc=self.fuel_cg_loc,
                              mass_oew=self.mass_oew,
                              mass_payload=self.mass_payload,
                              mass_fuel=self.mass_fuel,
                              mean_aerodynamic_chord=self.main_wing.mean_aerodynamic_chord,
                              x_le_mac=self.main_wing.x_le_mac,
                              length_fuselage=self.fuselage.length_fuselage)

    # Creating the vertical tail part from the VerticalTail class
    @Part
    def vertical_tail(self):
        return VerticalTail(volume_vt=self.volume_VT,
                            aspect_ratio_vertical=self.aspect_Ratio_vertical,
                            taper_ratio_vertical=self.taper_Ratio_vertical,
                            sweep_leading_edge_vertical=self.sweep_leading_edge_vertical,
                            mach_cruise=self.mach_cruise,
                            surface_area=self.main_wing.area_wing,
                            span=self.main_wing.span,
                            lift_coefficient=self.main_wing.lift_coefficient,
                            length_fuselage=self.fuselage.length_fuselage,
                            length_tail=self.fuselage.length_tail,
                            cg_aft=self.cg_range.cg_aft,
                            diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer)

    # Creating the horizontal tail part from the HorizontalTail class, requires VT input for positioning
    @Part
    def horizontal_tail(self):
        return HorizontalTail(volume_ht=self.volume_HT,
                              aspect_ratio_horizontal=self.aspect_Ratio_horizontal,
                              taper_ratio_horizontal=self.taper_Ratio_horizontal,
                              sweep_three_quarter_horizontal=self.sweep_three_quarter_horizontal,
                              mach_cruise=self.mach_cruise,
                              surface_area=self.main_wing.area_wing,
                              mac=self.main_wing.mean_aerodynamic_chord,
                              length_fuselage=self.fuselage.length_fuselage,
                              cg_aft=self.cg_range.cg_aft,
                              diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer,
                              x_tail_vertical=self.vertical_tail.x_tail_vertical,
                              x_tip_vertical=self.vertical_tail.vt_x_shift_tip,
                              z_tip_vertical=self.vertical_tail.vt_z_shift_tip,
                              span_vertical=self.vertical_tail.span_vertical_tail,
                              root_chord_vertical_tail=self.vertical_tail.root_chord_vertical_tail,
                              tail_config=self.tail_config,
                              sweep_vertical=self.vertical_tail.sweep_leading_edge_vertical)

    # Creating the entire propulsion system using the PropulsionSystem class that places several TurboFan instances
    @Part
    def prop_system(self):
        return PropulsionSystem(thrust_to=self.thrust_to,
                                n_engines=self.n_engines,
                                bypass_ratio=self.bypass_ratio,
                                turbine_inlet_temp=self.turbine_inlet_temp,
                                phi=self.phi,
                                span=self.main_wing.span,
                                diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer,
                                wing_z_shift=self.main_wing.wing_z_shift,
                                dihedral=self.main_wing.dihedral,
                                x_tail_vertical=self.vertical_tail.x_tail_vertical,
                                wing_x_shift=self.main_wing.wing_x_shift,
                                sweep_leading_edge=self.main_wing.sweep_leading_edge,
                                max_diameter=self.turbofan.max_diameter)

    # Running Q3D to eventually use the wing drag
    @Attribute
    def q3d(self):
        return Q3D(span=self.main_wing.span,
                   root_chord=self.main_wing.chord_root,
                   tip_chord=self.main_wing.chord_tip,
                   MAC=self.main_wing.mean_aerodynamic_chord,
                   twist_tip=self.main_wing.twist,
                   dihedral=self.main_wing.dihedral,
                   sweep=self.main_wing.sweep_leading_edge,
                   altitude=self.main_wing.altitude_cruise,
                   mach=self.main_wing.mach_cruise,
                   cl=self.main_wing.lift_coefficient,
                   temperature=self.main_wing.temperature,
                   pressure=self.main_wing.pressure_static,
                   sound_speed=self.main_wing.sound_speed,
                   air_speed=self.main_wing.air_speed,
                   air_density=self.main_wing.air_density)

    # Calculating the total drag using the class Drag which combines the wing drag as calculated above
    # and the drag of fuselage, nacelles and empennage
    @Attribute
    def drag(self):
        return Drag(lift_coefficient=self.q3d.cldes,
                    drag_coefficient=self.q3d.cddes,
                    density=self.q3d.air_density,
                    velocity=self.q3d.air_speed,
                    surface=self.main_wing.area_wing,
                    fus_diam=self.fuselage.diameter_fuselage_outer,
                    ht_surface=self.horizontal_tail.surface_horizontal_tail,
                    ht_sweep=self.horizontal_tail.sweep_cuarter_chord_horizontal_tail,
                    vt_surface=self.vertical_tail.surface_vertical_tail,
                    vt_sweep=self.vertical_tail.sweep_cuarter_chord_vertical_tail,
                    len_nacelle=self.turbofan.nacelle_length,
                    cowling_length=self.turbofan.fan_length,
                    cowling_length_1=self.turbofan.loc_max_diameter,
                    cowling_diam=self.turbofan.max_diameter,
                    cowling_fan=self.turbofan.inlet_diameter,
                    cowling_ef=self.turbofan.exit_diameter,
                    gg_length=self.turbofan.length_gas_generator,
                    gg_diam=self.turbofan.diameter_gas_generator,
                    gg_diam_exit=self.turbofan.exit_diameter_gas_generator,
                    span=self.main_wing.span,
                    root_chord=self.main_wing.chord_root,
                    tip_chord=self.main_wing.chord_tip,
                    mac=self.main_wing.mean_aerodynamic_chord,
                    altitude=self.altitude_cruise,
                    mach=self.mach_cruise,
                    mach_critical=self.main_wing.mach_critical,
                    cl=self.main_wing.lift_coefficient,
                    taper_ratio=self.main_wing.taper_ratio,
                    aspect_ratio=self.main_wing.aspect_ratio,
                    sweep=self.main_wing.sweep_quarter_chord,
                    n_engines=self.n_engines)

    # calculates the energy required for the flight and estimates the required tank size
    @Attribute
    def energy(self):
        return Energy1(range=self.range,
                       efficiency=self.efficiency,
                       energy_density=self.energy_density,
                       fus_diam=self.fuselage.diameter_fuselage_inner,
                       length_fuselage=self.fuselage.length_fuselage,
                       length_cockpit=self.fuselage.length_cockpit,
                       length_tailcone=self.fuselage.length_tailcone,
                       position_floor_lower=self.fuselage.position_floor_lower,
                       drag=self.drag.drag_tot)

    # creates the part tanks using the Tanks class which creates and places as many instances of a tank as required
    @Part
    def tanks(self):
        return Tanks(length_cockpit=self.fuselage.length_cockpit,
                     position_floor_lower=self.fuselage.position_floor_lower,
                     diameter_fuselage_inner=self.fuselage.diameter_fuselage_inner,
                     diameter_tank_final=self.energy.diameter_tank_final,
                     number_of_tanks=self.energy.number_of_tanks,
                     length_tank=self.energy.length_tank)

    # calculaes the dimensions and profile of a new fuselage to fit around the positioned tanks
    @Attribute
    def new_profile(self):
        return NewFuselageProfile(fuselage_diameter=self.fuselage.diameter_fuselage_outer,
                                  y_pos=self.tanks.y_pos,
                                  z_pos=self.tanks.z_pos,
                                  diameter_tank_final=self.tanks.diameter_tank_final)

    # creates a new attribute which is another instance of the class Drag but now with an updated fuselage profile
    @Attribute
    def drag_new(self):
        return Drag(lift_coefficient=self.q3d.cldes,
                    drag_coefficient=self.q3d.cddes,
                    density=self.q3d.air_density,
                    velocity=self.q3d.air_speed,
                    surface=self.main_wing.area_wing,
                    fus_diam=self.new_profile.fus_diam_new,
                    ht_surface=self.horizontal_tail.surface_horizontal_tail,
                    ht_sweep=self.horizontal_tail.sweep_cuarter_chord_horizontal_tail,
                    vt_surface=self.vertical_tail.surface_vertical_tail,
                    vt_sweep=self.vertical_tail.sweep_cuarter_chord_vertical_tail,
                    len_nacelle=self.turbofan.nacelle_length,
                    cowling_length=self.turbofan.fan_length,
                    cowling_length_1=self.turbofan.loc_max_diameter,
                    cowling_diam=self.turbofan.max_diameter,
                    cowling_fan=self.turbofan.inlet_diameter,
                    cowling_ef=self.turbofan.exit_diameter,
                    gg_length=self.turbofan.length_gas_generator,
                    gg_diam=self.turbofan.diameter_gas_generator,
                    gg_diam_exit=self.turbofan.exit_diameter_gas_generator,
                    span=self.main_wing.span,
                    root_chord=self.main_wing.chord_root,
                    tip_chord=self.main_wing.chord_tip,
                    mac=self.main_wing.mean_aerodynamic_chord,
                    altitude=self.altitude_cruise,
                    mach=self.mach_cruise,
                    mach_critical=self.main_wing.mach_critical,
                    cl=self.main_wing.lift_coefficient,
                    taper_ratio=self.main_wing.taper_ratio,
                    aspect_ratio=self.main_wing.aspect_ratio,
                    sweep=self.main_wing.sweep_quarter_chord,
                    n_engines=self.n_engines)

    # A couple of outputs of the two drag calculations such that they can be easily compared in the GUI
    # This is the total drag value of the fossil fuel plane
    @Attribute
    def drag_value_old(self):
        return self.drag.drag_tot

    # Total drag value of the LH2 plane
    @Attribute
    def drag_value_new(self):
        return self.drag_new.drag_tot

    # Drag coefficient of the old fuselage
    @Attribute
    def cd_fuselage_old(self):
        return self.drag.drag_coeff_fus

    # Drag coefficient of the newfuselage
    @Attribute
    def cd_fuselage_new(self):
        return self.drag_new.drag_coeff_fus

    # Increase in drag counts between the new and old design
    @Attribute
    def cd_fuselage_new_count_increase(self):
        return (self.drag_new.drag_coeff_fus - self.drag.drag_coeff_fus) * 10000

    # increase in the wave drag due to the new design
    @Attribute
    def wave_drag_increase(self):
        return self.drag_new.wave_drag_coefficient_change

    # The induced drag coefficient
    @Attribute
    def induced_drag_coefficient(self):
        return self.drag_new.induced_drag

    # Total drag coefficient of the old fuselage
    @Attribute
    def cd_old(self):
        return self.drag.drag_coefficient_total

    # Total drag coefficient of the new fuselage
    @Attribute
    def cd_new(self):
        return self.drag_new.drag_coefficient_total

    # Creates a visual representation of the new cg range
    @Part
    def cg_range_hyd(self):
        return CGCalculationsHyd(mtow=self.weight_to,
                                 payload_cg_loc=self.payload_cg_loc,
                                 tank_length=self.energy.length_tank,
                                 tank_front_loc=self.fuselage.length_cockpit,
                                 vol_needed=self.energy.vol_needed,
                                 hyd_density=self.hyd_density,
                                 g_i=0.5,  # gravimetric index taken from report on flying V, cryogenic tank
                                 vol_to_kg_hyd=8 / 120,  # hydrogen conversion from L to kg
                                 mass_oew_fr=self.mass_oew,
                                 mass_payload_fr=self.mass_payload,
                                 max_cg_fuel=self.cg_calc.cg_aft,
                                 min_cg_fuel=self.cg_calc.cg_forward,
                                 x_le_mac=self.main_wing.x_le_mac,
                                 mean_aerodynamic_chord=self.main_wing.mean_aerodynamic_chord,
                                 length_fuselage=self.fuselage.length_fuselage)

    # Calculates the original fuel mass
    @Attribute
    def fuel_mass(self):
        return self.weight_to * self.mass_fuel

    # Calculates the new MTOW by substracting the old fuel mass and adding the LH2+tanks mass
    @Attribute
    def new_mtow(self):
        return self.weight_to - self.fuel_mass + (
                self.energy.vol_needed * 1000 * self.cg_range_hyd.vol_to_kg_hyd * 9.81)

    # Creates a set of fuselage profiles for each section along its length depending on the tank size
    @Attribute
    def new_fuselage_1(self):
        return NewFuselage1(diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer,
                            section_length_outer=self.fuselage.section_length_outer,
                            length_fuselage=self.fuselage.length_fuselage,
                            diameter_tank_final=self.energy.diameter_tank_final,
                            y_pos=self.tanks.y_pos,
                            z_pos=self.tanks.z_pos)

    # Modifies the input for creating the new fuselage depending on if the tanks fit in the old fuselage or not
    @Attribute
    def new_fuselage_input(self):
        if self.tanks.tank_max_dim > self.fuselage.diameter_fuselage_inner / 2:
            aaa = [self.fuselage.outer_profile_set[0],
                   self.fuselage.outer_profile_set[1],
                   self.new_fuselage_1.new_profile_first.composed_crv,
                   self.new_fuselage_1.new_profile_set[0].composed_crv,
                   self.new_fuselage_1.new_profile_set[1].composed_crv,
                   self.new_fuselage_1.new_profile_set[2].composed_crv,
                   self.new_fuselage_1.new_profile_set[3].composed_crv,
                   self.new_fuselage_1.new_profile_set[4].composed_crv,
                   self.fuselage.outer_profile_set[8],
                   self.fuselage.outer_profile_set[9],
                   self.fuselage.outer_profile_set[10]]
        else:
            aaa = [self.fuselage.outer_profile_set[0],
                   self.fuselage.outer_profile_set[1],
                   self.fuselage.outer_profile_set[2],
                   self.fuselage.outer_profile_set[3],
                   self.fuselage.outer_profile_set[4],
                   self.fuselage.outer_profile_set[5],
                   self.fuselage.outer_profile_set[6],
                   self.fuselage.outer_profile_set[7],
                   self.fuselage.outer_profile_set[8],
                   self.fuselage.outer_profile_set[9],
                   self.fuselage.outer_profile_set[10]]
        return aaa

    # Physically creates the new fuselage as a part
    @Part
    def new_fuselage(self):
        return NewFuselage2(input_profile_set=self.new_fuselage_input)

    # Physically shows the new fuselage profiles (not important but adds for visualisation in the GUI)
    @Part
    def new_fuselage_profiles(self):
        return NewFuselage1(diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer,
                            section_length_outer=self.fuselage.section_length_outer,
                            length_fuselage=self.fuselage.length_fuselage,
                            diameter_tank_final=self.energy.diameter_tank_final,
                            y_pos=self.tanks.y_pos,
                            z_pos=self.tanks.z_pos)

    # Generates a list of tree elements relating to the tanks that we want to convert to STEP files
    @Attribute
    def tanks_step(self):
        tanks_stp = []
        for i in range(0, int(self.energy.number_of_tanks)):
            tanks_stp = tanks_stp + [self.tanks.tank[i].tank]
        return tanks_stp

    # Generates a list of tree elements relating to the seats and seat rows that we want to convert to STEP files
    @Attribute
    def seats_step(self):
        seats_stp = []
        for i in range(0, int(self.fuselage.n_rows_front)):
            for j in range(0, int(self.fuselage.seats_abreast - 2)):
                seats_stp = seats_stp + [self.fuselage.seats_front[i].seat_row[j].seat]
        for i in range(0, int(self.fuselage.n_rows_middle)):
            for j in range(0, int(self.fuselage.seats_abreast)):
                seats_stp = seats_stp + [self.fuselage.seats_middle[i].seat_row[j].seat]
        for i in range(0, int(self.fuselage.n_rows_rear)):
            for j in range(0, int(self.fuselage.seats_abreast - 2)):
                seats_stp = seats_stp + [self.fuselage.seats_rear[i].seat_row[j].seat]
        return seats_stp

    # Generates a list of tree elements relating to the engines that we want to convert to STEP files
    @Attribute
    def engines_step(self):
        engines_stp = []
        for i in range(0, int(self.prop_system.n_engines)):
            engines_stp = engines_stp + [self.prop_system.propulsion_system[i].spinner,
                                         self.prop_system.propulsion_system[i].fan,
                                         self.prop_system.propulsion_system[i].core,
                                         self.prop_system.propulsion_system[i].nozzle,
                                         self.prop_system.propulsion_system[i].bypass]
        return engines_stp

    # Generates a list of tree elements relating to the fuselage that we want to convert to STEP files
    @Attribute
    def fuse_wing_empen_step(self):
        fuse_wing_empenage = [self.fuselage.fuselage_subtracted,
                              self.fuselage.floor_cut,
                              self.fuselage.ceiling_cut,
                              self.main_wing.right_wing_surface.right_wing_surface,
                              self.main_wing.left_wing_surface.right_wing_surface,
                              self.vertical_tail.vertical_tail.right_wing_surface,
                              self.horizontal_tail.right_wing_surface_ht.right_wing_surface,
                              self.horizontal_tail.left_wing_surface_ht.right_wing_surface,
                              self.cg_range.cg_front,
                              self.cg_range.cg_rear,
                              self.cg_range_hyd.cg_front,
                              self.cg_range_hyd.cg_rear,
                              self.new_fuselage.fuselage_lofted_solid_outer]
        return fuse_wing_empenage

    # Generates a total list of tree elements that we want to convert to STEP files
    @Attribute
    def assem_step(self):
        engines = self.engines_step
        fuselage = self.fuse_wing_empen_step
        tanks = self.tanks_step
        seats = self.seats_step
        return engines + fuselage + tanks + seats

    # @Part
    # def step_writer_seats(self):
    #     return STEPWriter(default_directory=DIR,
    #                       nodes=self.seats_step)
    #
    # @Part
    # def step_writer_engines(self):
    #     return STEPWriter(default_directory=DIR,
    #                       nodes=self.engines_step)
    #
    # @Part
    # def step_writer_fuselage_wing_empennage(self):
    #     return STEPWriter(default_directory=DIR,
    #                       nodes=self.fuse_wing_empen)
    #
    # @Part
    # def step_writer_tanks(self):
    #     return STEPWriter(default_directory=DIR,
    #                       nodes=self.tanks_step)

    # Generates a step files writer of the final product
    @Part
    def step_writer_assem(self):
        return STEPWriter(default_directory=DIR,
                          label='Aircraft_STEP',
                          nodes=self.assem_step,
                          filename="Aircraft_STEP.stp")

    # Creating Input.txt file with all the inputs of this case
    f = open("input.txt", "w+")
    f.write("User inputs \n\n")

    f.write("n_pax = " + str(Number_of_passengers) + "[-] \n")
    f.write("width_aisle = " + str(Width_aisle) + "[m] \n")
    f.write("width_seat = " + str(Width_seat) + "[m] \n")
    f.write("width_armrest = " + str(Width_armrest) + "[m] \n")
    f.write("clearance_seat = " + str(Seat_clearance) + "[-] \n")
    f.write("length_cockpit = " + str(Length_cockpit) + "[m] \n")
    f.write("length_tailcone_over_diam = " + str(Length_tailcone_over_Diameter_Fuselage) + "[-] \n")
    f.write("length_nosecone_over_diam = " + str(Length_nosecone_over_Diameter_Fuselage) + "[-] \n")
    f.write("length_tail_over_diam = " + str(Length_Tail_over_Diameter_Fuselage) + "[-] \n")
    f.write("height_floor = " + str(Height_floor) + "[m] \n")
    f.write("height_shoulder = " + str(Height_shoulder) + "[m] \n")
    f.write("luggage_per_pax = " + str(Luggage_per_pax) + "[kg] \n")
    f.write("weight_cargo = " + str(Cargo) + "[kg] \n")
    f.write("kcc = " + str(Kcc) + "[-] \n")

    f.write("mach_cruise = " + str(Mach_cruise) + "[-] \n")
    f.write("altitude_cruise = " + str(Altitude_cruise) + "[m] \n")
    f.write("weight_to = " + str(Weight_TO) + "[N] \n")
    f.write("wing_loading = " + str(Wing_loading) + "[kg/m^2] \n")
    f.write("aspect_ratio = " + str(Aspect_ratio) + "[-] \n")

    f.write("n_engines = " + str(N_engines) + "[-] \n")
    f.write("thrust_to = " + str(Thrust_TO) + "[MN] \n")
    f.write("turbine_inlet_temp = " + str(Temp_T_4) + "[K] \n")
    f.write("phi = " + str(Phi) + "[-] \n")
    f.write("bypass_ratio = " + str(BPR) + "[-] \n")

    f.write("wing_mass_fraction = " + str(Wing_mass_fraction) + "[-] \n")
    f.write("propulsion_mass_fraction = " + str(Propulsion_system_mass_fraction) + "[-] \n")
    f.write("fuselage_mass_fraction = " + str(Fuselage_mass_fraction) + "[-] \n")
    f.write("empennage_mass_fraction = " + str(Empennage_mass_fraction) + "[-] \n")
    f.write("fixed_equipment_mass_fraction = " + str(Fixed_equipment_mass_fraction) + "[-] \n")
    f.write("mass_oew_fraction = " + str(OEW_mass_fraction) + "[-] \n")
    f.write("mass_payload_fraction = " + str(Payload_mass_fraction) + "[-] \n")
    f.write("mass_fuel_fraction = " + str(Fuel_mass_fraction) + "[-] \n")

    f.write("wing_cg_loc = " + str(Wing_cg_loc) + "[-] \n")
    f.write("propulsion_cg_loc = " + str(Propulsion_system_cg_loc) + "[-] \n")
    f.write("fuselage_cg_loc = " + str(Fuselage_cg_loc) + "[-] \n")
    f.write("empennage_cg_loc = " + str(Empennage_cg_loc) + "[-] \n")
    f.write("fixed_equipment_cg_loc = " + str(Fixed_equipment_cg_loc) + "[-] \n")
    f.write("oew_cg_loc = " + str(OEW_cg_loc) + "[-] \n")
    f.write("payload_cg_loc = " + str(Payload_cg_loc) + "[-] \n")
    f.write("fuel_cg_loc = " + str(Fuel_cg_loc) + "[-] \n")

    f.write("volume_HT = " + str(Tail_volume_horizontal) + "[m^3] \n")
    f.write("volume_VT = " + str(Tail_volume_vertical) + "[m^3] \n")
    f.close()

    # Creating Output.txt file with all the attributes
    f = open("output.txt", "w+")
    f.write("Outputs Fuselage class \n\n")

    f.write("seats_abreast = " + str(Fuselage().seats_abreast) + "[-] \n")
    f.write("n_aisles = " + str(Fuselage().n_aisles) + "[-] \n")
    f.write("n_rows = " + str(Fuselage().n_rows) + "[-] \n")
    f.write("length_cabin = " + str(Fuselage().length_cabin) + "[m] \n")
    f.write("diameter_fuselage_inner = " + str(Fuselage().diameter_fuselage_inner) + "[m] \n")
    f.write("diameter_fuselage_outer = " + str(Fuselage().diameter_fuselage_outer) + "[m] \n")
    f.write("length_tailcone = " + str(Fuselage().length_tailcone) + "[m] \n")
    f.write("length_nosecone = " + str(Fuselage().length_nosecone) + "[m] \n")
    f.write("length_tail = " + str(Fuselage().length_tail) + "[m] \n")
    f.write("length_fuselage = " + str(Fuselage().length_fuselage) + "[m]  \n")
    f.write("thickness_fuselage = " + str(Fuselage().thickness_fuselage) + "[m]  \n")
    f.write("position_floor_upper = " + str(Fuselage().position_floor_upper) + "[m]  \n")
    f.write("position_floor_lower = " + str(Fuselage().position_floor_lower) + "[m]  \n")
    f.write("section_radius_outer = " + str(Fuselage().section_radius_outer) + "[m]  \n")
    f.write("section_radius_inner = " + str(Fuselage().section_radius_inner) + "[m]  \n")
    f.write("section_length_outer = " + str(Fuselage().section_length_outer) + "[m]  \n")
    f.write("section_length_inner = " + str(Fuselage().section_length_inner) + "[m]  \n")
    f.write("x_fuselage_cg = " + str(Fuselage().x_fuselage_cg) + "[m]  \n\n")

    f.write("Outputs SeatRow class \n\n")
    f.write("seat_spacing = " + str(SeatRow().seat_spacing) + "[m]  \n")
    f.write("row_width = " + str(SeatRow().row_width) + "[m]  \n\n")

    f.write("Outputs Horizontal_tail class \n\n")
    f.write("x_tail_horizontal = " + str(HorizontalTail().x_tail_horizontal) + "[m]  \n")
    f.write("cg_arm_horizontal = " + str(HorizontalTail().cg_arm_horizontal) + "[m]  \n")
    f.write("surface_horizontal_tail = " + str(HorizontalTail().surface_horizontal_tail) + "[m^2]  \n")
    f.write("span_horizontal_tail = " + str(HorizontalTail().span_horizontal_tail) + "[m]  \n")
    f.write("root_chord_horizontal_tail = " + str(HorizontalTail().root_chord_horizontal_tail) + "[m]  \n")
    f.write("tip_chord_horizontal_tail = " + str(HorizontalTail().tip_chord_horizontal_tail) + "[m]  \n")
    f.write("sweep_leading_edge_horizontal_tail = " + str(
        HorizontalTail().sweep_leading_edge_horizontal_tail) + "[deg] \n")
    f.write(
        "sweep_cuarter_chord_horizontal_tail = " + str(
            HorizontalTail().sweep_cuarter_chord_horizontal_tail) + "[deg] \n")
    f.write("sweep_mid_chord_horizontal_tail = " + str(HorizontalTail().sweep_mid_chord_horizontal_tail) + "[deg] \n")
    f.write("ht_x_shift = " + str(HorizontalTail().ht_x_shift) + "[m]  \n")
    f.write("ht_z_shift = " + str(HorizontalTail().ht_z_shift) + "[m]  \n")
    f.write("mach_drag_divergence = " + str(HorizontalTail().mach_drag_divergence) + "[-] \n")
    f.write("thickness_to_chord = " + str(HorizontalTail().thickness_to_chord) + "[-] \n\n")

    f.write("Outputs Vertical_tail class \n\n")
    f.write("x_tail_vertical = " + str(VerticalTail().x_tail_vertical) + "[m]  \n")
    f.write("cg_arm_vertical = " + str(VerticalTail().cg_arm_vertical) + "[m]  \n")
    f.write("surface_vertical_tail = " + str(VerticalTail().surface_vertical_tail) + "[m^2]  \n")
    f.write("span_vertical_tail = " + str(VerticalTail().span_vertical_tail) + "[m]  \n")
    f.write("root_chord_vertical_tail = " + str(VerticalTail().root_chord_vertical_tail) + "[m]  \n")
    f.write("tip_chord_vertical_tail = " + str(VerticalTail().tip_chord_vertical_tail) + "[m]  \n")
    f.write("vt_x_shift = " + str(VerticalTail().vt_x_shift) + "[m]  \n")
    f.write("vt_z_shift = " + str(VerticalTail().vt_z_shift) + "[m]  \n")
    f.write("sweep_mid_chord_vertical_tail = " + str(VerticalTail().sweep_mid_chord_vertical_tail) + "[deg] \n")
    f.write(
        "sweep_cuarter_chord_vertical_tail = " + str(VerticalTail().sweep_cuarter_chord_vertical_tail) + "[deg] \n")
    f.write("mach_drag_divergence = " + str(VerticalTail().mach_drag_divergence) + "[-] \n")
    f.write("thickness_to_chord = " + str(VerticalTail().thickness_to_chord) + "[-] \n\n")

    f.write("Outputs Wing class \n\n")
    f.write("area_wing = " + str(Wing().area_wing) + "[m^2]  \n")
    f.write("temperature = " + str(Wing().temperature) + "[K] \n")
    f.write("pressure_static = " + str(Wing().pressure_static) + "[Pa] \n")
    f.write("sound_speed = " + str(Wing().sound_speed) + "[m/s] \n")
    f.write("air_speed = " + str(Wing().air_speed) + "[m/s] \n")
    f.write("airDensity = " + str(Wing().air_density) + "[kg/m^3] \n")
    f.write("dynamic_pressure = " + str(Wing().dynamic_pressure) + "[Pa] \n")
    f.write("mach_drag_divergence = " + str(Wing().mach_drag_divergence) + "[-] \n")
    f.write("sweep_quarter_chord = " + str(Wing().sweep_quarter_chord) + "[deg] \n")
    f.write("span = " + str(Wing().span) + "[m] \n")
    f.write("taper_ratio = " + str(Wing().taper_ratio) + "[-] \n")
    f.write("chord_root = " + str(Wing().chord_root) + "[m]  \n")
    f.write("chord_tip = " + str(Wing().chord_tip) + "[m]  \n")
    f.write("sweep_leading_edge = " + str(Wing().sweep_leading_edge) + "[deg] \n")
    f.write("mean_aerodynamic_chord = " + str(Wing().mean_aerodynamic_chord) + "[m]  \n")
    f.write("y_mean_aerodynamic_chord = " + str(Wing().y_mean_aerodynamic_chord) + "[m]  \n")
    f.write("lift_coefficient = " + str(Wing().lift_coefficient) + "[-] \n")
    f.write("dihedral = " + str(Wing().dihedral) + "[deg] \n")
    f.write("x_wing_cg = " + str(Wing().x_wing_cg) + "[m]  \n")
    f.write("x_le_mac = " + str(Wing().x_le_mac) + "[m]  \n")
    f.write("wing_x_shift = " + str(Wing().wing_x_shift) + "[m]  \n")
    f.write("wing_z_shift = " + str(Wing().wing_z_shift) + "[m]  \n\n")

    f.write("Outputs Tanks class \n\n")
    f.write("y_pos = " + str(Tanks().y_pos) + "[m]  \n")
    f.write("z_pos = " + str(Tanks().z_pos) + "[m]  \n")
    f.write("tank_max_dim = " + str(Tanks().tank_max_dim) + "[m]  \n\n")

    f.write("Outputs Drag class \n\n")
    f.write("wet_area_fus = " + str(Drag().wet_area_fus) + "[m^2] \n")
    f.write("wet_area_ht = " + str(Drag().wet_area_ht) + "[m^2]  \n")
    f.write("wet_area_vt = " + str(Drag().wet_area_vt) + "[m^2]  \n")
    f.write("wet_area_nacelle = " + str(Drag().wet_area_nacelle) + "[m^2]  \n")
    f.write("wet_area_total = " + str(Drag().wet_area_total) + "[m^2]  \n")
    f.write("skin_friction = " + str(Drag().skin_friction) + "[-] \n")
    f.write("form_factor_ht = " + str(Drag().form_factor_ht) + "[-] \n")
    f.write("form_factor_vt = " + str(Drag().form_factor_vt) + "[-] \n")
    f.write("form_factor_fus = " + str(Drag().form_factor_fus) + "[-] \n")
    f.write("form_factor_nacelle = " + str(Drag().form_factor_nacelle) + "[-] \n")
    f.write("drag_coeff_fus = " + str(Drag().drag_coeff_fus) + "[-] \n")
    f.write("drag_coeff_ht = " + str(Drag().drag_coeff_ht) + "[-] \n")
    f.write("drag_coeff_vt = " + str(Drag().drag_coeff_vt) + "[-] \n")
    f.write("drag_coeff_nacelle = " + str(Drag().drag_coeff_nacelle) + "[-] \n")
    f.write("drag_coeff_wing = " + str(Drag().drag_coeff_wing) + "[-] \n")
    f.write("drag_coefficient_total = " + str(Drag().drag_coefficient_total) + "[-] \n")
    f.write("drag = " + str(Drag().drag_tot) + "[-] \n\n")

    f.write("Outputs Energy class \n\n")
    f.write("work = " + str(Energy1().work) + "[J] \n")
    f.write("energy_req = " + str(Energy1().energy_req) + "[J] \n")
    f.write("vol_needed = " + str(Energy1().vol_needed) + "[m^3] \n")
    f.write("length_tank = " + str(Energy1().length_tank) + "[m] \n")
    f.write("diameter_tank = " + str(Energy1().diameter_tank) + "[m] \n")
    f.write("number_of_tanks = " + str(Energy1().number_of_tanks) + "[-] \n")
    f.write("diameter_tank_final = " + str(Energy1().diameter_tank_final) + "[m] \n\n")

    f.write("Outputs Q3D class \n\n")
    f.write("cldes = " + str(Q3D().cldes) + "[-] \n")
    f.write("cddes = " + str(Q3D().cddes) + "[-] \n")
    f.write("alpha = " + str(Q3D().alpha) + "[deg] \n\n")

    f.write("Outputs CG_calculations class \n\n")
    f.write("x_oew = " + str(CGCalculations().x_oew) + "[m] \n")
    f.write("x_payload = " + str(CGCalculations().x_payload) + "[m] \n")
    f.write("x_fuel = " + str(CGCalculations().x_fuel) + "[m] \n")
    f.write("cg_forward = " + str(CGCalculations().cg_forward) + "[m] \n")
    f.write("cg_aft = " + str(CGCalculations().cg_aft) + "[m] \n\n")

    f.write("Outputs CGCalculations_hyd class \n\n")
    f.write("mtom = " + str(CGCalculationsHyd().mtom) + "[kg] \n")
    f.write("mass_oew = " + str(CGCalculationsHyd().mass_oew) + "[kg-] \n")
    f.write("mass_payload = " + str(CGCalculationsHyd().mass_payload) + "[kg] \n")
    f.write("x_fuel = " + str(CGCalculationsHyd().x_fuel) + "[m] \n")
    f.write("tank_cg_loc = " + str(CGCalculationsHyd().tank_cg_loc) + "[m] \n")
    f.write("mass_fuel = " + str(CGCalculationsHyd().mass_fuel) + "[kg] \n")
    f.write("mass_tank = " + str(CGCalculationsHyd().mass_tank) + "[kg] \n")
    f.write("x_oew = " + str(CGCalculationsHyd().x_oew) + "[m] \n")
    f.write("x_payload = " + str(CGCalculationsHyd().x_payload) + "[m] \n")
    f.write("cg_forward = " + str(CGCalculationsHyd().cg_forward) + "[m] \n")
    f.write("cg_aft = " + str(CGCalculationsHyd().cg_aft) + "[m] \n\n")

    f.write("Outputs Propulsion_System class \n\n")
    f.write("y_pos = " + str(PropulsionSystem().y_pos) + "[m] \n")
    f.write("z_pos = " + str(PropulsionSystem().z_pos) + "[m] \n")
    f.write("x_pos = " + str(PropulsionSystem().x_pos) + "[m] \n\n")

    f.write("Outputs Fan_engine class \n\n")
    f.write("massflow = " + str(FanEngine().massflow) + "[kg/s] \n")
    f.write("ratio_inlet_to_spinner = " + str(FanEngine().ratio_inlet_to_spinner) + "[-] \n")
    f.write("inlet_diameter = " + str(FanEngine().inlet_diameter) + "[m] \n")
    f.write("nacelle_length = " + str(FanEngine().nacelle_length) + "[m] \n")
    f.write("fan_length = " + str(FanEngine().fan_length) + "[m] \n")
    f.write("loc_max_diameter = " + str(FanEngine().loc_max_diameter) + "[m] \n")
    f.write("max_diameter = " + str(FanEngine().max_diameter) + "[m] \n")
    f.write("exit_diameter = " + str(FanEngine().exit_diameter) + "[m] \n")
    f.write("length_gas_generator = " + str(FanEngine().length_gas_generator) + "[m] \n")
    f.write("diameter_gas_generator = " + str(FanEngine().diameter_gas_generator) + "[m] \n")
    f.write("exit_diameter_gas_generator = " + str(FanEngine().exit_diameter_gas_generator) + "[m] \n\n")

    f.write("Outputs New_Fuselage_Profile class \n\n")
    f.write("delta_radius = " + str(NewFuselageProfile().delta_radius) + "[m] \n")
    f.write("straight_length_midpoints = " + str(NewFuselageProfile().straight_length_midpoints) + "[m] \n")
    f.write("straight_length_outer = " + str(NewFuselageProfile().straight_length_outer) + "[m] \n")
    f.write("angle_1 = " + str(NewFuselageProfile().angle_1) + "[rad] \n")
    f.write("angle_2 = " + str(NewFuselageProfile().angle_2) + "[rad] \n")
    f.write("y_lower = " + str(NewFuselageProfile().y_lower) + "[m] \n")
    f.write("y_upper = " + str(NewFuselageProfile().y_upper) + "[m] \n")
    f.write("z_lower = " + str(NewFuselageProfile().z_lower) + "[m] \n")
    f.write("z_upper = " + str(NewFuselageProfile().z_upper) + "[m] \n")
    f.close()


# Creates the GUI
if __name__ == '__main__':
    from parapy.gui import display

    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)

# Modifies all the STEP files in the working directory to be sized in metres rather than millimeters.
# Required because our code works with SI units and metre as a standard whereas parapy assumes every
# dimension to be in mm which is the standard in most CAD software packages

# and no, the optional input 'UNIT' for the STEPWriter does not change anything,
# it only converts the 'standard' unit of the .stp file but not the actual size.
# So rather it would convert a length of 1000mm to 1m rather than to 1000m, that is why this operation is needed
# It only comes into action after closing the GUI as the user can have created multiple .stp files whilst using it

# Works by the following procedure:
# 1) finding all files that end with .stp,
# 2) storing all their content in variable 'data'
# 3) replacing every mention of mm to m in the variable 'data'
# 4) overwriting the original file by parsing 'data' back into it
# Also creates print statements to indicate how many step files were found and corrected
location = os.getcwd()
for file in os.listdir(location):
    if file.endswith(".stp"):
        print(".stp file found:\t", file)
        f = open(file, "rt")
        data = f.read()
        data = data.replace('SI_UNIT(.MILLI.,.METRE.)', 'SI_UNIT(.METRE.)')
        f.close()
        f = open(file, "wt")
        f.write(data)
        f.close()
    else:
        print("This was not a .stp file")

print()
print('The found .stp files have been altered to metres')
print()
