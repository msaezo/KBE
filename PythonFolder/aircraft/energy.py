import numpy as np
import aircraft.Import_Input as In
from math import *
import warnings

from parapy.core import *
from parapy.geom import *

from aircraft.fuselage import Fuselage
from aircraft.empennage import HorizontalTail
from aircraft.empennage import VerticalTail
from aircraft.propulsion import FanEngine
from aircraft.wing import Wing
from aircraft.runQ3D import Q3D


# This class actually makes the tanks,
# uses drag as input and based on the range and efficiency calculates the required energy storage
# designs tanks to fit that amount of liquid hydrogen and placed it below the fuselage floor

# Drag class estimates the drag of the fuselage and empennage
# energy class calculates energy needed based on drag and sizes the tanks
# Tanks class only places the tanks

class Tanks(GeomBase):
    # range = Input(In.Range)
    # efficiency = Input(In.total_efficiency)
    # energy_density = Input(In.energy_density)
    # fus_diam = Input(Fuselage().diameter_fuselage_outer)
    # length_fuselage = Input(Fuselage().length_fuselage)
    # length_tailcone = Input(Fuselage().length_tailcone)
    # drag = Input(5)

    length_cockpit = Input(Fuselage().length_cockpit)
    diameter_fuselage_inner = Input(Fuselage().diameter_fuselage_inner)
    position_floor_lower = Input(Fuselage().position_floor_lower)
    diameter_tank_final = Input(0.5)
    number_of_tanks = Input(5)
    length_tank = Input(10)

    @Attribute
    def y_pos(self):
        return (1.1 * self.diameter_tank_final * (self.number_of_tanks - 1)) / 2

    @Attribute
    def z_pos(self):
        return self.position_floor_lower - 1.1 * self.diameter_tank_final / 2

    @Attribute
    def tank_max_dim(self):
        if 1.1 * self.diameter_tank_final / 2 >= self.diameter_fuselage_inner / 2:
            msg = "The diameter of the hydrogen tanks is too big to be realistic, a lower ratio compared to the " \
                  "fuselage diameter is expected. " \
                  "Suggested options:" \
                  "     - Decrease range of the aircraft"
            warnings.warn(msg)
            if self.popup_gui:  # invoke pop-up dialogue box using Tk"""
                generate_warning("Warning: Value changed", msg)
        return np.sqrt(self.y_pos ** 2 + self.z_pos ** 2) + self.diameter_tank_final / 2

    @Attribute
    def new_fuselage(self):
        if self.tank_max_dim < self.diameter_fuselage_inner:
            result = 'False'
        else:
            result = 'True'
        return result

    @Part
    def tank(self):
        return Energy2(quantify=self.number_of_tanks,
                       diameter_tank_final=self.diameter_tank_final,
                       length_tank = self.length_tank,
                       position=translate(self.position,
                                          'x', self.length_cockpit,
                                          'y', self.y_pos - 1.1 * self.diameter_tank_final * child.index,
                                          'z', self.z_pos),
                       hidden=False)


