import numpy as np
import aircraft.Import_Input as I
from math import *

from parapy.core import *
from parapy.geom import *


from aircraft.fuselage import Fuselage
from aircraft.empennage import Horizontal_Tail
from aircraft.empennage import Vertical_Tail
from aircraft.propulsion import Fan_engine
from aircraft.wing import Wing
from aircraft.runQ3D import Q3D


class Tanks(GeomBase):
    range            = Input(I.Range)
    lift_coefficient = Input(Q3D().CLdes)
    drag_coefficient = Input(Q3D().CDdes)
    surface          = Input(I.Wing_area)
    density          = Input(Q3D().airDensity)
    velocity         = Input(Q3D().airSpeed)
    efficiency       = Input(I.total_efficiency)
    energy_density   = Input(I.energy_density)

    @Attribute
    def y_pos(self):
        return (1.1 * Energy().diameter_tank_final * (Energy().number_of_tanks - 1)) / 2

    @Attribute
    def z_pos(self):
        return Fuselage().position_floor_lower - 1.1 * Energy().diameter_tank_final / 2

    @Attribute
    def tank_max_dim(self):
        return np.sqrt(self.y_pos**2 + self.z_pos**2)+Energy().diameter_tank_final/2

    @Attribute
    def new_fuselage(self):
        if self.tank_max_dim < Fuselage().diameter_fuselage_inner:
            result = 'False'
        else:
            result = 'True'
        return result

    @Part
    def tank(self):
        return Energy(quantify=Energy().number_of_tanks,
                      position=translate(self.position,
                                         'x', Fuselage().length_cockpit,
                                         'y', self.y_pos - 1.1 * Energy().diameter_tank_final * child.index,
                                         'z', self.z_pos),
                      hidden=False)


