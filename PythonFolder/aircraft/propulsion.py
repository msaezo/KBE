import numpy as np
from parapy.core import *
from parapy.geom import *
from math import *

import aircraft.Import_Input as I
from aircraft.fuselage import Fuselage
from aircraft.wing import Wing
from aircraft.empennage import  Vertical_Tail


# Class that defines location of engines and places them
class Propulsion_System(GeomBase):

    n_engines          = Input(I.N_engines)
    thrust_to          = Input(I.Thrust_TO)
    bypass_ratio       = Input(I.BPR)
    turbine_inlet_temp = Input(I.Temp_T_4)
    phi                = Input(I.Phi)

    @Attribute
    def y_pos(self):
        if self.n_engines ==1:
            pos1 = 0
            y_distr = [pos1]
        elif self.n_engines ==2:
            pos1 = 0.35*Wing().span/2
            y_distr = [-pos1, pos1]
        elif self.n_engines == 3:
            pos1 = 0.35 * Wing().span / 2
            pos2 = 0
            y_distr = [-pos1, pos2, pos1]
        elif self.n_engines == 4:
            pos1 = 0.4 * Wing().span / 2
            pos2 = 0.7 * Wing().span / 2
            y_distr = [-pos2, -pos1, pos1, pos2]
        return y_distr

    @Attribute
    def z_pos(self):
        if self.n_engines ==1:
            pos1 = Fuselage().diameter_fuselage_outer/2 + Fan_engine().max_diameter * 1.1/2
            z_distr = [pos1]
        elif self.n_engines == 2:
            pos1 = Wing().wing_z_shift + np.tan(np.deg2rad(Wing().dihedral)) * 0.35 * Wing().span/2 - Fan_engine().max_diameter*1.1/2
            z_distr = [pos1, pos1]
        elif self.n_engines == 3:
            pos1 = Wing(wing_highlow="high").wing_z_shift + np.tan(np.deg2rad(Wing().dihedral)) * 0.35 * Wing().span / 2 - Fan_engine().max_diameter * 1.1/2
            pos2 = Fuselage().diameter_fuselage_outer/2 + Fan_engine().max_diameter * 1.1/2
            z_distr = [pos1, pos2, pos1]
        elif self.n_engines == 4:
            pos1 = Wing().wing_z_shift + np.tan(np.deg2rad(Wing().dihedral)) * 0.4 * Wing().span / 2 - Fan_engine().max_diameter * 1.1/2
            pos2 = Wing().wing_z_shift + np.tan(np.deg2rad(Wing().dihedral)) * 0.7 * Wing().span / 2 - Fan_engine().max_diameter * 1.1/2
            z_distr = [pos2, pos1, pos1, pos2]
        return z_distr

    @Attribute
    def x_pos(self):
        if self.n_engines == 1:
            pos1 = Vertical_Tail().x_tail_vertical - 0.5
            x_distr = [pos1]
        elif self.n_engines ==2:
            pos1 = Wing().wing_x_shift + np.tan(np.deg2rad(Wing().sweep_leading_edge)) * 0.35 * Wing().span / 2 - 0.5
            x_distr = [pos1, pos1]
        elif self.n_engines == 3:
            pos1 = Wing().wing_x_shift + np.tan(np.deg2rad(Wing().sweep_leading_edge)) * 0.35 * Wing().span / 2 - 0.5
            pos2 = Vertical_Tail().x_tail_vertical -0.5
            x_distr = [pos1, pos2, pos1]
        elif self.n_engines == 4:
            pos1 = Wing().wing_x_shift + np.tan(np.deg2rad(Wing().sweep_leading_edge)) * 0.4 * Wing().span / 2 - 0.5
            pos2 = Wing().wing_x_shift + np.tan(np.deg2rad(Wing().sweep_leading_edge)) * 0.7 * Wing().span / 2 - 0.5
            x_distr = [pos2, pos1, pos1, pos2]
        return x_distr

    @Part
    def propulsion_system(self):
        return Fan_engine(quantify=int(self.n_engines),
                        position=translate(self.position,
                                           'x', self.x_pos[child.index],
                                           'y', self.y_pos[child.index],
                                           'z', self.z_pos[child.index]),
                        hidden=False)