# Calculates drag of fuselage, nacelles and empennage through wetter surface and form factors
# adds all drag coeffieinct together in the end
class Drag(GeomBase):
    lift_coefficient = Input(Q3D().cldes)
    drag_coefficient = Input(Q3D().cddes)
    surface = Input(Wing().area_wing)
    density = Input(Q3D().air_density)
    velocity = Input(Q3D().air_speed)
    eq_skinfriction_coefficient = Input(In.eq_skinfriction_coefficient)
    fus_diam = Input(Fuselage().diameter_fuselage_outer)
    fus_len = Input(Fuselage().length_fuselage)
    ht_surface = Input(HorizontalTail().surface_horizontal_tail)
    ht_sweep = Input(HorizontalTail().sweep_cuarter_chord_horizontal_tail)
    vt_surface = Input(VerticalTail().surface_vertical_tail)
    vt_sweep = Input(VerticalTail().sweep_cuarter_chord_vertical_tail)
    thick_to_chord = Input(0.24)
    max_thick = Input(0.25)
    len_nacelle = Input(FanEngine().nacelle_length)
    cowling_length = Input(FanEngine().fan_length)
    cowling_length_1 = Input(FanEngine().loc_max_diameter)
    cowling_diam = Input(FanEngine().max_diameter)
    cowling_fan = Input(FanEngine().inlet_diameter)
    cowling_ef = Input(FanEngine().exit_diameter)
    gg_length = Input(FanEngine().length_gas_generator)
    gg_diam = Input(FanEngine().diameter_gas_generator)
    gg_diam_exit = Input(FanEngine().exit_diameter_gas_generator)
    q_nacelle = Input(1.3)
    q_fuselage = Input(1)
    q_emp = Input(1.04)

    t_zero = Input(288)  # Kelvin
    t_zero_vs = Input(273)  # Kelvin
    s_vis = Input(111)  # Kelvin
    p_zero = Input(101325)  # Pa
    rho_zero = Input(1.225)  # kg/m3
    deltat = Input(-0.0065)  # K/m
    viscosity_dyn_zero = Input(1.716 * 10 ** (-5))
    span = Input(Wing().span)  # m input total, Q3D puts half of it already
    root_chord = Input(Wing().chord_root)  # m
    tip_chord = Input(Wing().chord_tip)  # m
    mac = Input(Wing().mean_aerodynamic_chord)  # m

    altitude = Input(Wing().altitude_cruise)  # m
    mach = Input(Wing().mach_cruise)  # make it in accordance with the flight speed and altitude
    cl = Input(Wing().lift_coefficient)  # if Cl is used do not use angle of attack

    popup_gui = Input(False)

    @Attribute
    def temperature(self):
        if self.altitude < 11001:
            temp = self.t_zero + self.altitude * self.deltat
        else:
            temp = self.t_zero + 11000 * self.deltat
        return temp

    @Attribute
    def pressure(self):
        if self.altitude < 11001:
            press = self.p_zero * np.e ** ((-9.81665 / (287 * self.temperature)) * self.altitude)
        else:
            press = 22632 * (self.temperature / 216.65) ** (-9.81665 / (self.altitude * 287))
        return press

    @Attribute
    def sound_speed(self):
        return np.sqrt(1.4 * 287 * self.temperature)

    @Attribute
    def air_speed(self):
        return self.mach * self.sound_speed

    @Attribute
    def air_density(self):
        return self.pressure / (287 * self.temperature)

    @Attribute
    def viscosity_dyn(self):
        return self.viscosity_dyn_zero * ((self.temperature / self.t_zero_vs) ** (3 / 2)
                                          * (self.t_zero_vs + self.s_vis) / (
                                                  self.temperature + self.s_vis))  # Sutherland's' Law

    @Attribute
    def reynolds(self):
        return self.air_density * self.air_speed * self.mac / self.viscosity_dyn

    @Attribute
    def dynamic_pressure(self):
        return 1 / 2 * self.density * self.velocity ** 2

    @Attribute
    def wet_area_fus(self):
        return pi * self.fus_diam * self.fus_len * (1 - 2 / (self.fus_len / self.fus_diam)) ** (2 / 3) \
               * (1 + 1 / (self.fus_len / self.fus_diam))

    @Attribute
    def wet_area_ht(self):
        return 2 * self.ht_surface * 0.8 * (1 + 0.25 * self.thick_to_chord)  # 0.8 is the ratio of area inside the fus

    @Attribute
    def wet_area_vt(self):
        return 2 * self.vt_surface * 0.9 * (1 + 0.25 * self.thick_to_chord)  # 0.9 is the ratio of area inside the fus

    @Attribute
    def wet_area_nacelle(self):
        wet_area_cowl = self.cowling_length * self.cowling_diam * (
                2 + 0.35 * self.cowling_length_1 / self.cowling_length *
                0.8 * (self.cowling_length * self.cowling_fan) /
                (self.cowling_length * self.cowling_diam) +
                1.15 * (1 - self.cowling_length_1 / self.cowling_length) *
                self.cowling_ef / self.cowling_diam)
        wet_area_gas = pi * self.gg_length * self.gg_diam * (1 - 1 / 3 * (1 - self.gg_diam_exit / self.gg_diam)
                                                             * (1 - 0.18 * (self.gg_diam / self.gg_length) ** (5 / 3)))
        return wet_area_cowl + wet_area_gas

    @Attribute
    def wet_area_total(self):
        return self.wet_area_fus + self.wet_area_ht + self.wet_area_vt + self.wet_area_nacelle

    @Attribute
    def skin_friction(self):
        return 0.455 / (log(self.reynolds) ** 2.58 * (1 + 0.144 * self.mach ** 2) ** 0.65)

    @Attribute
    def form_factor_ht(self):
        return (1 + 0.6 / self.max_thick * self.thick_to_chord + 100 * self.thick_to_chord ** 4) * \
               (1.34 * self.mach ** 0.18 * cos(self.ht_sweep * pi / 180) ** 0.28)

    @Attribute
    def form_factor_vt(self):
        return (1 + 0.6 / self.max_thick * self.thick_to_chord + 100 * self.thick_to_chord ** 4) * \
               (1.34 * self.mach ** 0.18 * cos(self.vt_sweep * pi / 180) ** 0.28)

    @Attribute
    def form_factor_fus(self):
        return 1 + 60 / (self.fus_len / self.fus_diam) ** 3 + (self.fus_len / self.fus_diam) / 400

    @Attribute
    def form_factor_nacelle(self):
        return 1 + 0.35 / (self.len_nacelle / self.cowling_diam)

    @Attribute
    def drag_coeff_fus(self):
        return self.skin_friction * self.form_factor_fus * self.q_fuselage * self.wet_area_fus / self.surface

    @Attribute
    def drag_coeff_ht(self):
        return self.skin_friction * self.form_factor_ht * self.q_emp * self.wet_area_ht / self.surface

    @Attribute
    def drag_coeff_vt(self):
        return self.skin_friction * self.form_factor_vt * self.q_emp * self.wet_area_vt / self.surface

    @Attribute
    def drag_coeff_nacelle(self):
        return self.skin_friction * self.form_factor_nacelle * self.q_nacelle * self.wet_area_nacelle / self.surface

    @Attribute
    def drag_coeff_wing(self):
        if np.isnan(self.drag_coefficient) is True:
            cd = self.lift_coefficient / 20
        else:
            cd = self.drag_coefficient
        return cd

    @Attribute
    def drag_coefficient_total(self):
        return self.drag_coeff_fus + self.drag_coeff_wing + self.drag_coeff_ht + self.drag_coeff_vt \
               + self.drag_coeff_nacelle

    @Attribute
    def drag_tot(self):
        return self.drag_coefficient_total * self.dynamic_pressure * self.surface


