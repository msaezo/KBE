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
#   - C.G.Range Hydrogen > C.G. Range Kerosene   -- Just give warning
#       - WARNING: - Problems might arise due to higher C.G. range than before -
#   - Any other?

# Some other doubts I have at the moment, or improvements for future.
#   - Include the drag of the fuselage, theoretically we could extend it and drag would not increase (good that tank is limited by the fus length)
#   - Fuel weight defined twice? once in fuel mass fraction (guessing kerosene) twice range (guessing hydrogen)
#   - Cargo not included at all
from parapy.core import *
from parapy.geom import *

from AircraftGeometry import AircraftGeometry
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
from aircraft import Seat_row
from aircraft import Fan_engine
from aircraft import New_Fuselage_Profile



AircraftGeometry()

f= open("00_input.txt","w+")
f.write("Inputs \n\n")
f.write("n_pax = " + str(AircraftGeometry().n_pax) + "\n")
f.write("aisle width = " + str(AircraftGeometry().width_aisle) + "\n")
f.write("width_seat = " + str(AircraftGeometry().width_seat ) + "\n")
f.write("width_armrest = " + str(AircraftGeometry().width_armrest ) + "\n")
f.write("clearance_seat = " + str(AircraftGeometry().clearance_seat ) + "\n")
f.write("length_cockpit = " + str(AircraftGeometry().length_cockpit ) + "\n")
f.write("length_tailcone_over_diam = " + str(AircraftGeometry().length_tailcone_over_diam ) + "\n")
f.write("length_nosecone_over_diam = " + str(AircraftGeometry().length_nosecone_over_diam ) + "\n")
f.write("length_tail_over_diam = " + str(AircraftGeometry().length_tail_over_diam ) + "\n")
f.write("height_floor = " + str(AircraftGeometry().height_floor ) + "\n")
f.write("height_shoulder = " + str(AircraftGeometry().height_shoulder ) + "\n")
f.write("luggage_per_pax = " + str(AircraftGeometry().luggage_per_pax ) + "\n")
f.write("weight_cargo = " + str(AircraftGeometry().weight_cargo ) + "\n")
f.write("kcc = " + str(AircraftGeometry().kcc ) + "\n")

f.write("mach_cruise = " + str(AircraftGeometry().mach_cruise ) + "\n")
f.write("altitude_cruise = " + str(AircraftGeometry().altitude_cruise ) + "\n")
f.write("weight_to = " + str(AircraftGeometry().weight_to) + "\n")
f.write("wing_loading = " + str(AircraftGeometry().wing_loading ) + "\n")
f.write("aspect_ratio = " + str(AircraftGeometry().aspect_ratio ) + "\n")
f.write("wing_highlow = " + str(AircraftGeometry().wing_highlow ) + "\n")

f.write("n_engines = " + str(AircraftGeometry().n_engines ) + "\n")
f.write("thrust_to = " + str(AircraftGeometry().thrust_to ) + "\n")
f.write("turbine_inlet_temp = " + str(AircraftGeometry().turbine_inlet_temp) + "\n")
f.write("phi = " + str(AircraftGeometry().phi ) + "\n")
f.write("bypass_ratio = " + str(AircraftGeometry().bypass_ratio ) + "\n")

f.write("wing_mass_fraction = " + str(AircraftGeometry().wing_mass_fraction ) + "\n")
f.write("propulsion_mass_fraction = " + str(AircraftGeometry().propulsion_mass_fraction ) + "\n")
f.write("fuselage_mass_fraction = " + str(AircraftGeometry().fuselage_mass_fraction) + "\n")
f.write("empennage_mass_fraction = " + str(AircraftGeometry().empennage_mass_fraction ) + "\n")
f.write("fixed_equipment_mass_fraction = " + str(AircraftGeometry().fixed_equipment_mass_fraction ) + "\n")
f.write("mass_oew = " + str(AircraftGeometry().mass_oew ) + "\n")
f.write("mass_payload = " + str(AircraftGeometry().mass_payload ) + "\n")
f.write("mass_fuel = " + str(AircraftGeometry().mass_fuel ) + "\n")

