import numpy as np
import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *


from aircraft.fuselage import Fuselage
from aircraft.wing import Wing
from aircraft.runQ3D import Q3D




class Energy(GeomBase):

    range = Input(I.range)
    lift_coefficient = Input(Q3D().CLdes)
    drag_coefficient = Input(Q3D().CDdes)
    surface = Input(I.Wing_area)
    density = Input(Q3D().airDensity)
    velocity = Input(Q3D().airSpeed)
    efficiency = Input(I.total_efficiency)
    energy_density = Input(I.energy_density)
    n_tanks = Input(3)


    @Attribute
    def drag(self):
        return 0.5*self.density*self.velocity**2 * self.lift_coefficient/14 * self.surface

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
        return (Fuselage().length_fuselage-Fuselage().length_cockpit-Fuselage().length_tailcone)

    @Attribute
    def diameter_tank(self):
        coeff = [1, 0.75*self.length_tank, -0.75*self.vol_needed/self.n_tanks *1/np.pi ]
        roots = np.roots(coeff)
        roots1 = roots[0]
        roots2 = roots[1]
        print (roots1)
        print (roots2)
        if roots1>0:
            radius = roots1
        else :
            radius = roots2
        return radius*2

    @Part
    def cylinder(self):
        return Cylinder(radius=self.diameter_tank/2,
                       height=self.length_tank,
                       centered=True,
                       position=translate(
                           rotate(self.position, "y", np.deg2rad(90)),
                           "z", self.length_tank/2 + self.diameter_tank/2),
                       mesh_deflection=0.0001,
                       hidden=True)

    @Part
    def sphere1(self):
        return Sphere(radius=self.diameter_tank/2,
                      position=translate(self.position,
                          "x", self.diameter_tank/2),
                      hidden=True)
    @Part
    def sphere2(self):
        return Sphere(radius=self.diameter_tank / 2,
                      position=translate(self.position,
                          "x", self.length_tank + self.diameter_tank / 2),
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

class Tanks(GeomBase):

    @Part
    def tank(self):
        return Energy(quantify=Energy().n_tanks,
                      position=translate(self.position,
                                         'x', Fuselage().length_cockpit,
                                         'y', (1.1*Energy().diameter_tank*(Energy().n_tanks-1))/2 - 1.1*Energy().diameter_tank*child.index ,
                                         'z', Fuselage().position_floor_lower -1.1*Energy().diameter_tank/2),
                    hidden=False)