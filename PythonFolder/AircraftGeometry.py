from parapy.core import *
from parapy.geom import *

from aircraft import Wing
from aircraft import Fuselage
from aircraft import VerticalTail
from aircraft import HorizontalTail
from aircraft import CGCalculations
from aircraft import CGCalculationsHyd

from aircraft import PropulsionSystem
from aircraft import Q3D
from aircraft import Drag
from aircraft import Energy1
from aircraft import Energy2
from aircraft import Tanks
from aircraft import NewFuselage1
from aircraft import NewFuselage2
from aircraft import SeatRow
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
    for i in range(57, 66):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Flight parameters
    for i in range(68, 73):
        Name = worksheet.cell(i, 1).value
        Value = worksheet.cell(i, 2).value
        exec(Name + "=Value")

    # Inputting the variables to parapy with the proper naming convention

    # imported parameters from input file
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

    # Declaring input warnings if it is out of recommended bounds

    @Attribute
    def warnings_inputs(self):

        if self.mach_cruise < 0.75 or self.mach_cruise > 0.92:
            msg = "The mach number on the Input File might be outside of bounds for typical transport aviation." \
                  "Suggested options:" \
                  "     - Change mach_cruise between the bounds" \
                  "     - 0.75 and 0.92"
            warnings.warn(msg)

        pax_average = 0.0012 * self.weight_to / 9.81 + 86.01
        if self.n_pax <= pax_average * 0.75 or self.n_pax >= pax_average * 1.25:
            msg = "The number of passengers on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change passengers using the following approximation" \
                  "     - n_pax = 0.0012 * MTOW [kg] + 86.01"
            warnings.warn(msg)

        wing_loading_average = 0.0005 * self.weight_to / 9.81 + 547.52
        if self.wing_loading <= wing_loading_average * 0.77 or self.wing_loading >= wing_loading_average * 1.23:
            msg = "The wing loading on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change wing_loading using the following approximation" \
                  "     - wing_loading = 0.0005 * MTOW [kg] + 547.52"
            warnings.warn(msg)

        if self.aspect_ratio < 7.73 or self.aspect_ratio > 9.44:
            msg = "The aspect ratio on the Input File might be outside of bounds for the typical transportation" \
                  "aircraft. Suggested options:" \
                  "     - Change to aspect_ratio between the following bounds" \
                  "     - 7.73 to 9.44"
            warnings.warn(msg)

        span = sqrt(self.aspect_ratio * self.weight_to / 9.81 / self.wing_loading)
        if span >= 80 or span <= 22:
            msg = "The wing span resulting from the Input File might be outside of bounds for the typical " \
                  "transportation aircraft. Suggested options:" \
                  "     - Change the aspect ratio between the bounds" \
                  "     - Change the wing loading"
            warnings.warn(msg)

        range_average = 0.0323 * self.weight_to / 9.81 + 2819.4
        if self.range < range_average * 0.60 or self.range > range_average * 1.40:
            msg = "The range on the Input File might be outside of bounds for the selected MTOW " \
                  "Suggested options:" \
                  "     - Change range using the following approximation" \
                  "     - range = 0.0323 * MTOW [kg] + 2819.4"
            warnings.warn(msg)
        finish = 'Look in terminal for warnings'
        return finish

    # Some attributes to easily check in parapy GUI

    # @Attribute
    # def volume_needed(self):
    #     return Energy().vol_needed
    #
    # @Attribute
    # def cl_in(self):
    #     return Wing().lift_coefficient
    #
    # @Attribute
    # def cl_out(self):
    #     return Q3D().cldes
    #
    # @Attribute
    # def cd_out(self):
    #     return Q3D().cddes
    #
    # @Attribute
    # def alpha(self):
    #     return Q3D().alpha
    #
    # @Attribute
    # def reynolds(self):
    #     return Q3D().reynolds
    #
    # @Attribute
    # def cd_total(self):
    #     return Drag().drag_coefficient_total
    #
    # @Attribute
    # def drag_total(self):
    #     return Drag().drag

    @Attribute
    def cg_calc(self):
        return CGCalculations(payload_cg_loc=self.Payload_cg_loc,
                              fuel_cg_loc=self.Fuel_cg_loc,
                              mass_oew=self.OEW_mass_fraction,
                              mass_payload=self.Payload_mass_fraction,
                              mass_fuel=self.Fuel_mass_fraction)

    @Attribute
    def turbofan(self):
        return FanEngine(thrust_to=self.thrust_to,
                         n_engines=self.n_engines,
                         bypass_ratio=self.bypass_ratio,
                         turbine_inlet_temp=self.turbine_inlet_temp,
                         phi=self.phi)

    # Creating the parts for the GUI

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
                   cl=self.main_wing.lift_coefficient)

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
                    cl=self.main_wing.lift_coefficient,
                    n_engines=self.n_engines)



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

    @Part
    def tanks(self):
        return Tanks(  # range=self.range,
                     # efficiency=self.efficiency,
                     # energy_density=self.energy_density,
                     # fus_diam=self.fuselage.diameter_fuselage_outer,
                     # length_fuselage=self.fuselage.length_fuselage,
                     length_cockpit=self.fuselage.length_cockpit,
                     # length_tailcone=self.fuselage.length_tailcone,
                     position_floor_lower=self.fuselage.position_floor_lower,
                     diameter_fuselage_inner=self.fuselage.diameter_fuselage_inner,
                     # drag=self.drag.drag_tot,
                     diameter_tank_final=self.energy.diameter_tank_final,
                     number_of_tanks=self.energy.number_of_tanks,
                     length_tank=self.energy.length_tank)

    @Attribute
    def new_profile(self):
        return NewFuselageProfile(fuselage_diameter=self.fuselage.diameter_fuselage_outer,
                                  y_pos=self.tanks.y_pos,
                                  z_pos=self.tanks.z_pos,
                                  diameter_tank_final=self.tanks.diameter_tank_final)

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
                    cl=self.main_wing.lift_coefficient,
                    n_engines=self.n_engines)

    @Attribute
    def drag_value_old(self):
        return self.drag.drag_tot

    @Attribute
    def drag_value_new(self):
        return self.drag_new.drag_tot

    @Attribute
    def cd_fuselage_old(self):
        return self.drag.drag_coeff_fus

    @Attribute
    def cd_fuselage_new(self):
        return self.drag_new.drag_coeff_fus

    @Attribute
    def cd_fuselage_new_count_increase(self):
        return (self.drag_new.drag_coeff_fus - self.drag.drag_coeff_fus)*10000

    @Attribute
    def cd_old(self):
        return self.drag.drag_coefficient_total

    @Attribute
    def cd_new(self):
        return self.drag_new.drag_coefficient_total

    @Part
    def cg_range_hyd(self):
        return CGCalculationsHyd(mtow=self.weight_to,
                                 payload_cg_loc=self.payload_cg_loc,
                                 tank_length=self.energy.length_tank,
                                 tank_front_loc=self.fuselage.length_cockpit,
                                 vol_needed=self.energy.vol_needed,
                                 hyd_density=self.hyd_density,
                                 g_i=0.5,  # gravimetric index taken from report on flying V, cryogenic tank
                                 vol_to_kg_hyd=8/120, #hydrogen conversion from L to kg
                                 mass_oew_fr=self.mass_oew,
                                 mass_payload_fr=self.mass_payload,
                                 max_cg_fuel=self.cg_calc.cg_aft,
                                 min_cg_fuel=self.cg_calc.cg_forward,
                                 x_le_mac=self.main_wing.x_le_mac,
                                 mean_aerodynamic_chord=self.main_wing.mean_aerodynamic_chord,
                                 length_fuselage=self.fuselage.length_fuselage)

        # Variable input for new fuselage depending on tank size
        # if tanks dont fit inside fuselage use new profiles that do fit
        # else reuse old profiles and recreate fuselage as is
    @Attribute
    def fuel_mass(self):
        return self.weight_to * self.mass_fuel

    @Attribute
    def new_MTOW(self):
        return (self.weight_to - self.fuel_mass) + (self.cg_range_hyd.g_i * self.cg_range_hyd.vol_needed *
                                                  self.cg_range_hyd.vol_to_kg_hyd)

    @Attribute
    def new_fuselage_1(self):
        return NewFuselage1(diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer,
                            section_length_outer=self.fuselage.section_length_outer,
                            length_fuselage=self.fuselage.length_fuselage,
                            diameter_tank_final=self.energy.diameter_tank_final,
                            y_pos=self.tanks.y_pos,
                            z_pos=self.tanks.z_pos)

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

    @Part
    def new_fuselage(self):
        return NewFuselage2(input_profile_set=self.new_fuselage_input)

    @Part
    def new_fuselage_profiles(self):
        return NewFuselage1(diameter_fuselage_outer=self.fuselage.diameter_fuselage_outer,
                            section_length_outer=self.fuselage.section_length_outer,
                            length_fuselage=self.fuselage.length_fuselage,
                            diameter_tank_final=self.energy.diameter_tank_final,
                            y_pos=self.tanks.y_pos,
                            z_pos=self.tanks.z_pos)

    @Attribute
    def tanks_step(self):
        if self.energy.number_of_tanks == 1:
            tanks_stp = [self.tanks.tank[0].tank]
        elif self.energy.number_of_tanks == 2:
            tanks_stp = [self.tanks.tank[0].tank,
                         self.tanks.tank[1].tank]
        elif self.energy.number_of_tanks == 3:
            tanks_stp = [self.tanks.tank[0].tank,
                         self.tanks.tank[1].tank,
                         self.tanks.tank[2].tank]
        elif self.energy.number_of_tanks == 4:
            tanks_stp = [self.tanks.tank[0].tank,
                         self.tanks.tank[1].tank,
                         self.tanks.tank[2].tank,
                         self.tanks.tank[3].tank]
        else:
            tanks_stp = [self.tanks.tank[0].tank,
                         self.tanks.tank[1].tank]
        return tanks_stp

    @Attribute
    def engines_step(self):
        if self.prop_system.n_engines == 1:
            engines_stp = [self.prop_system.propulsion_system[0].spinner,
                           self.prop_system.propulsion_system[0].fan,
                           self.prop_system.propulsion_system[0].core,
                           self.prop_system.propulsion_system[0].nozzle,
                           self.prop_system.propulsion_system[0].bypass]
        elif self.prop_system.n_engines == 2:
            engines_stp = [self.prop_system.propulsion_system[0].spinner,
                           self.prop_system.propulsion_system[0].fan,
                           self.prop_system.propulsion_system[0].core,
                           self.prop_system.propulsion_system[0].nozzle,
                           self.prop_system.propulsion_system[0].bypass,
                           self.prop_system.propulsion_system[1].spinner,
                           self.prop_system.propulsion_system[1].fan,
                           self.prop_system.propulsion_system[1].core,
                           self.prop_system.propulsion_system[1].nozzle,
                           self.prop_system.propulsion_system[1].bypass]
        elif self.prop_system.n_engines == 3:
            engines_stp = [self.prop_system.propulsion_system[0].spinner,
                           self.prop_system.propulsion_system[0].fan,
                           self.prop_system.propulsion_system[0].core,
                           self.prop_system.propulsion_system[0].nozzle,
                           self.prop_system.propulsion_system[0].bypass,
                           self.prop_system.propulsion_system[1].spinner,
                           self.prop_system.propulsion_system[1].fan,
                           self.prop_system.propulsion_system[1].core,
                           self.prop_system.propulsion_system[1].nozzle,
                           self.prop_system.propulsion_system[1].bypass,
                           self.prop_system.propulsion_system[2].spinner,
                           self.prop_system.propulsion_system[2].fan,
                           self.prop_system.propulsion_system[2].core,
                           self.prop_system.propulsion_system[2].nozzle,
                           self.prop_system.propulsion_system[2].bypass]
        elif self.prop_system.n_engines == 4:
            engines_stp = [self.prop_system.propulsion_system[0].spinner,
                           self.prop_system.propulsion_system[0].fan,
                           self.prop_system.propulsion_system[0].core,
                           self.prop_system.propulsion_system[0].nozzle,
                           self.prop_system.propulsion_system[0].bypass,
                           self.prop_system.propulsion_system[1].spinner,
                           self.prop_system.propulsion_system[1].fan,
                           self.prop_system.propulsion_system[1].core,
                           self.prop_system.propulsion_system[1].nozzle,
                           self.prop_system.propulsion_system[1].bypass,
                           self.prop_system.propulsion_system[2].spinner,
                           self.prop_system.propulsion_system[2].fan,
                           self.prop_system.propulsion_system[2].core,
                           self.prop_system.propulsion_system[2].nozzle,
                           self.prop_system.propulsion_system[2].bypass,
                           self.prop_system.propulsion_system[3].spinner,
                           self.prop_system.propulsion_system[3].fan,
                           self.prop_system.propulsion_system[3].core,
                           self.prop_system.propulsion_system[3].nozzle,
                           self.prop_system.propulsion_system[3].bypass]
        return engines_stp

    @Part
    def step_writer_tanks(self):
        return STEPWriter(default_directory=DIR,
                          nodes=self.tanks_step)

    @Part
    def step_writer_engines(self):
        return STEPWriter(default_directory=DIR,
                          nodes=self.engines_step)

    @Part
    def step_writer_fuselage_wing_empennage(self):
        return STEPWriter(default_directory=DIR,
                          nodes=[self.fuselage.fuselage_subtracted,
                                 self.fuselage.floor_cut,
                                 self.fuselage.ceiling_cut,
                                 self.main_wing.right_wing_surface,
                                 self.main_wing.left_wing_surface,
                                 self.vertical_tail.vertical_wing_surface,
                                 self.horizontal_tail.right_wing_surface_ht,
                                 self.horizontal_tail.left_wing_surface_ht,
                                 self.cg_range.cg_front,
                                 self.cg_range.cg_rear,
                                 self.cg_range_hyd.cg_front,
                                 self.cg_range_hyd.cg_rear,
                                 self.newprofile.fuselage_lofted_solid_outer])

    # Creating Output.txt file

    # f = open("output.txt", "w+")
    # f.write("Outputs Fuselage class \n\n")
    #
    # f.write("seats_abreast = " + str(Fuselage().seats_abreast) + "\n")
    # f.write("n_aisles width = " + str(Fuselage().n_aisles) + "\n")
    # f.write("n_rows = " + str(Fuselage().n_rows) + "\n")
    # f.write("length_cabin = " + str(Fuselage().length_cabin) + "\n")
    # f.write("diameter_fuselage_inner = " + str(Fuselage().diameter_fuselage_inner) + "\n")
    # f.write("diameter_fuselage_outer = " + str(Fuselage().diameter_fuselage_outer) + "\n")
    # f.write("length_tailcone = " + str(Fuselage().length_tailcone) + "\n")
    # f.write("length_nosecone = " + str(Fuselage().length_nosecone) + "\n")
    # f.write("length_tail = " + str(Fuselage().length_tail) + "\n")
    # f.write("length_fuselage = " + str(Fuselage().length_fuselage) + "\n")
    # f.write("thickness_fuselage = " + str(Fuselage().thickness_fuselage) + "\n")
    # f.write("position_floor_upper = " + str(Fuselage().position_floor_upper) + "\n")
    # f.write("position_floor_lower = " + str(Fuselage().position_floor_lower) + "\n")
    # f.write("section_radius_outer = " + str(Fuselage().section_radius_outer) + "\n")
    # f.write("section_radius_inner = " + str(Fuselage().section_radius_inner) + "\n")
    # f.write("section_length_outer = " + str(Fuselage().section_length_outer) + "\n")
    # f.write("section_length_inner = " + str(Fuselage().section_length_inner) + "\n")
    # f.write("x_fuselage_cg = " + str(Fuselage().x_fuselage_cg) + "\n\n")
    #
    # f.write("Outputs Seat_row class \n\n")
    # f.write("seat_spacing = " + str(Seat_row().seat_spacing) + "\n")
    # f.write("row_width = " + str(Seat_row().row_width) + "\n\n")
    #
    # f.write("Outputs Horizontal_tail class \n\n")
    # f.write("x_tail_horizontal = " + str(Horizontal_Tail().x_tail_horizontal) + "\n")
    # f.write("cg_arm_horizontal = " + str(Horizontal_Tail().cg_arm_horizontal) + "\n")
    # f.write("surface_horizontal_tail = " + str(Horizontal_Tail().surface_horizontal_tail) + "\n")
    # f.write("span_horizontal_tail = " + str(Horizontal_Tail().span_horizontal_tail) + "\n")
    # f.write("root_chord_horizontal_tail = " + str(Horizontal_Tail().root_chord_horizontal_tail) + "\n")
    # f.write("tip_chord_horizontal_tail = " + str(Horizontal_Tail().tip_chord_horizontal_tail) + "\n")
    # f.write("sweep_leading_edge_horizontal_tail = " +str(Horizontal_Tail().sweep_leading_edge_horizontal_tail) + "\n")
    # f.write(
    #     "sweep_cuarter_chord_horizontal_tail = " + str(Horizontal_Tail().sweep_cuarter_chord_horizontal_tail) + "\n")
    # f.write("sweep_mid_chord_horizontal_tail = " + str(Horizontal_Tail().sweep_mid_chord_horizontal_tail) + "\n")
    # f.write("ht_x_shift = " + str(Horizontal_Tail().ht_x_shift) + "\n")
    # f.write("ht_z_shift = " + str(Horizontal_Tail().ht_z_shift) + "\n")
    # f.write("mach_drag_divergence = " + str(Horizontal_Tail().mach_drag_divergence) + "\n")
    # f.write("thickness_to_chord = " + str(Horizontal_Tail().thickness_to_chord) + "\n\n")
    #
    # f.write("Outputs Vertical_tail class \n\n")
    # f.write("x_tail_vertical = " + str(Vertical_Tail().x_tail_vertical) + "\n")
    # f.write("cg_arm_vertical = " + str(Vertical_Tail().cg_arm_vertical) + "\n")
    # f.write("surface_vertical_tail = " + str(Vertical_Tail().surface_vertical_tail) + "\n")
    # f.write("span_vertical_tail = " + str(Vertical_Tail().span_vertical_tail) + "\n")
    # f.write("root_chord_vertical_tail = " + str(Vertical_Tail().root_chord_vertical_tail) + "\n")
    # f.write("tip_chord_vertical_tail = " + str(Vertical_Tail().tip_chord_vertical_tail) + "\n")
    # f.write("vt_x_shift = " + str(Vertical_Tail().vt_x_shift) + "\n")
    # f.write("vt_z_shift = " + str(Vertical_Tail().vt_z_shift) + "\n")
    # f.write("sweep_mid_chord_vertical_tail = " + str(Vertical_Tail().sweep_mid_chord_vertical_tail) + "\n")
    # f.write("sweep_cuarter_chord_vertical_tail = " + str(Vertical_Tail().sweep_cuarter_chord_vertical_tail) + "\n")
    # f.write("mach_drag_divergence = " + str(Vertical_Tail().mach_drag_divergence) + "\n")
    # f.write("thickness_to_chord = " + str(Vertical_Tail().thickness_to_chord) + "\n\n")
    #
    # f.write("Outputs Wing class \n\n")
    # f.write("area_wing = " + str(Wing().area_wing) + "\n")
    # f.write("temperature = " + str(Wing().temperature) + "\n")
    # f.write("pressure_static = " + str(Wing().pressure_static) + "\n")
    # f.write("sound_speed = " + str(Wing().sound_speed) + "\n")
    # f.write("air_speed = " + str(Wing().air_speed) + "\n")
    # f.write("airDensity = " + str(Wing().airDensity) + "\n")
    # f.write("dynamic_pressure = " + str(Wing().dynamic_pressure) + "\n")
    # f.write("mach_drag_divergence = " + str(Wing().mach_drag_divergence) + "\n")
    # f.write("sweep_quarter_chord = " + str(Wing().sweep_quarter_chord) + "\n")
    # f.write("span = " + str(Wing().span) + "\n")
    # f.write("taper_ratio = " + str(Wing().taper_ratio) + "\n")
    # f.write("chord_root = " + str(Wing().chord_root) + "\n")
    # f.write("chord_tip = " + str(Wing().chord_tip) + "\n")
    # f.write("sweep_leading_edge = " + str(Wing().sweep_leading_edge) + "\n")
    # f.write("sweep_mid_chord = " + str(Wing().sweep_mid_chord) + "\n")
    # f.write("mean_aerodynamic_chord = " + str(Wing().mean_aerodynamic_chord) + "\n")
    # f.write("y_mean_aerodynamic_chord = " + str(Wing().y_mean_aerodynamic_chord) + "\n")
    # f.write("lift_coefficient = " + str(Wing().lift_coefficient) + "\n")
    # f.write("dihedral = " + str(Wing().dihedral) + "\n")
    # f.write("x_wing_cg = " + str(Wing().x_wing_cg) + "\n")
    # f.write("x_le_mac = " + str(Wing().x_le_mac) + "\n")
    # f.write("wing_x_shift = " + str(Wing().wing_x_shift) + "\n")
    # f.write("wing_z_shift = " + str(Wing().wing_z_shift) + "\n\n")
    #
    # f.write("Outputs Tanks class \n\n")
    # f.write("y_pos = " + str(Tanks().y_pos) + "\n")
    # f.write("z_pos = " + str(Tanks().z_pos) + "\n")
    # f.write("tank_max_dim = " + str(Tanks().tank_max_dim) + "\n")
    # f.write("new_fuselage = " + str(Tanks().new_fuselage) + "\n\n")
    #
    # f.write("Outputs Drag class \n\n")
    # f.write("wet_area_fus = " + str(Drag().wet_area_fus) + "\n")
    # f.write("wet_area_ht = " + str(Drag().wet_area_ht) + "\n")
    # f.write("wet_area_vt = " + str(Drag().wet_area_vt) + "\n")
    # f.write("wet_area_nacelle = " + str(Drag().wet_area_nacelle) + "\n")
    # f.write("wet_area_total = " + str(Drag().wet_area_total) + "\n")
    # f.write("skin_friction = " + str(Drag().skin_friction) + "\n")
    # f.write("form_factor_ht = " + str(Drag().form_factor_ht) + "\n")
    # f.write("form_factor_vt = " + str(Drag().form_factor_vt) + "\n")
    # f.write("form_factor_fus = " + str(Drag().form_factor_fus) + "\n")
    # f.write("form_factor_nacelle = " + str(Drag().form_factor_nacelle) + "\n")
    # f.write("drag_coeff_fus = " + str(Drag().drag_coeff_fus) + "\n")
    # f.write("drag_coeff_ht = " + str(Drag().drag_coeff_ht) + "\n")
    # f.write("drag_coeff_vt = " + str(Drag().drag_coeff_vt) + "\n")
    # f.write("drag_coeff_nacelle = " + str(Drag().drag_coeff_nacelle) + "\n")
    # f.write("drag_coeff_wing = " + str(Drag().drag_coeff_wing) + "\n")
    # f.write("drag_coefficient_total = " + str(Drag().drag_coefficient_total) + "\n")
    # f.write("drag = " + str(Drag().drag) + "\n\n")
    #
    # f.write("Outputs Energy class \n\n")
    # f.write("work = " + str(Energy().work) + "\n")
    # f.write("energy_req = " + str(Energy().energy_req) + "\n")
    # f.write("vol_needed = " + str(Energy().vol_needed) + "\n")
    # f.write("length_tank = " + str(Energy().length_tank) + "\n")
    # f.write("diameter_tank = " + str(Energy().diameter_tank) + "\n")
    # f.write("number_of_tanks = " + str(Energy().number_of_tanks) + "\n")
    # f.write("diameter_tank_final = " + str(Energy().diameter_tank_final) + "\n\n")
    #
    # f.write("Outputs Q3D class \n\n")
    # f.write("q_three_d = " + str(Q3D().q_three_d) + "\n")
    # f.write("cldes = " + str(Q3D().cldes) + "\n")
    # f.write("cddes = " + str(Q3D().cddes) + "\n")
    # f.write("alpha = " + str(Q3D().alpha) + "\n\n")
    #
    # f.write("Outputs CG_calculations class \n\n")
    # f.write("x_oew = " + str(CG_calculations().x_oew) + "\n")
    # f.write("x_payload = " + str(CG_calculations().x_payload) + "\n")
    # f.write("x_fuel = " + str(CG_calculations().x_fuel) + "\n")
    # f.write("cg_forward = " + str(CG_calculations().cg_forward) + "\n")
    # f.write("cg_aft = " + str(CG_calculations().cg_aft) + "\n\n")
    #
    # f.write("Outputs CG_calculations_hyd class \n\n")
    # f.write("mtom = " + str(CG_calculations_hyd().mtom) + "\n")
    # f.write("mass_oew = " + str(CG_calculations_hyd().mass_oew) + "\n")
    # f.write("mass_payload = " + str(CG_calculations_hyd().mass_payload) + "\n")
    # f.write("x_fuel = " + str(CG_calculations_hyd().x_fuel) + "\n")
    # f.write("tank_cg_loc = " + str(CG_calculations_hyd().tank_cg_loc) + "\n")
    # f.write("mass_fuel = " + str(CG_calculations_hyd().mass_fuel) + "\n")
    # f.write("mass_tank = " + str(CG_calculations_hyd().mass_tank) + "\n")
    # f.write("x_oew = " + str(CG_calculations_hyd().x_oew) + "\n")
    # f.write("x_payload = " + str(CG_calculations_hyd().x_payload) + "\n")
    # f.write("cg_forward = " + str(CG_calculations_hyd().cg_forward) + "\n")
    # f.write("cg_aft = " + str(CG_calculations_hyd().cg_aft) + "\n\n")
    #
    # f.write("Outputs Propulsion_System class \n\n")
    # f.write("y_pos = " + str(Propulsion_System().y_pos) + "\n")
    # f.write("z_pos = " + str(Propulsion_System().z_pos) + "\n")
    # f.write("x_pos = " + str(Propulsion_System().x_pos) + "\n\n")
    #
    # f.write("Outputs Fan_engine class \n\n")
    # f.write("massflow = " + str(Fan_engine().massflow) + "\n")
    # f.write("ratio_inlet_to_spinner = " + str(Fan_engine().ratio_inlet_to_spinner) + "\n")
    # f.write("inlet_diameter = " + str(Fan_engine().inlet_diameter) + "\n")
    # f.write("nacelle_length = " + str(Fan_engine().nacelle_length) + "\n")
    # f.write("fan_length = " + str(Fan_engine().fan_length) + "\n")
    # f.write("loc_max_diameter = " + str(Fan_engine().loc_max_diameter) + "\n")
    # f.write("max_diameter = " + str(Fan_engine().max_diameter) + "\n")
    # f.write("exit_diameter = " + str(Fan_engine().exit_diameter) + "\n")
    # f.write("length_gas_generator = " + str(Fan_engine().length_gas_generator) + "\n")
    # f.write("diameter_gas_generator = " + str(Fan_engine().diameter_gas_generator) + "\n")
    # f.write("exit_diameter_gas_generator = " + str(Fan_engine().exit_diameter_gas_generator) + "\n\n")
    #
    # f.write("Outputs New_Fuselage_Profile class \n\n")
    # f.write("delta_radius = " + str(New_Fuselage_Profile().delta_radius) + "\n")
    # f.write("straight_length_midpoints = " + str(New_Fuselage_Profile().straight_length_midpoints) + "\n")
    # f.write("straight_length_outer = " + str(New_Fuselage_Profile().straight_length_outer) + "\n")
    # f.write("angle_1 = " + str(New_Fuselage_Profile().angle_1) + "\n")
    # f.write("angle_2 = " + str(New_Fuselage_Profile().angle_2) + "\n")
    # f.write("y_lower = " + str(New_Fuselage_Profile().y_lower) + "\n")
    # f.write("y_upper = " + str(New_Fuselage_Profile().y_upper) + "\n")
    # f.write("z_lower = " + str(New_Fuselage_Profile().z_lower) + "\n")
    # f.write("z_upper = " + str(New_Fuselage_Profile().z_upper) + "\n")
    # f.close()


if __name__ == '__main__':
    from parapy.gui import display

    obj1 = AircraftGeometry(label="totalgeometry")
    display(obj1)
