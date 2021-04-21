import numpy as np
from parapy.core import *
from parapy.geom import *
import aircraft.Import_Input as I



class Fuselage(GeomBase):
    # imported parameters from input file
    n_pax = Input(I.Number_of_passengers)
    width_aisle = Input(I.Width_aisle)
    width_seat = Input(I.Width_seat)
    width_armrest = Input(I.Width_armrest)
    clearance_seat = Input(I.Seat_clearance)
    length_cockpit = Input(I.Length_cockpit)
    length_tailcone_over_diam = Input(I.Length_tailcone_over_Diameter_Fuselage)
    length_nosecone_over_diam = Input(I.Length_nosecone_over_Diameter_Fuselage)
    length_tail_over_diam = Input(I.Length_Tail_over_Diameter_Fuselage)
    height_floor = Input(I.Height_floor)
    height_shoulder = Input(I.Height_shoulder)
    luggage_per_pax = Input(I.Luggage_per_pax)
    weight_cargo = Input(I.Cargo)
    kcc = Input(I.Kcc) #cargo compartment factor

    fuselage_mass_fraction = Input(I.Fuselage_mass_fraction)
    empennage_mass_fraction = Input(I.Empennage_mass_fraction)
    fixed_equipment_mass_fraction = Input(I.Fixed_equipment_mass_fraction)
    fuselage_cg_loc = Input(I.Fuselage_cg_loc)
    empennage_cg_loc = Input(I.Empennage_cg_loc)
    fixed_equipment_cg_loc = Input(I.Fixed_equipment_cg_loc)

    density_luggage = Input(170)
    density_cargo = Input(160)
    kos = Input(0.74) # overhead storage factor
    area_os_lat = Input(0.2) # overhead storage area lat
    area_os_centre = Input(0.24)  # overhead storage area centre
    n_compartments_lat = Input(2)

    fuselage_sections = Input([1,10, 90, 100, 100, 100, 100, 100, 80, 10,1])
    fuselage_sections_z = Input([-0.3,-0.3, -0.08, 0, 0, 0, 0, 0, 0.2, 0.62, 0.65])

    @Attribute
    def seats_abreast(self):
        seats = 0.45*np.sqrt(self.n_pax)
        seatsmax = 9
        return min(np.ceil(seats),seatsmax)



    @Attribute
    def n_aisles(self):
        if self.seats_abreast <7:
            n_aisle = 1
        else:
            n_aisle = 2
        return n_aisle

    @Attribute
    def n_rows(self):
        return np.ceil(self.n_pax/self.seats_abreast)

    @Attribute
    def length_cabin(self):
        if self.n_aisles ==1:
            k_cabin = 1.08
        elif self.n_aisles ==2:
            k_cabin = 1.17
        return self.n_pax/self.seats_abreast * k_cabin

    @Attribute
    def diameter_fuselage_inner(self):
        return self.seats_abreast*self.width_seat \
               + (self.seats_abreast+self.n_aisles+1)*self.width_armrest \
               + self.n_aisles*self.width_aisle + 2*self.clearance_seat

    @Attribute
    def diameter_fuselage_outer(self):
        return 1.045*self.diameter_fuselage_inner + 0.084

    @Attribute
    def length_tailcone(self):
        return self.length_tailcone_over_diam*self.diameter_fuselage_outer

    @Attribute
    def length_nosecone(self):
        return self.length_nosecone_over_diam * self.diameter_fuselage_outer

    @Attribute
    def length_tail(self):
        return self.length_tail_over_diam * self.diameter_fuselage_outer

    @Attribute
    def length_fuselage(self):
        return self.length_cabin + self.length_cockpit + self.length_tail

    @Attribute
    def thickness_fuselage(self):
        return (self.diameter_fuselage_outer - self.diameter_fuselage_inner)/2

    @Attribute
    def position_floor_upper(self):
        return  - self.height_shoulder

    @Attribute
    def position_floor_lower(self):
        return self.position_floor_upper - self.height_floor

    @Attribute
    def angle_lower(self):
        return 2*np.rad2deg(np.arccos(1-(self.position_floor_lower)/(self.diameter_fuselage_inner/2)))

    @Attribute
    def area_available_cargo(self):
        return 0.5 * (self.diameter_fuselage_inner/2)**2 *(np.deg2rad(self.angle_lower) - np.sin(np.deg2rad(self.angle_lower)))

    @Attribute
    def volume_available_cargo(self):
        return self.area_available_cargo * self.kcc * self.length_cabin

    @Attribute
    def weight_luggage(self):
        return self.n_pax * self.luggage_per_pax

    @Attribute
    def volume_required_luggage(self):
        return self.weight_luggage/self.density_luggage

    @Attribute
    def volume_required_cargo(self):
        return self.weight_cargo / self.density_cargo

    @Attribute
    def volume_overhead_storage(self):
        if self.n_aisles ==1:
            n_compartments_centre = 0
        else:
            n_compartments_centre = 1
        return (self.n_compartments_lat*self.area_os_lat + n_compartments_centre*self.area_os_centre)*self.length_cabin*self.kos



    @Attribute
    def section_radius_outer(self):
        return [i * self.diameter_fuselage_outer/2 / 100. for i in self.fuselage_sections]

    @Attribute
    def section_radius_inner(self):
        radius_0 = 0.01
        radius_1 = self.fuselage_sections[1] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_2 = self.fuselage_sections[2] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_3 = self.fuselage_sections[3] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_4 = self.fuselage_sections[4] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_5 = self.fuselage_sections[5] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_6 = self.fuselage_sections[6] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_7 = self.fuselage_sections[7] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_8 = self.fuselage_sections[8] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_9 = self.fuselage_sections[9] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        radius_10 = 0.01
        return radius_0, radius_1, radius_2, radius_3, radius_4, radius_5, radius_6, radius_7, radius_8, radius_9, radius_10

    @Attribute
    def section_length_outer(self):
        section_0 = 0
        section_1 = 0.001
        section_2 = self.length_cockpit/self.length_fuselage
        section_3 = self.length_nosecone/self.length_fuselage
        cylindrical_part = self.length_fuselage-self.length_nosecone-self.length_tailcone
        section_4 = (self.length_nosecone + 1/4 *cylindrical_part) / self.length_fuselage
        section_5 = (self.length_nosecone + 2/4 *cylindrical_part) / self.length_fuselage
        section_6 = (self.length_nosecone + 3/4 * cylindrical_part) / self.length_fuselage
        section_7 = (self.length_nosecone + 4/4 * cylindrical_part) / self.length_fuselage
        section_8 = (self.length_fuselage-self.length_tail)/self.length_fuselage
        section_9 = 0.996
        section_10 = 1
        return section_0, section_1, section_2, section_3, section_4, section_5, section_6, section_7, section_8, section_9, section_10

    @Attribute
    def section_length_inner(self):
        section_0 = 0.0005
        section_1 = 0.001
        section_2 = self.length_cockpit / self.length_fuselage
        section_3 = self.length_nosecone / self.length_fuselage
        cylindrical_part = self.length_fuselage - self.length_nosecone - self.length_tailcone
        section_4 = (self.length_nosecone + 1 / 4 * cylindrical_part) / self.length_fuselage
        section_5 = (self.length_nosecone + 2 / 4 * cylindrical_part) / self.length_fuselage
        section_6 = (self.length_nosecone + 3 / 4 * cylindrical_part) / self.length_fuselage
        section_7 = (self.length_nosecone + 4 / 4 * cylindrical_part) / self.length_fuselage
        section_8 = (self.length_fuselage - self.length_tail) / self.length_fuselage
        section_9 = 0.996
        section_10 = 0.999
        return section_0, section_1, section_2, section_3, section_4, section_5, section_6, section_7, section_8, section_9, section_10

    @Attribute  # used by the superclass LoftedSolid. It could be removed if the @Part profile_set /
    # would be renamed "profiles" and LoftedSolid specified as superclass for Fuselage
    def profiles(self):
        return self.profile_set  # collect the elements of the sequence profile_set

    @Attribute
    def x_fuselage_cg(self):
        fuselage_sum = self.fuselage_cg_loc * self.fuselage_mass_fraction
        empennage_sum = self.empennage_cg_loc * self.empennage_mass_fraction
        fixed_equip_sum = self.fixed_equipment_cg_loc * self.fixed_equipment_mass_fraction
        mass_sum = self.fuselage_mass_fraction + self.empennage_mass_fraction + self.fixed_equipment_mass_fraction
        return self.length_fuselage * (fuselage_sum + empennage_sum + fixed_equip_sum) / (
            mass_sum)

    @Part
    def outer_profile_set(self):
        return Circle(quantify=len(self.fuselage_sections), color="Black",
                      radius=self.section_radius_outer[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(
                          rotate(self.position, "y", np.deg2rad(90)),
                          "z", self.section_length_outer[child.index]*self.length_fuselage,
                          "-x", self.fuselage_sections_z[child.index] * self.diameter_fuselage_outer/2))

    @Part
    def inner_profile_set(self):
        return Circle(quantify=len(self.fuselage_sections), color="Black",
                      radius=self.section_radius_inner[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(
                          rotate(self.position, "y", np.deg2rad(90)),
                          "z", self.section_length_inner[child.index] * self.length_fuselage,
                          "-x",self.fuselage_sections_z[child.index] * self.diameter_fuselage_outer / 2 ))

    @Part
    def fuselage_lofted_solid_outer(self):
        return LoftedSolid(profiles=self.outer_profile_set,
                           color="yellow",
                           mesh_deflection=0.00001,
                           hidden=True)

    @Part
    def fuselage_lofted_solid_inner(self):
        return LoftedSolid(profiles=self.inner_profile_set,
                           color="red",
                           mesh_deflection=0.00001,
                           hidden=True)

    @Part
    def fuselage_subtracted(self):
        return SubtractedSolid(shape_in=self.fuselage_lofted_solid_outer,
                               tool=self.fuselage_lofted_solid_inner,
                               color="orange",
                               mesh_deflection=0.00005,
                               transparency=0.5)

    @Part
    def floor(self):
        return Box(length=self.diameter_fuselage_outer,
                   width=self.length_fuselage,
                   height=self.height_floor,
                   centered=True,
                   position=translate(self.position,
                                      "z", -self.height_shoulder - self.height_floor/2,
                                      "x", self.length_fuselage/2-0.1),
                   hidden=True)

    @Part
    def ceiling(self):
        return Box(length=self.diameter_fuselage_outer,
                   width=self.length_fuselage,
                   height=0.1,
                   centered=True,
                   position=translate(self.position,
                                      "z", -self.height_shoulder  + 2.2,
                                      "x", self.length_fuselage / 2 + 0.1),
                   hidden=True)

    @Part
    def floor_cut(self):
        return CommonSolid(shape_in=self.floor,
                           tool=self.fuselage_lofted_solid_inner,
                           hidden = False,
                           mesh_deflection=0.00001)

    @Part
    def ceiling_cut(self):
        return CommonSolid(shape_in=self.ceiling,
                           tool=self.fuselage_lofted_solid_inner,
                           hidden=False,
                           mesh_deflection=0.00001,
                           transparency = 0.5)

    @Part
    def seats_front(self):
        return Seat_row(seats_abreast = self.seats_abreast-2,
                        quantify=int(np.floor((self.length_nosecone-self.length_cockpit)/(0.8*Seat().k_cabin))),
                        position=translate(self.position,
                                       'x', self.length_cockpit + child.index*0.8*Seat().k_cabin),
                        hidden=False)

    @Part
    def seats_middle(self):
        return Seat_row(seats_abreast=self.seats_abreast,
                        quantify=int(np.floor((self.length_fuselage - self.length_nosecone - self.length_tailcone) / (0.8 * Seat().k_cabin))),
                        position=translate(self.position,
                                           'x', self.length_nosecone  + child.index * 0.8 * Seat().k_cabin),
                        hidden=False)

    @Part
    def seats_rear(self):
        return Seat_row(seats_abreast=self.seats_abreast - 2,
                        quantify=int((self.n_pax
                                      - self.seats_abreast*int(np.floor((self.length_fuselage
                                                                         - self.length_nosecone
                                                                         - self.length_tailcone) / (0.8 * Seat().k_cabin)))
                                      - (self.seats_abreast-2)*int(np.floor((self.length_nosecone
                                                                             -self.length_cockpit)/(0.8*Seat().k_cabin))))
                                     /(self.seats_abreast - 2)),
                        position=translate(self.position,
                                           'x', self.length_fuselage - self.length_tailcone +child.index * 0.8 * Seat().k_cabin),
                        hidden=False)




class Seat(GeomBase):

    @Attribute
    def k_cabin(self):
        if Fuselage().n_aisles ==1:
            k_cabin1 = 1.08
        elif Fuselage().n_aisles ==2:
            k_cabin1 = 1.17
        return k_cabin1

    @Attribute
    def l_feet(self):
        if Fuselage().n_aisles == 1:
            l_feet1 = 0.48
        elif Fuselage().n_aisles == 2:
            l_feet1 = 0.57
        return l_feet1

    @Attribute
    def l_seat(self):
        if Fuselage().n_aisles == 1:
            l_seat1 = 0.98
        elif Fuselage().n_aisles == 2:
            l_seat1 = 1.07
        return l_seat1

    @Attribute
    def fillets(self):
        e1= self.seatbox.top_face.edges
        return e1

    @Part
    def leg1(self):
        return Box(length=Fuselage().width_seat/3,
                   width=self.k_cabin,
                   height=0.4,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.2,
                                      "x", self.k_cabin / 2.,
                                      'y',Fuselage().width_seat/3),
                   hidden=True
                   )

    @Part
    def leg2(self):
        return Box(length=Fuselage().width_seat / 3,
                   width=self.k_cabin,
                   height=0.4,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.2,
                                      "x", self.k_cabin / 2.,
                                      'y', -Fuselage().width_seat / 3),
                   hidden=True
                   )

    @Part
    def seatbox(self):
        return Box(length=Fuselage().width_seat,
                   width=self.k_cabin,
                   height=1.3,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.65,
                                      "x",self.k_cabin/2),
                   hidden=True
                   )

    @Part
    def feetspace(self):
        return Box(length=Fuselage().width_seat,
                   width=self.l_feet,
                   height=0.5,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.25,
                                      "x", self.l_feet / 2),
                   hidden=True
                   )

    @Part
    def seatspace(self):
        return Box(length=Fuselage().width_seat,
                   width=self.l_seat,
                   height=0.8,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.5+0.4,
                                      "x",self.l_seat/2),
                   hidden=True)

    @Part
    def seat_filleted(self):
        return FilletedSolid(self.seatbox, radius=0.2, edge_table=self.fillets,
                               hidden=True)


    @Part
    def seat(self):
        return SubtractedSolid(shape_in=self.seat_filleted,
                               tool=(self.feetspace,self.leg1, self.leg2, self.seatspace),
                               mesh_deflection=0.00005)

