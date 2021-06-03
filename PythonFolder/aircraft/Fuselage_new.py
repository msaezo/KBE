import numpy as np

import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *
from aircraft.fuselage import Fuselage
from aircraft.energy import Tanks
from aircraft.energy import Energy1


class NewFuselage1(GeomBase):
    diameter_fuselage_outer = Input(Fuselage().diameter_fuselage_outer)
    section_length_outer = Input(Fuselage().section_length_outer)
    length_fuselage = Input(Fuselage().length_fuselage)
    diameter_tank_final = Input(Energy1().diameter_tank_final)
    y_pos = Input(Tanks().y_pos)
    z_pos = Input(Tanks().z_pos)

    # creates the frofile of the first section
    # separated as it is smaller then the rest due to the taper of the nosecone
    # hardcoded as 90% of normal fuselage diameter
    @Part
    def new_profile_first(self):
        return NewFuselageProfile(fuselage_diameter=0.9 * self.diameter_fuselage_outer,
                                  x_pos=self.section_length_outer[2] * self.length_fuselage,
                                  y_pos=self.y_pos,
                                  z_pos=self.z_pos,  # 0.04*self.diameter_fuselage_outer,
                                  diameter_tank_final=self.diameter_tank_final,
                                  hidden=False)

    # creates profiles set for the nef fuselage for the remaining section ins the 'cylindrical' part of the fuselage
    @Part
    def new_profile_set(self):
        return NewFuselageProfile(quantify=5,
                                  fuselage_diameter=self.diameter_fuselage_outer,
                                  x_pos=self.section_length_outer[child.index + 3] * self.length_fuselage,
                                  y_pos=self.y_pos,
                                  z_pos=self.z_pos,
                                  diameter_tank_final=self.diameter_tank_final,
                                  hidden=False)


class NewFuselage2(GeomBase):
    # Class the creates the new fuselage, inherits this set from Aircraft Geometry depending
    # on if the tanks fit or not in the original fuselage
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

    # created the new fuselage part as a lofted solid
    @Part
    def fuselage_lofted_solid_outer(self):
        return LoftedSolid(profiles=self.input_profile_set,
                           color="green",
                           mesh_deflection=0.00001,
                           transparency=0.5)


