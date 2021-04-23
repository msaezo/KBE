import numpy as np
import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *


from aircraft.fuselage import Fuselage
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

class Energy(GeomBase):

    range            = Input(Tanks().range)
    lift_coefficient = Input(Tanks().lift_coefficient)
    drag_coefficient = Input(Tanks().drag_coefficient)
    surface          = Input(Tanks().surface)
    density          = Input(Tanks().density)
    velocity         = Input(Tanks().velocity)
    efficiency       = Input(Tanks().efficiency)
    energy_density   = Input(Tanks().energy_density)
    n_tanks          = Input([1,2,3,4])


    @Attribute
    def drag(self):
        if np.isnan(self.drag_coefficient) == True:
            cd = self.lift_coefficient/20
        else:
            cd = self.drag_coefficient
        return 0.5*self.density*self.velocity**2 * cd * self.surface

    @Attribute
    def work(self):
        return self.drag*self.range*1000

    @Attribute
    def energy(self):
        return self.work /self.efficiency

    @Attribute
    def vol_needed(self):
        return self.energy/(self.energy_density*10**6)

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