# class that creates one engine
class Fan_engine(GeomBase):
    thrust_to          = Input(Propulsion_System().thrust_to)
    n_engines          = Input(Propulsion_System().n_engines)
    bypass_ratio       = Input(Propulsion_System().bypass_ratio)
    turbine_inlet_temp = Input(Propulsion_System().turbine_inlet_temp)
    phi                = Input(Propulsion_System().phi)

    eta_n       = Input(0.97)
    eta_tf      = Input(0.75)
    sound_speed = Input(343)
    rho_0       = Input(1.225)



    @Attribute
    def massflow(self):
        G = self.turbine_inlet_temp/600 -1.25
        return (self.thrust_to*10**6)/(self.n_engines*self.sound_speed) * (1+self.bypass_ratio)/(np.sqrt(5*self.eta_n*G*(1+self.eta_tf*self.bypass_ratio)))

    @Attribute
    def ratio_inlet_to_spinner(self):
        return 0.05*(1+0.1*(self.rho_0*self.sound_speed)/(self.massflow) + (3*self.bypass_ratio)/(1+self.bypass_ratio))

    @Attribute
    def inlet_diameter(self):
        return 1.65 * np.sqrt((0.005+(self.massflow)/(self.rho_0*self.sound_speed))/(1-self.ratio_inlet_to_spinner**2))

    @Attribute
    def nacelle_length(self):
        if self.phi == 1:
            cl = 9.8
            delta_l = 0.05
            beta = 0.35

        elif self.phi <1:
            cl = 7.8
            delta_l = 0.1
            beta = 0.21 + (0.12) / (np.sqrt(self.phi - 0.3))

        return cl*(delta_l +np.sqrt((self.massflow*(1+0.2*self.bypass_ratio))/(self.rho_0*self.sound_speed*(1+self.bypass_ratio))))

    @Attribute
    def fan_length(self):
        return self.phi*self.nacelle_length

    @Attribute
    def loc_max_diameter(self):
        if self.phi == 1:
            beta = 0.35
        elif self.phi <1:
            beta = 0.21 + (0.12) / (np.sqrt(self.phi - 0.3))
        return beta

    @Attribute
    def max_diameter(self):
        return self.inlet_diameter +0.06*self.fan_length+0.03

    @Attribute
    def exit_diameter(self):
        return self.max_diameter*(1-1/3*self.phi**2)

    @Attribute
    def length_gas_generator(self):
        return (1-self.phi)*self.nacelle_length

    @Attribute
    def diameter_gas_generator(self):
        lambda_m_over_a_rho = self.bypass_ratio*self.massflow/(self.rho_0*self.sound_speed)
        return self.exit_diameter*((0.089*lambda_m_over_a_rho +4.5)/(0.067*lambda_m_over_a_rho+5.8))**2

    @Attribute
    def exit_diameter_gas_generator(self):
        return 0.55*self.diameter_gas_generator

    @Part
    def spinner(self):
        return Cone(radius1= 0.05,
                    radius2=self.inlet_diameter*self.ratio_inlet_to_spinner,
                    height=0.5,
                    position=rotate(self.position, "y", np.deg2rad(90)),
                    color="yellow")

    @Part
    def fan(self):
        return Cylinder(radius=self.inlet_diameter / 2,
                        height=self.inlet_diameter * 0.05,
                        position=translate(rotate(self.position, "y", np.deg2rad(90)),"z",0.5),
                        color="orange")

    @Part
    def core(self):
        return Cylinder(radius=self.diameter_gas_generator / 2,
                        height=self.fan_length-0.5 - self.inlet_diameter * 0.05,
                        position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                           "z",self.inlet_diameter * 0.05 +0.5),
                        color="orange")

    @Part
    def nozzle(self):
        return Cone(radius1=self.diameter_gas_generator / 2,
                    radius2=self.exit_diameter_gas_generator/2,
                    height=self.length_gas_generator,
                    position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                       "z", self.fan_length),
                    color="orange")

    @Part
    def bypass_cowling_1(self):
        return Cone(radius1=(self.inlet_diameter+0.2)/2,
                    radius2=self.max_diameter / 2,
                    height=self.loc_max_diameter,
                    position=rotate(self.position, "y", np.deg2rad(90)),
                    hidden=True)

    @Part
    def bypass_cowling_2(self):
        return Cone(radius1=self.max_diameter / 2,
                    radius2=self.exit_diameter / 2,
                    height=self.fan_length - self.loc_max_diameter,
                    position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                       "z", self.loc_max_diameter),
                    hidden=True)

    @Part
    def fused_bypass_outer(self):
        return FusedSolid(shape_in=self.bypass_cowling_1, tool=self.bypass_cowling_2,
                          color="Orange",
                          hidden=True)

    @Part
    def bypass_cowling_cut_1(self):
        return Cone(radius1=(self.inlet_diameter ) / 2,
                    radius2=(self.max_diameter-0.2) / 2,
                    height=self.loc_max_diameter,
                    position=rotate(self.position, "y", np.deg2rad(90)),
                    hidden=True)

    @Part
    def bypass_cowling_cut_2(self):
        return Cone(radius1=(self.max_diameter-0.2) / 2,
                    radius2=(self.exit_diameter-0.2) / 2,
                    height=self.fan_length - self.loc_max_diameter,
                    position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                       "z", self.loc_max_diameter),
                    hidden=True)

    @Part
    def fused_bypass_inner(self):
        return FusedSolid(shape_in=self.bypass_cowling_cut_1,
                          tool=self.bypass_cowling_cut_2,
                          color="Orange",
                          hidden=True)

    @Part
    def bypass(self):
        return SubtractedSolid(shape_in=self.fused_bypass_outer,
                               tool=self.fused_bypass_inner,
                               color="yellow",
                               transparency = 0.5)



if __name__ == '__main__':
    from parapy.gui import display
    obj1 = Propulsion_System(label="Prop")
    display(obj1)