class Drag(GeomBase):

    lift_coefficient            = Input(Tanks().lift_coefficient)
    drag_coefficient            = Input(Tanks().drag_coefficient)
    surface                     = Input(Tanks().surface)
    density                     = Input(Tanks().density)
    velocity                    = Input(Tanks().velocity)
    eq_skinfriction_coefficient = Input(I.eq_skinfriction_coefficient)
    fus_diam                    = Input(Fuselage().diameter_fuselage_outer)
    fus_len                     = Input(Fuselage().length_fuselage)
    ht_surface                  = Input(Horizontal_Tail().surfaceHorizontalTail)
    ht_sweep                    = Input(Horizontal_Tail().sweepCuarterChordHorizontalTail)
    vt_surface                  = Input(Vertical_Tail().surfaceVerticalTail)
    vt_sweep                    = Input(Vertical_Tail().sweepCuarterChordVerticalTail)
    thick_to_chord              = Input(0.24)
    max_thick                   = Input(0.25)
    len_nacelle                  = Input(Fan_engine().nacelle_length)
    cowling_length              = Input(Fan_engine().fan_length)
    cowling_length_1            = Input(Fan_engine().loc_max_diameter)
    cowling_diam                = Input(Fan_engine().max_diameter)
    cowling_fan                 = Input(Fan_engine().inlet_diameter)
    cowling_ef                  = Input(Fan_engine().exit_diameter)
    gg_length                   = Input(Fan_engine().length_gas_generator)
    gg_diam                     = Input(Fan_engine().diameter_gas_generator)
    gg_diam_exit                = Input(Fan_engine().exit_diameter_gas_generator)
    q_nacelle                   = Input(1.3)
    q_fuselage                  = Input(1)
    q_emp                       = Input(1.04)

    T_zero   = Input(288) #Kelvin
    T_zero_vs= Input(273) #Kelvin
    S_vis    = Input(111) #Kelvin
    P_zero   = Input(101325) #Pa
    Rho_zero = Input(1.225) #kg/m3
    deltaT   = Input(-0.0065) #K/m
    viscosity_dyn_zero = Input(1.716*10**(-5))
    span       = Input(Wing().span)  # m input total, Q3D puts half of it already
    root_chord = Input(Wing().chord_root)  # m
    tip_chord  = Input(Wing().chord_tip)  # m
    MAC        = Input(Wing().mean_aerodynamic_chord) # m

    altitude = Input(Wing().altitude_cruise)  # m
    Mach     = Input(Wing().mach_cruise)  # make it in accordance with the flight speed and altitude
    Cl       = Input(Wing().lift_coefficient) # if Cl is used do not use angle of attack

    @Attribute
    def temperature(self):
        if self.altitude <11001:
            temp = self.T_zero + self.altitude*self.deltaT
        else:
            temp = self.T_zero + 11000*self.deltaT
        return temp

    @Attribute
    def pressure(self):
        if self.altitude <11001:
            press = self.P_zero * (np.e) ** ((-9.81665 / (287 * self.temperature)) * (self.altitude))
        else:
            press = 22632 * (self.temperature / 216.65) ** (-9.81665 / (self.altitude * 287))
        return press

    @Attribute
    def soundSpeed(self):
        return np.sqrt(1.4*287*self.temperature)

    @Attribute
    def airSpeed(self):
        return self.Mach *self.soundSpeed

    @Attribute
    def airDensity(self):
        return self.pressure/(287*self.temperature)

    @Attribute
    def viscosity_dyn(self):
        return self.viscosity_dyn_zero*((self.temperature/self.T_zero_vs)**(3/2)*(self.T_zero_vs+self.S_vis)/\
                                        (self.temperature+self.S_vis))  # Sutherlands' Law

    @Attribute
    def reynolds(self):
        return self.airDensity*self.airSpeed*self.MAC/self.viscosity_dyn


    @Attribute
    def dynamic_pressure(self):
        return 1/2*self.density*self.velocity**2

    @Attribute
    def wet_area_fus(self):
        return pi * self.fus_diam * self.fus_len * (1 - 2/(self.fus_len/self.fus_diam))**(2/3)*(1 + 1/(self.fus_len/self.fus_diam))

    @Attribute
    def wet_area_ht(self):
        return 2*self.ht_surface * 0.8 * (1+0.25*self.thick_to_chord)  # 0.8 is the ratio of area inside the fus

    @Attribute
    def wet_area_vt(self):
        return 2*self.vt_surface * 0.9 * (1+0.25*self.thick_to_chord)  # 0.9 is the ratio of area inside the fus

    @Attribute
    def wet_area_nacelle(self):
        wet_area_cowl = self.cowling_length*self.cowling_diam*(2+0.35*self.cowling_length_1/self.cowling_length *
                                                               0.8*(self.cowling_lenght * self.cowling_fan)/
                                                               (self.cowling_length * self.cowling_diam) +
                                                               1.15*(1-self.cowling_length_1/self.cowling_length)*
                                                               self.cowling_ef/self.cowling_diam)
        wet_area_gas = pi*self.gg_length*self.gg_diam*(1-1/3*(1-self.gg_diam_exit/self.gg_diam)
                                                       *(1-0.18*(self.gg_diam/self.gg_length)**(5/3)))
        return wet_area_cowl + wet_area_gas

    @Attribute
    def wet_area_total(self):
        return self.wet_area_fus + self.wet_area_ht + self.wet_area_vt + self.wet_area_nacelle

    @Attribute
    def skin_friction(self):
        return 0.455/(log(self.reynolds)**2.58 * (1+0.144 * self.Mach**2)**0.65)

    @Attribute
    def form_factor_ht(self):
        return (1+0.6/self.max_thick * self.thick_to_chord +100 * self.thick_to_chord**4)*\
               (1.34*self.Mach**0.18*cos(self.ht_sweep * pi/180)**0.28)

    @Attribute
    def form_factor_vt(self):
        return (1+0.6/self.max_thick * self.thick_to_chord +100 * self.thick_to_chord**4)*\
               (1.34*self.Mach**0.18*cos(self.vt_sweep * pi/180)**0.28)

    @Attribute
    def form_factor_fus(self):
        return 1 + 60/(self.fus_len/self.fus_diam)**3 + (self.fus_len/self.fus_diam)/400

    @Attribute
    def form_factor_nacelle(self):
        return 1 + 0.35/(self.len_nacelle/self.cowling_diam)

    @Attribute
    def drag_coeff_fus(self):
        return self.skin_friction * self.form_factor_fus * self.q_fuselage * self.wet_area_fus/self.surface

    @Attribute
    def drag_coeff_ht(self):
        return self.skin_friction * self.form_factor_ht * self.q_emp * self.wet_area_ht/self.surface

    @Attribute
    def drag_coeff_vt(self):
        return self.skin_friction * self.form_factor_vt * self.q_emp * self.wet_area_vt/self.surface

    @Attribute
    def drag_coeff_nacelle(self):
        return self.skin_friction * self.form_factor_nacelle * self.q_nacelle * self.wet_area_nacelle/self.surface

    @Attribute
    def drag_coeff_wing(self):
        if np.isnan(self.drag_coefficient) == True:
            cd = self.lift_coefficient/20
        else:
            cd = self.drag_coefficient
        return cd

    @Attribute
    def drag_coefficient_total(self):
        return self.drag_coeff_fus + self.drag_coeff_wing + self.drag_coeff_ht + self.drag_coeff_vt \
               + self.drag_coeff_nacelle

    @Attribute
    def drag(self):
        return self.drag_coefficient_total*self.dynamic_pressure*self.surface