class Seat_row(GeomBase):
    width_aisle = Input(I.Width_aisle)
    width_seat = Input(I.Width_seat)
    width_armrest = Input(I.Width_armrest)

    seats_abreast = Input()

    @Attribute
    def n_aisles(self):
        if self.seats_abreast <7:
            n_aisle = 1
        else:
            n_aisle = 2
        return n_aisle

    @Attribute
    def seat_spacing(self):
        if self.seats_abreast==3:#2 seats, aisle, 1 seats
            spacing = ([0,
                        1*self.width_seat + 1*self.width_armrest,
                        2*self.width_seat + 3*self.width_armrest + self.width_aisle ])
        elif self.seats_abreast==4:#2 seats, aisle, 2 seats
            spacing = ([0,
                        1*self.width_seat + 1*self.width_armrest,
                        2*self.width_seat + 3*self.width_armrest + self.width_aisle,
                        3*self.width_seat + 4*self.width_armrest + self.width_aisle ])
        elif self.seats_abreast ==5: #3 seats, aisle, 2 seats
            spacing = ([0,
                        1*self.width_seat + 1*self.width_armrest,
                        2*self.width_seat + 2*self.width_armrest,
                        3*self.width_seat + 4*self.width_armrest + self.width_aisle,
                        4*self.width_seat + 5*self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 6:#3 seats, aisle, 3 seats
            spacing = ([0,
                        1*self.width_seat + 1*self.width_armrest,
                        2*self.width_seat + 2*self.width_armrest,
                        3*self.width_seat + 4*self.width_armrest + self.width_aisle,
                        4*self.width_seat + 5*self.width_armrest + self.width_aisle,
                        5*self.width_seat + 6*self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 7:#2 seats, aisle, 3 seats, aisle, 2 seats
            spacing = ([0,
                        1*self.width_seat + 1*self.width_armrest,
                        2*self.width_seat + 3*self.width_armrest + self.width_aisle,
                        3*self.width_seat + 4*self.width_armrest + self.width_aisle,
                        4*self.width_seat + 5*self.width_armrest + self.width_aisle,
                        5*self.width_seat + 7*self.width_armrest + 2*self.width_aisle,
                        6*self.width_seat + 8*self.width_armrest + 2*self.width_aisle])
        elif self.seats_abreast == 8:#2 seats, aisle, 4 seats, aisle, 2 seats
            spacing = ([0,
                        1*self.width_seat + 1*self.width_armrest,
                        2*self.width_seat + 3*self.width_armrest + self.width_aisle,
                        3*self.width_seat + 4*self.width_armrest + self.width_aisle,
                        4*self.width_seat + 5*self.width_armrest + self.width_aisle,
                        5*self.width_seat + 6*self.width_armrest + self.width_aisle,
                        6*self.width_seat + 8*self.width_armrest + 2*self.width_aisle,
                        7*self.width_seat + 9*self.width_armrest + 2*self.width_aisle])
        elif self.seats_abreast == 9:  # 3 seats, aisle, 3 seats, aisle, 3 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 2 * self.width_armrest,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle,
                        4 * self.width_seat + 5 * self.width_armrest + self.width_aisle,
                        5 * self.width_seat + 6 * self.width_armrest + self.width_aisle,
                        6 * self.width_seat + 8 * self.width_armrest + 2 * self.width_aisle,
                        7 * self.width_seat + 9 * self.width_armrest + 2 * self.width_aisle,
                        8 * self.width_seat + 10* self.width_armrest + 2 * self.width_aisle])
        return spacing

    @Attribute
    def row_width(self):
        if self.seats_abreast == 3:
            width = 2*self.width_seat + 3*self.width_armrest+ self.width_aisle
        elif self.seats_abreast == 4:
            width = 3*self.width_seat + 4*self.width_armrest+ self.width_aisle
        elif self.seats_abreast == 5:
            width = 4*self.width_seat + 5*self.width_armrest+ self.width_aisle
        elif self.seats_abreast == 6:
            width = 5*self.width_seat + 6*self.width_armrest+ self.width_aisle
        elif self.seats_abreast == 7:
            width = 6*self.width_seat + 8*self.width_armrest+ 2*self.width_aisle
        elif self.seats_abreast == 8:
            width = 7*self.width_seat + 9*self.width_armrest+ 2*self.width_aisle
        elif self.seats_abreast == 9:
            width = 8 * self.width_seat + 10 * self.width_armrest + 2 * self.width_aisle
        return width

    @Part
    def seat_row(self):
        return Seat(quantify=int(self.seats_abreast),
                    position=translate(self.position,
                                       'y', self.row_width/2 - self.seat_spacing[child.index],
                                       "z", -Fuselage().height_shoulder),
                    hidden=False)









if __name__ == '__main__':
    from parapy.gui import display
    obj = Fuselage()
    display(obj)



