f.write("wing_cg_loc = " + str(AircraftGeometry().wing_cg_loc) + "\n")
f.write("propulsion_cg_loc = " + str(AircraftGeometry().propulsion_cg_loc) + "\n")
f.write("fuselage_cg_loc = " + str(AircraftGeometry().fuselage_cg_loc ) + "\n")
f.write("empennage_cg_loc = " + str(AircraftGeometry().empennage_cg_loc ) + "\n")
f.write("fixed_equipment_cg_loc = " + str(AircraftGeometry().fixed_equipment_cg_loc ) + "\n")
f.write("payload_cg_loc = " + str(AircraftGeometry().payload_cg_loc ) + "\n")
f.write("fuel_cg_loc = " + str(AircraftGeometry().fuel_cg_loc ) + "\n")

f.write("volume_HT = " + str(AircraftGeometry().volume_HT ) + "\n")
f.write("volume_VT = " + str(AircraftGeometry().volume_VT ) + "\n")
f.write("aspect_Ratio_horizontal = " + str(AircraftGeometry().aspect_Ratio_horizontal) + "\n")
f.write("aspect_Ratio_vertical = " + str(AircraftGeometry().aspect_Ratio_vertical ) + "\n")
f.write("taper_Ratio_horizontal = " + str(AircraftGeometry().taper_Ratio_horizontal ) + "\n")
f.write("taper_Ratio_vertical = " + str(AircraftGeometry().taper_Ratio_vertical ) + "\n")
f.write("sweep_three_quarter_horizontal = " + str(AircraftGeometry().sweep_three_quarter_horizontal) + "\n")
f.write("sweep_leading_edge_vertical = " + str(AircraftGeometry().sweep_leading_edge_vertical ) + "\n")

f.write("range = " + str(AircraftGeometry().range ) + "\n")
f.write("efficiency = " + str(AircraftGeometry().efficiency ) + "\n")
f.write("energy_density = " + str(AircraftGeometry().energy_density ) + "\n")
f.write("hyd_density = " + str(AircraftGeometry().hyd_density ) + "\n")
f.write("skinfric_coeff = " + str(AircraftGeometry().skinfric_coeff ) + "\n")
f.close()

f= open("00_output.txt","w+")
f.write("Outputs Fuselage class \n\n")

f.write("seats_abreast = " + str(Fuselage().seats_abreast) + "\n")
f.write("n_aisles width = " + str(Fuselage().n_aisles) + "\n")
f.write("n_rows = " + str(Fuselage().n_rows ) + "\n")
f.write("length_cabin = " + str(Fuselage().length_cabin ) + "\n")
f.write("diameter_fuselage_inner = " + str(Fuselage().diameter_fuselage_inner ) + "\n")
f.write("diameter_fuselage_outer = " + str(Fuselage().diameter_fuselage_outer ) + "\n")
f.write("length_tailcone = " + str(Fuselage().length_tailcone ) + "\n")
f.write("length_nosecone = " + str(Fuselage().length_nosecone ) + "\n")
f.write("length_tail = " + str(Fuselage().length_tail ) + "\n")
f.write("length_fuselage = " + str(Fuselage().length_fuselage ) + "\n")
f.write("thickness_fuselage = " + str(Fuselage().thickness_fuselage ) + "\n")
f.write("position_floor_upper = " + str(Fuselage().position_floor_upper ) + "\n")
f.write("position_floor_lower = " + str(Fuselage().position_floor_lower ) + "\n")
f.write("section_radius_outer = " + str(Fuselage().section_radius_outer ) + "\n")
f.write("section_radius_inner = " + str(Fuselage().section_radius_inner ) + "\n")
f.write("section_length_outer = " + str(Fuselage().section_length_outer ) + "\n")
f.write("section_length_inner = " + str(Fuselage().section_length_inner ) + "\n")
f.write("x_fuselage_cg = " + str(Fuselage().x_fuselage_cg ) + "\n\n")