class Energy(GeomBase):

    range            = Input(Tanks().range)
    efficiency       = Input(Tanks().efficiency)
    energy_density   = Input(Tanks().energy_density)
    n_tanks          = Input([1,2,3,4])
    drag             = Input(Drag.drag)


    @Attribute
    def work(self):
        return self.drag*self.range*1000

    @Attribute
    def energy_req(self):
        return self.work/self.efficiency

    @Attribute
    def vol_needed(self):
        return self.energy_req/(self.energy_density*10**6)

    @Attribute
    def length_tank(self):
        return (Fuselage().length_fuselage-Fuselage().length_cockpit-Fuselage().length_tailcone)*0.95

    @Attribute
    def diameter_tank(self):
        diameter = []
        for i in range(0,len(self.n_tanks)):
            coeff = [1, 0.75*self.length_tank, -0.75*self.vol_needed/self.n_tanks[i] *1/np.pi ]
            roots = np.roots(coeff)
            roots1 = roots[0]
            roots2 = roots[1]
            # print (roots1)
            # print (roots2)
            if roots1>0:
                radius = roots1
            else :
                radius = roots2
            diameter.append(radius*2)
        return diameter

    @Attribute
    def number_of_tanks(self):
        max_distance = []
        for i in range(0, len(self.n_tanks)):
            z_pos = Fuselage().position_floor_lower -1.1*self.diameter_tank[i]/2
            y_pos = (1.1*self.diameter_tank[i]*(self.n_tanks[i]-1))/2
            tot_pos = np.sqrt(z_pos**2 + y_pos**2)
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
        return self.diameter_tank[self.number_of_tanks-1]



    @Part
    def cylinder(self):
        return Cylinder(radius=self.diameter_tank_final/2,
                       height=self.length_tank,
                       centered=True,
                       position=translate(
                           rotate(self.position, "y", np.deg2rad(90)),
                           "z", self.length_tank/2 + self.diameter_tank_final/2),
                       mesh_deflection=0.0001,
                       hidden=True)

    @Part
    def sphere1(self):
        return Sphere(radius=self.diameter_tank_final/2,
                      position=translate(self.position,
                          "x", self.diameter_tank_final/2),
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