# calculates energy needed through drag  and transfers it to required volume of tanks
# the required volume is then divided over the number of tanks that fit the best
#

class Energy1(GeomBase):
    range = Input(In.Range)
    efficiency = Input(In.total_efficiency)
    energy_density = Input(In.energy_density)
    n_tanks = Input([1, 2, 3, 4])
    drag = Input(Drag().drag_tot)
    fus_diam = Input(Fuselage().diameter_fuselage_inner)
    length_fuselage = Input(Fuselage().length_fuselage)
    length_cockpit = Input(Fuselage().length_cockpit)
    length_tailcone = Input(Fuselage().length_tailcone)
    position_floor_lower = Input(Fuselage().position_floor_lower)

    popup_gui = Input(False)

    @Attribute
    def work(self):
        return self.drag * self.range * 1000

    @Attribute
    def energy_req(self):
        return self.work / self.efficiency

    @Attribute
    def vol_needed(self):
        return self.energy_req / (self.energy_density * 10 ** 6)

    @Attribute
    def length_tank(self):
        return (self.length_fuselage - self.length_cockpit - self.length_tailcone) * 0.95

    @Attribute
    def diameter_tank(self):
        diameter = []
        for i in range(0, len(self.n_tanks)):
            coeff = [1, 0.75 * self.length_tank, -0.75 * self.vol_needed / self.n_tanks[i] * 1 / np.pi]
            roots = np.roots(coeff)
            roots1 = roots[0]
            roots2 = roots[1]
            # print (roots1)
            # print (roots2)
            if roots1 > 0:
                radius = roots1
            else:
                radius = roots2
            diameter.append(radius * 2)

        return diameter

    @Attribute
    def number_of_tanks(self):
        max_distance = []
        for i in range(0, len(self.n_tanks)):
            z_pos = self.position_floor_lower - 1.1 * self.diameter_tank[i] / 2
            y_pos = (1.1 * self.diameter_tank[i] * (self.n_tanks[i] - 1)) / 2
            tot_pos = np.sqrt(z_pos ** 2 + y_pos ** 2)
            max_distance.append(tot_pos)
        max_dist = min(max_distance)
        for i in range(0, len(self.n_tanks)):
            if max_dist == max_distance[i]:
                n_tanks = i
            else:
                n_tanks = 2
        return n_tanks

    @Attribute
    def diameter_tank_final(self):
        return self.diameter_tank[self.number_of_tanks - 1]

    # @Part
    # def cylinder(self):
    #     return Cylinder(radius=self.diameter_tank_final / 2,
    #                     height=self.length_tank,
    #                     centered=True,
    #                     position=translate(
    #                         rotate(self.position, "y", np.deg2rad(90)),
    #                         "z", self.length_tank / 2 + self.diameter_tank_final / 2),
    #                     mesh_deflection=0.0001,
    #                     hidden=True)
    #
    # @Part
    # def sphere1(self):
    #     return Sphere(radius=self.diameter_tank_final / 2,
    #                   position=translate(self.position,
    #                                      "x", self.diameter_tank_final / 2),
    #                   hidden=True)
    #
    # @Part
    # def sphere2(self):
    #     return Sphere(radius=self.diameter_tank_final / 2,
    #                   position=translate(self.position,
    #                                      "x", self.length_tank + self.diameter_tank_final / 2),
    #                   hidden=True)
    #
    # @Part
    # def tank1(self):
    #     return FusedSolid(shape_in=self.cylinder,
    #                       tool=self.sphere1,
    #                       hidden=True)
    #
    # @Part
    # def tank(self):
    #     return FusedSolid(shape_in=self.tank1,
    #                       tool=self.sphere2,
    #                       hidden=False,
    #                       color="Orange")