f.write("Outputs Seat_row class \n\n")
f.write("seat_spacing = " + str(Seat_row().seat_spacing ) + "\n")
f.write("row_width = " + str(Seat_row().row_width ) + "\n\n")

f.write("Outputs Horizontal_tail class \n\n")
f.write("x_tail_horizontal = " + str(Horizontal_Tail().x_tail_horizontal ) + "\n")
f.write("cg_arm_horizontal = " + str(Horizontal_Tail().cg_arm_horizontal ) + "\n")
f.write("surface_horizontal_tail = " + str(Horizontal_Tail().surface_horizontal_tail ) + "\n")
f.write("span_horizontal_tail = " + str(Horizontal_Tail().span_horizontal_tail ) + "\n")
f.write("root_chord_horizontal_tail = " + str(Horizontal_Tail().root_chord_horizontal_tail ) + "\n")
f.write("tip_chord_horizontal_tail = " + str(Horizontal_Tail().tip_chord_horizontal_tail ) + "\n")
f.write("sweep_leading_edge_horizontal_tail = " + str(Horizontal_Tail().sweep_leading_edge_horizontal_tail ) + "\n")
f.write("sweep_cuarter_chord_horizontal_tail = " + str(Horizontal_Tail().sweep_cuarter_chord_horizontal_tail ) + "\n")
f.write("sweep_mid_chord_horizontal_tail = " + str(Horizontal_Tail().sweep_mid_chord_horizontal_tail ) + "\n")
f.write("ht_x_shift = " + str(Horizontal_Tail().ht_x_shift ) + "\n")
f.write("ht_z_shift = " + str(Horizontal_Tail().ht_z_shift ) + "\n")
f.write("mach_drag_divergence = " + str(Horizontal_Tail().mach_drag_divergence ) + "\n")
f.write("thickness_to_chord = " + str(Horizontal_Tail().thickness_to_chord ) + "\n\n")

f.write("Outputs Vertical_tail class \n\n")
f.write("x_tail_vertical = " + str(Vertical_Tail().x_tail_vertical ) + "\n")
f.write("cg_arm_vertical = " + str(Vertical_Tail().cg_arm_vertical ) + "\n")
f.write("surface_vertical_tail = " + str(Vertical_Tail().surface_vertical_tail ) + "\n")
f.write("span_vertical_tail = " + str(Vertical_Tail().span_vertical_tail ) + "\n")
f.write("root_chord_vertical_tail = " + str(Vertical_Tail().root_chord_vertical_tail ) + "\n")
f.write("tip_chord_vertical_tail = " + str(Vertical_Tail().tip_chord_vertical_tail ) + "\n")
f.write("vt_x_shift = " + str(Vertical_Tail().vt_x_shift ) + "\n")
f.write("vt_z_shift = " + str(Vertical_Tail().vt_z_shift ) + "\n")
f.write("sweep_mid_chord_vertical_tail = " + str(Vertical_Tail().sweep_mid_chord_vertical_tail ) + "\n")
f.write("sweep_cuarter_chord_vertical_tail = " + str(Vertical_Tail().sweep_cuarter_chord_vertical_tail ) + "\n")
f.write("mach_drag_divergence = " + str(Vertical_Tail().mach_drag_divergence ) + "\n")
f.write("thickness_to_chord = " + str(Vertical_Tail().thickness_to_chord ) + "\n\n")