# creates new profile sections that fit around the fuselage and the tanks
# WARNING: this class includes a lot of trigonometry and might be tricky to understand without a drawing
class NewFuselageProfile(GeomBase):
    fuselage_diameter = Input(Fuselage().diameter_fuselage_outer)
    diameter_tank_final = Input(Energy1().diameter_tank_final)
    z_pos = Input(Tanks().z_pos)
    y_pos = Input(Tanks().y_pos)
    x_pos = Input(0)

    # First it calculated the difference in radii between the fuselage and the tank times 1.1
    # (need some space around the tanks for structures)
    @Attribute
    def delta_radius(self):
        return (self.fuselage_diameter - self.diameter_tank_final * 1.1) / 2

    # Calculate distance between midpoints of fuselage and thos eofmost outboard tanks
    @Attribute
    def straight_length_midpoints(self):
        return np.sqrt(self.z_pos ** 2 + self.y_pos ** 2)

    # calculates the length of the straight connection we need to make between the fuselage and the tank shell
    @Attribute
    def straight_length_outer(self):
        return np.sqrt(abs(self.straight_length_midpoints ** 2 - self.delta_radius ** 2))

    # calculate the value of two angles that will be used to split the circles later on, final value in radians
    @Attribute
    def angle_1(self):
        return np.rad2deg(
            np.arctan(-self.z_pos / self.y_pos) + np.arctan(self.delta_radius / self.straight_length_outer))

    @Attribute
    def angle_2(self):
        return np.deg2rad(180 - 90 - self.angle_1)

    # y-position of where the circle of the tank fill be split and a tangent line originates
    @Attribute
    def y_lower(self):
        return self.y_pos + np.cos(self.angle_2) * self.diameter_tank_final / 2 * 1.1

    # y-position of where the circle of the fuselage fill be split and a tangent line originates
    @Attribute
    def y_upper(self):
        return np.cos(self.angle_2) * self.fuselage_diameter / 2

    # z-position of where the circle of the tank fill be split and a tangent line originates
    @Attribute
    def z_lower(self):
        return self.z_pos + np.sin(self.angle_2) * self.diameter_tank_final / 2 * 1.1

    # z-position of where the circle of the fuselage fill be split and a tangent line originates
    @Attribute
    def z_upper(self):
        return np.sin(self.angle_2) * self.fuselage_diameter / 2

    # calculate the final angle of how much of the original fuselage circle will remain
    @Attribute
    def fuselage_angle(self):
        return np.pi - 2 * self.angle_2

    # calculate the final angle of how much of the original tank circle will remain
    @Attribute
    def tank_angle(self):
        return np.pi/2 + self.angle_2

    # calculate the profile length that the circular part of the fuselage encompasses
    @Attribute
    def profile_length_fuselage(self):
        return np.pi*self.fuselage_diameter * self.fuselage_angle/(2*np.pi)

    # calculate the profile length that the circular part of one tank encompasses
    @Attribute
    def profile_length_tank(self):
        return np.pi * self.diameter_tank_final * 1.1 * self.tank_angle / (2*np.pi)

    # calculate the total circumference of the new fuselage
    @Attribute
    def circum_new_fuselage(self):
        return self.profile_length_fuselage + 2*self.profile_length_tank+2*self.y_pos+2*self.straight_length_outer

    # calculate an 'equivalent diameter' for the new fuselage -> will be used for updated drag calculations
    @Attribute
    def fus_diam_new(self):
        return self.circum_new_fuselage/np.pi

    # create all the lines and circles to create the new fuselage profile
    # bottom line is split in two so we can use the symmetry line on the bottom as a starting point for
    # the lofting operation. Otherwise the new fuselage gets quite funky shapes as it simply takes a staring and an end
    # point on a profiles and distributes the surface equidistantly around it. so transferring from a circle to a new
    # shape such as the new fuselage would give asymmetrical results with weird bumps and folds around certain corners

    @Part
    def line_1(self):
        return LineSegment(start=Point(self.x_pos, self.y_lower, self.z_lower),
                           end=Point(self.x_pos, self.y_upper, self.z_upper),
                           hidden=False)

    @Part
    def line_2(self):
        return LineSegment(start=Point(self.x_pos, -self.y_lower, self.z_lower),
                           end=Point(self.x_pos, -self.y_upper, self.z_upper),
                           hidden=False)

    @Part
    def line_bottom1(self):
        return LineSegment(start=Point(self.x_pos, -self.y_pos, self.z_pos - self.diameter_tank_final / 2 * 1.1),
                           end=Point(self.x_pos, 0, self.z_pos - self.diameter_tank_final / 2 * 1.1),
                           hidden=False)

    @Part
    def line_bottom2(self):
        return LineSegment(
            start=Point(self.x_pos, 0, self.z_pos - self.diameter_tank_final / 2 * 1.1),
            end=Point(self.x_pos, self.y_pos, self.z_pos - self.diameter_tank_final / 2 * 1.1),
            hidden=False)

    @Part
    def circle_outer_fuselage(self):
        return Circle(radius=self.fuselage_diameter / 2,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z", self.x_pos),
                      hidden=True)

    @Part
    def circle_tank_1(self):
        return Circle(radius=self.diameter_tank_final * 1.1 / 2,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z", self.x_pos,
                                         "x", -self.z_pos,
                                         "y", self.y_pos),
                      hidden=True)

    @Part
    def circle_tank_2(self):
        return Circle(radius=self.diameter_tank_final * 1.1 / 2,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z", self.x_pos,
                                         "x", -self.z_pos,
                                         "y", -self.y_pos),
                      hidden=True)

    # splitting the fuselage circle with the respective points
    @Part
    def splitted_fuselage(self):
        return SplitEdge(built_from=self.circle_outer_fuselage,
                         tool=[Point(self.x_pos, self.y_upper, self.z_upper),
                               Point(self.x_pos, -self.y_upper, self.z_upper)],
                         hidden=False)

    # splitting the tank circles with the respective points
    @Part
    def splitted_tank_1(self):
        return SplitEdge(built_from=self.circle_tank_1,
                         tool=[Point(self.x_pos, self.y_lower, self.z_lower),
                               Point(self.x_pos, self.y_pos, self.z_pos - self.diameter_tank_final / 2 * 1.1)],
                         hidden=True)

    @Part
    def splitted_tank_2(self):
        return SplitEdge(built_from=self.circle_tank_2,
                         tool=[Point(self.x_pos, -self.y_lower, self.z_lower),
                               Point(self.x_pos, -self.y_pos, self.z_pos - self.diameter_tank_final / 2 * 1.1)],
                         hidden=True)

    # create a composed curve of all the segments, starting from the the bottom in the symmetry plane
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
                             hidden=False)
