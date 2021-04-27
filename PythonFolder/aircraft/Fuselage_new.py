
import numpy as np



import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *
from aircraft.fuselage import Fuselage
from aircraft.energy import Tanks
from aircraft.energy import Energy

class old_fuselage(GeomBase):



    @Part
    def fuselage_lofted_solid_outer2(self):
        return LoftedSolid(profiles=[Fuselage().outer_profile_set[0],
                                     Fuselage().outer_profile_set[1],
                                     Fuselage().outer_profile_set[2],
                                     Fuselage().outer_profile_set[3],
                                     Fuselage().outer_profile_set[4],
                                     Fuselage().outer_profile_set[5],
                                     Fuselage().outer_profile_set[6],
                                     Fuselage().outer_profile_set[7],
                                     Fuselage().outer_profile_set[8],
                                     Fuselage().outer_profile_set[9],
                                     Fuselage().outer_profile_set[10]],
                           color="blue",
                           mesh_deflection=0.00001,
                           transparency=0.8)

class new_fuselage1(GeomBase):




    @Part
    def new_profile_first(self):
        return new_fuselage_profile(Fuselage_diameter=0.9*Fuselage().diameter_fuselage_outer,
                                    x_pos = Fuselage().section_length_outer[2]*Fuselage().length_fuselage,
                                    zzpos = 0.04*Fuselage().diameter_fuselage_outer,
                                    hidden=False)

    @Part
    def new_profile_set(self):
        return new_fuselage_profile(quantify=5,
                                    Fuselage_diameter=Fuselage().diameter_fuselage_outer,
                                    x_pos=Fuselage().section_length_outer[child.index+3]*Fuselage().length_fuselage,
                                    hidden=False)




class new_fuselage2(GeomBase):

    input_profile_set = Input([Fuselage().outer_profile_set[0],
                                     Fuselage().outer_profile_set[1],
                                     Fuselage().outer_profile_set[2],
                                     Fuselage().outer_profile_set[3],
                                     Fuselage().outer_profile_set[4],
                                     Fuselage().outer_profile_set[5],
                                     Fuselage().outer_profile_set[6],
                                     Fuselage().outer_profile_set[7],
                                     Fuselage().outer_profile_set[8],
                                     Fuselage().outer_profile_set[9],
                                     Fuselage().outer_profile_set[10]])

    @Part
    def fuselage_lofted_solid_outer(self):
        return LoftedSolid(profiles=self.input_profile_set,
                             color="green",
                             mesh_deflection=0.00001,
                             transparency=0.8)









class new_fuselage_profile(GeomBase):

    Fuselage_diameter= Input(Fuselage().diameter_fuselage_outer)
    x_pos = Input(0)


    @Attribute
    def delta_radius(self):
        return (self.Fuselage_diameter-Energy().diameter_tank_final*1.1)/2

    @Attribute
    def straight_length_midpoints(self):
        return np.sqrt(Tanks().z_pos**2 + Tanks().y_pos**2)

    @Attribute
    def straight_length_outer(self):
        return np.sqrt(self.straight_length_midpoints**2 - self.delta_radius**2)

    @Attribute
    def angle_1(self):
        return np.rad2deg(np.arctan(-Tanks().z_pos/Tanks().y_pos)+np.arctan(self.delta_radius/self.straight_length_outer))

    @Attribute
    def angle_2(self):
        return np.deg2rad(180-90 - self.angle_1)

    @Attribute
    def y_lower(self):
        return Tanks().y_pos + np.cos(self.angle_2)*Energy().diameter_tank_final/2*1.1

    @Attribute
    def y_upper(self):
        return np.cos(self.angle_2) * self.Fuselage_diameter/2

    @Attribute
    def z_lower(self):
        return Tanks().z_pos + np.sin(self.angle_2) * Energy().diameter_tank_final/2 * 1.1

    @Attribute
    def z_upper(self):
        return np.sin(self.angle_2) * self.Fuselage_diameter/2

    @Part
    def line_1(self):
        return LineSegment(start=Point(self.x_pos, self.y_lower , self.z_lower),
                           end=Point(self.x_pos, self.y_upper, self.z_upper),
                           hidden= False)

    @Part
    def line_2(self):
        return LineSegment(start=Point(self.x_pos, -self.y_lower , self.z_lower),
                           end=Point(self.x_pos, -self.y_upper, self.z_upper),
                           hidden= False)

    @Part
    def line_bottom1(self):
        return LineSegment(start=Point(self.x_pos, -Tanks().y_pos, Tanks().z_pos-Energy().diameter_tank_final/2 * 1.1),
                           end=Point(self.x_pos, 0, Tanks().z_pos-Energy().diameter_tank_final/2 * 1.1 ),
                           hidden= False)

    @Part
    def line_bottom2(self):
        return LineSegment(
            start=Point(self.x_pos, 0, Tanks().z_pos - Energy().diameter_tank_final / 2 * 1.1  ),
            end=Point(self.x_pos, Tanks().y_pos, Tanks().z_pos - Energy().diameter_tank_final / 2 * 1.1 ),
            hidden=False)

    @Part
    def circle_outer_fuselage(self):
        return Circle(radius=self.Fuselage_diameter/2,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z",self.x_pos),
                      hidden= True)

    @Part
    def circle_tank_1(self):
        return Circle(radius=Energy().diameter_tank_final * 1.1 / 2 ,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z",self.x_pos,
                                         "x",-Tanks().z_pos,
                                         "y",Tanks().y_pos),
                      hidden= True)

    @Part
    def circle_tank_2(self):
        return Circle(radius=Energy().diameter_tank_final*1.1 / 2,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z",self.x_pos,
                                         "x",-Tanks().z_pos,
                                         "y",-Tanks().y_pos),
                      hidden= True)

    @Part
    def splitted_fuselage(self):
        return SplitEdge(built_from=self.circle_outer_fuselage,
                         tool=[Point(self.x_pos, self.y_upper, self.z_upper), Point(self.x_pos, -self.y_upper, self.z_upper)],
                         hidden= False)

    @Part
    def splitted_tank_1(self):
        return SplitEdge(built_from=self.circle_tank_1,
                         tool=[Point(self.x_pos, self.y_lower, self.z_lower), Point(self.x_pos, Tanks().y_pos, Tanks().z_pos - Energy().diameter_tank_final / 2 * 1.1)],
                         hidden= False)

    @Part
    def splitted_tank_2(self):
        return SplitEdge(built_from=self.circle_tank_2,
                         tool=[Point(self.x_pos, -self.y_lower, self.z_lower),Point(self.x_pos, -Tanks().y_pos, Tanks().z_pos - Energy().diameter_tank_final / 2 * 1.1)],
                         hidden= False)

    @Part
    def composed_crv(self):
        return ComposedCurve(built_from=[self.line_bottom2,
                                         self.splitted_tank_1.edges[0],
                                         self.line_1,
                                         self.splitted_fuselage.edges[1],
                                         self.line_2,
                                         self.splitted_tank_2.edges[1],
                                         self.line_bottom1],
                             line_thickness=2,
                             hidden = False)