f.write("Outputs Wing class \n\n")
f.write("area_wing = " + str(Wing().area_wing ) + "\n")
f.write("temperature = " + str(Wing().temperature ) + "\n")
f.write("pressure_static = " + str(Wing().pressure_static ) + "\n")
f.write("sound_speed = " + str(Wing().sound_speed ) + "\n")
f.write("air_speed = " + str(Wing().air_speed ) + "\n")
f.write("airDensity = " + str(Wing().airDensity ) + "\n")
f.write("dynamic_pressure = " + str(Wing().dynamic_pressure ) + "\n")
f.write("mach_drag_divergence = " + str(Wing().mach_drag_divergence ) + "\n")
f.write("sweep_quarter_chord = " + str(Wing().sweep_quarter_chord ) + "\n")
f.write("span = " + str(Wing().span ) + "\n")
f.write("taper_ratio = " + str(Wing().taper_ratio ) + "\n")
f.write("chord_root = " + str(Wing().chord_root ) + "\n")
f.write("chord_tip = " + str(Wing().chord_tip ) + "\n")
f.write("sweep_leading_edge = " + str(Wing().sweep_leading_edge ) + "\n")
f.write("sweep_mid_chord = " + str(Wing().sweep_mid_chord ) + "\n")
f.write("mean_aerodynamic_chord = " + str(Wing().mean_aerodynamic_chord ) + "\n")
f.write("y_mean_aerodynamic_chord = " + str(Wing().y_mean_aerodynamic_chord ) + "\n")
f.write("lift_coefficient = " + str(Wing().lift_coefficient ) + "\n")
f.write("dihedral = " + str(Wing().dihedral ) + "\n")
f.write("x_wing_cg = " + str(Wing().x_wing_cg ) + "\n")
f.write("x_le_mac = " + str(Wing().x_le_mac ) + "\n")
f.write("wing_x_shift = " + str(Wing().wing_x_shift ) + "\n")
f.write("wing_z_shift = " + str(Wing().wing_z_shift ) + "\n\n")

f.write("Outputs Tanks class \n\n")
f.write("y_pos = " + str(Tanks().y_pos ) + "\n")
f.write("z_pos = " + str(Tanks().z_pos ) + "\n")
f.write("tank_max_dim = " + str(Tanks().tank_max_dim ) + "\n")
f.write("new_fuselage = " + str(Tanks().new_fuselage ) + "\n\n")

f.write("Outputs Drag class \n\n")
f.write("wet_area_fus = " + str(Drag().wet_area_fus ) + "\n")
f.write("wet_area_ht = " + str(Drag().wet_area_ht ) + "\n")
f.write("wet_area_vt = " + str(Drag().wet_area_vt ) + "\n")
f.write("wet_area_nacelle = " + str(Drag().wet_area_nacelle ) + "\n")
f.write("wet_area_total = " + str(Drag().wet_area_total ) + "\n")
f.write("skin_friction = " + str(Drag().skin_friction ) + "\n")
f.write("form_factor_ht = " + str(Drag().form_factor_ht ) + "\n")
f.write("form_factor_vt = " + str(Drag().form_factor_vt ) + "\n")
f.write("form_factor_fus = " + str(Drag().form_factor_fus ) + "\n")
f.write("form_factor_nacelle = " + str(Drag().form_factor_nacelle ) + "\n")
f.write("drag_coeff_fus = " + str(Drag().drag_coeff_fus ) + "\n")
f.write("drag_coeff_ht = " + str(Drag().drag_coeff_ht ) + "\n")
f.write("drag_coeff_vt = " + str(Drag().drag_coeff_vt ) + "\n")
f.write("drag_coeff_nacelle = " + str(Drag().drag_coeff_nacelle ) + "\n")
f.write("drag_coeff_wing = " + str(Drag().drag_coeff_wing ) + "\n")
f.write("drag_coefficient_total = " + str(Drag().drag_coefficient_total ) + "\n")
f.write("drag = " + str(Drag().drag ) + "\n\n")

f.write("Outputs Energy class \n\n")
f.write("work = " + str(Energy().work ) + "\n")
f.write("energy_req = " + str(Energy().energy_req ) + "\n")
f.write("vol_needed = " + str(Energy().vol_needed ) + "\n")
f.write("length_tank = " + str(Energy().length_tank ) + "\n")
f.write("diameter_tank = " + str(Energy().diameter_tank ) + "\n")
f.write("number_of_tanks = " + str(Energy().number_of_tanks ) + "\n")
f.write("diameter_tank_final = " + str(Energy().diameter_tank_final ) + "\n\n")

f.write("Outputs Q3D class \n\n")
f.write("q_three_d = " + str(Q3D().q_three_d ) + "\n")
f.write("cldes = " + str(Q3D().cldes ) + "\n")
f.write("cddes = " + str(Q3D().cddes ) + "\n")
f.write("alpha = " + str(Q3D().alpha ) + "\n\n")

