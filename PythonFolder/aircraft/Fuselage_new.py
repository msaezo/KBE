
import numpy as np



import aircraft.Import_Input as I

from parapy.core import *
from parapy.geom import *
from aircraft.fuselage import Fuselage
from aircraft.energy import Tanks
from aircraft.energy import Energy

class new_fuselage(GeomBase):



    @Part
    def new_profile_first(self):
        return new_fuselage_profile(Fuselage_diameter=0.9*Fuselage().diameter_fuselage_outer,
                                    x_pos = Fuselage().section_length_outer[2]*Fuselage().length_fuselage)

    @Part
    def new_profile_set(self):
        return new_fuselage_profile(quantify=5,
                                    Fuselage_diameter=Fuselage().diameter_fuselage_outer,
                                    x_pos=Fuselage().section_length_outer[child.index+3]*Fuselage().length_fuselage)#,
                                    # position=translate(self.position,
                                    #                    "x", Fuselage().section_length_outer[child.index+3]))

    @Part
    def splittingrectangle(self):
        return RectangularFace(width=Fuselage().length_fuselage + 1,
                               length=10,
                               position=translate(rotate(self.position, "x", np.deg2rad(90)),
                                                  "x", Fuselage().length_fuselage / 2))

    @Part
    def filled_surface0(self):
        return Face(island=Fuselage().outer_profile_set[0])

    @Part
    def filled_surface1(self):
        return Face(island=Fuselage().outer_profile_set[1])

    @Part
    def filled_surface2(self):
        return Face(island=self.new_profile_first.composed_crv)

    @Part
    def filled_surface3(self):
        return Face(island=self.new_profile_set[0].composed_crv)

    @Part
    def filled_surface4(self):
        return Face(island=self.new_profile_set[1].composed_crv)

    @Part
    def filled_surface5(self):
        return Face(island=self.new_profile_set[2].composed_crv)

    @Part
    def filled_surface6(self):
        return Face(island=self.new_profile_set[3].composed_crv)

    @Part
    def filled_surface7(self):
        return Face(island=self.new_profile_set[4].composed_crv)

    @Part
    def filled_surface8(self):
        return Face(island=Fuselage().outer_profile_set[8])

    @Part
    def filled_surface9(self):
        return Face(island=Fuselage().outer_profile_set[9])

    @Part
    def filled_surface10(self):
        return Face(island=Fuselage().outer_profile_set[10])



    @Part
    def ref_line0(self):
        return IntersectedShapes(shape_in=self.filled_surface0,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line1(self):
        return IntersectedShapes(shape_in=self.filled_surface1,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line2(self):
        return IntersectedShapes(shape_in=self.filled_surface2,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line3(self):
        return IntersectedShapes(shape_in=self.filled_surface3,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line4(self):
        return IntersectedShapes(shape_in=self.filled_surface4,
                                 tool=self.splittingrectangle)
    @Part
    def ref_line5(self):
        return IntersectedShapes(shape_in=self.filled_surface5,
                      tool=self.splittingrectangle)

    @Part
    def ref_line6(self):
        return IntersectedShapes(shape_in=self.filled_surface6,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line7(self):
        return IntersectedShapes(shape_in=self.filled_surface7,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line8(self):
        return IntersectedShapes(shape_in=self.filled_surface8,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line9(self):
        return IntersectedShapes(shape_in=self.filled_surface9,
                                 tool=self.splittingrectangle)

    @Part
    def ref_line10(self):
        return IntersectedShapes(shape_in=self.filled_surface10,
                                 tool=self.splittingrectangle)

    @Part
    def path(self):
        return FittedCurve(points=[self.ref_line0.edges[0].vertices[0].point,
                                   self.ref_line1.edges[0].vertices[0].point,
                                   self.ref_line2.edges[0].vertices[0].point,
                                   self.ref_line3.edges[0].vertices[0].point,
                                   self.ref_line4.edges[0].vertices[0].point,
                                   self.ref_line5.edges[0].vertices[0].point,
                                   self.ref_line6.edges[0].vertices[0].point,
                                   self.ref_line7.edges[0].vertices[0].point,
                                   self.ref_line8.edges[0].vertices[0].point,
                                   self.ref_line9.edges[0].vertices[0].point,
                                   self.ref_line10.edges[0].vertices[0].point])



    @Part
    def splitcurve0(self):
        return SplitCurve(curve_in=Fuselage().outer_profile_set[0],
                          tool=self.ref_line0.edges[0].vertices[0].point)

    @Part
    def splitcurve1(self):
        return SplitCurve(curve_in=Fuselage().outer_profile_set[1],
                          tool=self.ref_line1.edges[0].vertices[0].point)

    @Part
    def splitcurve2(self):
        return SplitCurve(curve_in=self.new_profile_first.composed_crv,
                          tool=self.ref_line2.edges[0].vertices[0].point)

    @Part
    def splitcurve3(self):
        return SplitCurve(curve_in=self.new_profile_set[0].composed_crv,
                          tool=self.ref_line3.edges[0].vertices[0].point)


    @Part
    def fuselage_lofted_shell_outer1(self):
        return LoftedShell(profiles=[self.splitcurve0,
                                     self.splitcurve1,
                                     self.splitcurve2,
                                     self.splitcurve3],
                           color="green",
                           mesh_deflection=0.00001,
                           transparency = 0.8)

    @Part
    def fuselage_lofted_shell_outer2(self):
        return LoftedShell(profiles=[Fuselage().outer_profile_set[0],
                                     Fuselage().outer_profile_set[1],
                                     self.new_profile_first.composed_crv,
                                     self.new_profile_set[0].composed_crv,
                                     self.new_profile_set[1].composed_crv,
                                     self.new_profile_set[2].composed_crv,
                                     self.new_profile_set[3].composed_crv,
                                     self.new_profile_set[4].composed_crv,
                                     Fuselage().outer_profile_set[8],
                                     Fuselage().outer_profile_set[9],
                                     Fuselage().outer_profile_set[10]],
                           color="green",
                           mesh_deflection=0.00001,
                           transparency = 0.8)









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
        return LineSegment(start=Point(self.x_pos, self.y_lower, self.z_lower ),
                           end=Point(self.x_pos, self.y_upper, self.z_upper),
                           hidden= True)

    @Part
    def line_2(self):
        return LineSegment(start=Point(self.x_pos, -self.y_lower, self.z_lower),
                           end=Point(self.x_pos, -self.y_upper, self.z_upper),
                           hidden= True)

    @Part
    def line_bottom(self):
        return LineSegment(start=Point(self.x_pos, Tanks().y_pos, Tanks().z_pos-Energy().diameter_tank_final/2 * 1.1),
                           end=Point(self.x_pos, -Tanks().y_pos, Tanks().z_pos-Energy().diameter_tank_final/2 * 1.1),
                           hidden= True)

    @Part
    def circle_outer_fuselage(self):
        return Circle(radius=self.Fuselage_diameter/2,
                      position=translate(rotate(self.position, "y", np.deg2rad(90)),
                                         "z",self.x_pos),
                      hidden= True)

    @Part
    def circle_tank_1(self):
        return Circle(radius=Energy().diameter_tank_final * 1.1 / 2,
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
                         hidden= True)

    @Part
    def splitted_tank_1(self):
        return SplitEdge(built_from=self.circle_tank_1,
                         tool=[Point(self.x_pos, self.y_lower, self.z_lower), Point(self.x_pos, Tanks().y_pos, Tanks().z_pos - Energy().diameter_tank_final / 2 * 1.1)],
                         hidden= True)

    @Part
    def splitted_tank_2(self):
        return SplitEdge(built_from=self.circle_tank_2,
                         tool=[Point(self.x_pos, -self.y_lower, self.z_lower),Point(self.x_pos, -Tanks().y_pos, Tanks().z_pos - Energy().diameter_tank_final / 2 * 1.1)],
                         hidden= True)

    @Part
    def composed_crv(self):
        return ComposedCurve(built_from=[self.line_bottom,
                                         self.line_1,
                                         self.line_2,
                                         self.splitted_fuselage.edges[1],
                                         self.splitted_tank_1.edges[0],
                                         self.splitted_tank_2.edges[1]],
                             line_thickness=2,
                             hidden = False)