class Energy2(GeomBase):

    diameter_tank_final = Input(Energy1().diameter_tank_final)
    length_tank = Input(Energy1().length_tank)
    #
    #
    # range = Input(Tanks().range)
    # efficiency = Input(Tanks().efficiency)
    # energy_density = Input(Tanks().energy_density)
    # n_tanks = Input([1, 2, 3, 4])
    # drag = Input(Drag().drag_tot)
    # fus_diam = Input(Fuselage().diameter_fuselage_inner)
    # length_fuselage = Input(Fuselage().length_fuselage)
    # length_cockpit = Input(Fuselage().length_cockpit)
    # length_tailcone = Input(Fuselage().length_tailcone)
    # position_floor_lower = Input(Fuselage().position_floor_lower)

    popup_gui = Input(False)

    # @Attribute
    # def work(self):
    #     return self.drag * self.range * 1000
    #
    # @Attribute
    # def energy_req(self):
    #     return self.work / self.efficiency
    #
    # @Attribute
    # def vol_needed(self):
    #     return self.energy_req / (self.energy_density * 10 ** 6)
    #
    # @Attribute
    # def length_tank(self):
    #     return (self.length_fuselage - self.length_cockpit - self.length_tailcone) * 0.95
    #
    # @Attribute
    # def diameter_tank(self):
    #     diameter = []
    #     for i in range(0, len(self.n_tanks)):
    #         coeff = [1, 0.75 * self.length_tank, -0.75 * self.vol_needed / self.n_tanks[i] * 1 / np.pi]
    #         roots = np.roots(coeff)
    #         roots1 = roots[0]
    #         roots2 = roots[1]
    #         # print (roots1)
    #         # print (roots2)
    #         if roots1 > 0:
    #             radius = roots1
    #         else:
    #             radius = roots2
    #         diameter.append(radius * 2)
    #
    #     return diameter
    #
    # @Attribute
    # def number_of_tanks(self):
    #     max_distance = []
    #     for i in range(0, len(self.n_tanks)):
    #         z_pos = self.position_floor_lower - 1.1 * self.diameter_tank[i] / 2
    #         y_pos = (1.1 * self.diameter_tank[i] * (self.n_tanks[i] - 1)) / 2
    #         tot_pos = np.sqrt(z_pos ** 2 + y_pos ** 2)
    #         max_distance.append(tot_pos)
    #     max_dist = min(max_distance)
    #     for i in range(0, len(self.n_tanks)):
    #         if max_dist == max_distance[i]:
    #             n_tanks = i
    #         else:
    #             n_tanks = 2
    #     return n_tanks
    #
    # @Attribute
    # def diameter_tank_final(self):
    #     return self.diameter_tank[self.number_of_tanks - 1]

    @Part
    def cylinder(self):
        return Cylinder(radius=self.diameter_tank_final / 2,
                        height=self.length_tank,
                        centered=True,
                        position=translate(
                            rotate(self.position, "y", np.deg2rad(90)),
                            "z", self.length_tank / 2 + self.diameter_tank_final / 2),
                        mesh_deflection=0.0001,
                        hidden=True)

    @Part
    def sphere1(self):
        return Sphere(radius=self.diameter_tank_final / 2,
                      position=translate(self.position,
                                         "x", self.diameter_tank_final / 2),
                      hidden=True)

    @Part
    def sphere2(self):
        return Sphere(radius=self.diameter_tank_final / 2,
                      position=translate(self.position,
                                         "x", self.length_tank + self.diameter_tank_final / 2),
                      hidden=True)

    @Part
    def tank1(self):
        return FusedSolid(shape_in=self.cylinder,
                          tool=self.sphere1,
                          hidden=True)

    @Part
    def tank(self):
        return FusedSolid(shape_in=self.tank1,
                          tool=self.sphere2,
                          hidden=False,
                          color="Orange")


def generate_warning(warning_header, msg):
    """
    This function generates the warning dialog box
    :param warning_header: The text to be shown on the dialog box header
    :param msg: the message to be shown in dialog box
    :return: None as it is GUI operation
    """
    from tkinter import Tk, messagebox

    # initialization
    window = Tk()
    window.withdraw()

    # generates message box
    messagebox.showwarning(warning_header, msg)

    # kills the gui
    window.deiconify()
    window.destroy()