f.write("Outputs CG_calculations class \n\n")
f.write("x_oew = " + str(CG_calculations().x_oew ) + "\n")
f.write("x_payload = " + str(CG_calculations().x_payload ) + "\n")
f.write("x_fuel = " + str(CG_calculations().x_fuel ) + "\n")
f.write("cg_forward = " + str(CG_calculations().cg_forward ) + "\n")
f.write("cg_aft = " + str(CG_calculations().cg_aft ) + "\n\n")

f.write("Outputs CG_calculations_hyd class \n\n")
f.write("mtom = " + str(CG_calculations_hyd().mtom ) + "\n")
f.write("mass_oew = " + str(CG_calculations_hyd().mass_oew ) + "\n")
f.write("mass_payload = " + str(CG_calculations_hyd().mass_payload ) + "\n")
f.write("x_fuel = " + str(CG_calculations_hyd().x_fuel ) + "\n")
f.write("tank_cg_loc = " + str(CG_calculations_hyd().tank_cg_loc ) + "\n")
f.write("mass_fuel = " + str(CG_calculations_hyd().mass_fuel ) + "\n")
f.write("mass_tank = " + str(CG_calculations_hyd().mass_tank ) + "\n")
f.write("x_oew = " + str(CG_calculations_hyd().x_oew ) + "\n")
f.write("x_payload = " + str(CG_calculations_hyd().x_payload ) + "\n")
f.write("cg_forward = " + str(CG_calculations_hyd().cg_forward ) + "\n")
f.write("cg_aft = " + str(CG_calculations_hyd().cg_aft ) + "\n\n")

f.write("Outputs Propulsion_System class \n\n")
f.write("y_pos = " + str(Propulsion_System().y_pos ) + "\n")
f.write("z_pos = " + str(Propulsion_System().z_pos ) + "\n")
f.write("x_pos = " + str(Propulsion_System().x_pos ) + "\n\n")

f.write("Outputs Fan_engine class \n\n")
f.write("massflow = " + str(Fan_engine().massflow ) + "\n")
f.write("ratio_inlet_to_spinner = " + str(Fan_engine().ratio_inlet_to_spinner ) + "\n")
f.write("inlet_diameter = " + str(Fan_engine().inlet_diameter ) + "\n")
f.write("nacelle_length = " + str(Fan_engine().nacelle_length ) + "\n")
f.write("fan_length = " + str(Fan_engine().fan_length ) + "\n")
f.write("loc_max_diameter = " + str(Fan_engine().loc_max_diameter ) + "\n")
f.write("max_diameter = " + str(Fan_engine().max_diameter ) + "\n")
f.write("exit_diameter = " + str(Fan_engine().exit_diameter ) + "\n")
f.write("length_gas_generator = " + str(Fan_engine().length_gas_generator ) + "\n")
f.write("diameter_gas_generator = " + str(Fan_engine().diameter_gas_generator ) + "\n")
f.write("exit_diameter_gas_generator = " + str(Fan_engine().exit_diameter_gas_generator ) + "\n\n")

f.write("Outputs New_Fuselage_Profile class \n\n")
f.write("delta_radius = " + str(New_Fuselage_Profile().delta_radius ) + "\n")
f.write("straight_length_midpoints = " + str(New_Fuselage_Profile().straight_length_midpoints ) + "\n")
f.write("straight_length_outer = " + str(New_Fuselage_Profile().straight_length_outer ) + "\n")
f.write("angle_1 = " + str(New_Fuselage_Profile().angle_1 ) + "\n")
f.write("angle_2 = " + str(New_Fuselage_Profile().angle_2 ) + "\n")
f.write("y_lower = " + str(New_Fuselage_Profile().y_lower ) + "\n")
f.write("y_upper = " + str(New_Fuselage_Profile().y_upper ) + "\n")
f.write("z_lower = " + str(New_Fuselage_Profile().z_lower ) + "\n")
f.write("z_upper = " + str(New_Fuselage_Profile().z_upper ) + "\n")
f.close()