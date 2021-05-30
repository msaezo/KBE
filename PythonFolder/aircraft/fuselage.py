import numpy as np
from parapy.core import *
from parapy.geom import *
import aircraft.Import_Input as In


class Fuselage(GeomBase):
    # imported parameters from input file
    n_pax = Input(In.Number_of_passengers)
    width_aisle = Input(In.Width_aisle)
    width_seat = Input(In.Width_seat)
    width_armrest = Input(In.Width_armrest)
    clearance_seat = Input(In.Seat_clearance)
    length_cockpit = Input(In.Length_cockpit)
    length_tailcone_over_diam = Input(In.Length_tailcone_over_Diameter_Fuselage)
    length_nosecone_over_diam = Input(In.Length_nosecone_over_Diameter_Fuselage)
    length_tail_over_diam = Input(In.Length_Tail_over_Diameter_Fuselage)
    height_floor = Input(In.Height_floor)
    height_shoulder = Input(In.Height_shoulder)
    luggage_per_pax = Input(In.Luggage_per_pax)
    weight_cargo = Input(In.Cargo)
    kcc = Input(In.Kcc)  # cargo compartment factor

    fuselage_mass_fraction = Input(In.Fuselage_mass_fraction)
    empennage_mass_fraction = Input(In.Empennage_mass_fraction)
    fixed_equipment_mass_fraction = Input(In.Fixed_equipment_mass_fraction)
    fuselage_cg_loc = Input(In.Fuselage_cg_loc)
    empennage_cg_loc = Input(In.Empennage_cg_loc)
    fixed_equipment_cg_loc = Input(In.Fixed_equipment_cg_loc)

    # percentage of calculated fuselage diameter for each section
    fuselage_sections = Input([1, 10, 90, 100, 100, 100, 100, 100, 80, 10, 1])
    # z-shift of each fuselage section
    fuselage_sections_z = Input([-0.3, -0.3, -0.08, 0, 0, 0, 0, 0, 0.2, 0.62, 0.65])

    @Attribute
    def seats_abreast(self):
        seats = 0.45 * np.sqrt(self.n_pax)
        seatsmax = 9
        return min(np.ceil(seats), seatsmax)

    @Attribute
    def n_aisles(self):
        if self.seats_abreast < 7:
            n_aisle = 1
        else:
            n_aisle = 2
        return n_aisle

    @Attribute
    def n_rows(self):
        return np.ceil(self.n_pax / self.seats_abreast)

    @Attribute
    def length_cabin(self):
        if self.n_aisles == 1:
            k_cabin = 1.2
        elif self.n_aisles == 2:
            k_cabin = 1.35
        return self.n_pax / self.seats_abreast * k_cabin

    @Attribute
    def diameter_fuselage_inner(self):
        return self.seats_abreast * self.width_seat \
               + (self.seats_abreast + self.n_aisles + 1) * self.width_armrest \
               + self.n_aisles * self.width_aisle + 2 * self.clearance_seat

    @Attribute
    def diameter_fuselage_outer(self):
        return 1.045 * self.diameter_fuselage_inner + 0.084

    @Attribute
    def length_tailcone(self):
        return self.length_tailcone_over_diam * self.diameter_fuselage_outer

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
        return (self.diameter_fuselage_outer - self.diameter_fuselage_inner) / 2

    @Attribute
    def position_floor_upper(self):
        return - self.height_shoulder

    @Attribute
    def position_floor_lower(self):
        return self.position_floor_upper - self.height_floor

    # calculate the radius for each section
    @Attribute
    def section_radius_outer(self):
        return [i * self.diameter_fuselage_outer / 2 / 100. for i in self.fuselage_sections]

    # calculate the inner radius for each section
    # first and last are different as thats where the fuselage converges
    @Attribute
    def section_radius_inner(self):
        rad_0 = 0.01
        rad_1 = self.fuselage_sections[1] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_2 = self.fuselage_sections[2] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_3 = self.fuselage_sections[3] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_4 = self.fuselage_sections[4] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_5 = self.fuselage_sections[5] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_6 = self.fuselage_sections[6] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_7 = self.fuselage_sections[7] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_8 = self.fuselage_sections[8] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_9 = self.fuselage_sections[9] * self.diameter_fuselage_outer / 2 / 100 - self.thickness_fuselage
        rad_10 = 0.01
        return rad_0, rad_1, rad_2, rad_3, rad_4, rad_5, rad_6, rad_7, rad_8, rad_9, rad_10

    # Calculate length of every section that gets used to shift the profiles in x direction for the outer profiles
    @Attribute
    def section_length_outer(self):
        sec_0 = 0
        sec_1 = 0.001
        sec_2 = self.length_cockpit / self.length_fuselage
        sec_3 = self.length_nosecone / self.length_fuselage
        cylindrical_part = self.length_fuselage - self.length_nosecone - self.length_tailcone
        sec_4 = (self.length_nosecone + 1 / 4 * cylindrical_part) / self.length_fuselage
        sec_5 = (self.length_nosecone + 2 / 4 * cylindrical_part) / self.length_fuselage
        sec_6 = (self.length_nosecone + 3 / 4 * cylindrical_part) / self.length_fuselage
        sec_7 = (self.length_nosecone + 4 / 4 * cylindrical_part) / self.length_fuselage
        sec_8 = (self.length_fuselage - self.length_tail) / self.length_fuselage
        sec_9 = 0.996
        sec_10 = 1
        return sec_0, sec_1, sec_2, sec_3, sec_4, sec_5, sec_6, sec_7, sec_8, sec_9, sec_10

    # calculate length of every inner section used to shift the profiles (SECTION 0 AND SECTION 10 are different)
    @Attribute
    def section_length_inner(self):
        sec_0 = 0.0005
        sec_1 = 0.001
        sec_2 = self.length_cockpit / self.length_fuselage
        sec_3 = self.length_nosecone / self.length_fuselage
        cylindrical_part = self.length_fuselage - self.length_nosecone - self.length_tailcone
        sec_4 = (self.length_nosecone + 1 / 4 * cylindrical_part) / self.length_fuselage
        sec_5 = (self.length_nosecone + 2 / 4 * cylindrical_part) / self.length_fuselage
        sec_6 = (self.length_nosecone + 3 / 4 * cylindrical_part) / self.length_fuselage
        sec_7 = (self.length_nosecone + 4 / 4 * cylindrical_part) / self.length_fuselage
        sec_8 = (self.length_fuselage - self.length_tail) / self.length_fuselage
        sec_9 = 0.996
        sec_10 = 0.999
        return sec_0, sec_1, sec_2, sec_3, sec_4, sec_5, sec_6, sec_7, sec_8, sec_9, sec_10

    # @Attribute
    # def profiles(self):
    #     return self.profile_set  # collect the elements of the sequence profile_set

    # Find cg of fuselage group
    @Attribute
    def x_fuselage_cg(self):
        fuselage_sum = self.fuselage_cg_loc * self.fuselage_mass_fraction
        empennage_sum = self.empennage_cg_loc * self.empennage_mass_fraction
        fixed_equip_sum = self.fixed_equipment_cg_loc * self.fixed_equipment_mass_fraction
        mass_sum = self.fuselage_mass_fraction + self.empennage_mass_fraction + self.fixed_equipment_mass_fraction
        return self.length_fuselage * (fuselage_sum + empennage_sum + fixed_equip_sum) / mass_sum

    # creating fuselage sections and placing them at desired location
    @Part
    def outer_profile_set(self):
        return Circle(quantify=len(self.fuselage_sections), color="Black",
                      radius=self.section_radius_outer[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(
                          rotate(self.position, "y", np.deg2rad(90)),
                          "z", self.section_length_outer[child.index] * self.length_fuselage,
                          "-x", self.fuselage_sections_z[child.index] * self.diameter_fuselage_outer / 2))

    # creating fuselage sections and placing them at desired location
    @Part
    def inner_profile_set(self):
        return Circle(quantify=len(self.fuselage_sections), color="Black",
                      radius=self.section_radius_inner[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(
                          rotate(self.position, "y", np.deg2rad(90)),
                          "z", self.section_length_inner[child.index] * self.length_fuselage,
                          "-x", self.fuselage_sections_z[child.index] * self.diameter_fuselage_outer / 2))

    # create solid for outer profiles
    @Part
    def fuselage_lofted_solid_outer(self):
        return LoftedSolid(profiles=self.outer_profile_set,
                           color="yellow",
                           mesh_deflection=0.00001,
                           hidden=True)

    # create solid for inner profiles
    @Part
    def fuselage_lofted_solid_inner(self):
        return LoftedSolid(profiles=self.inner_profile_set,
                           color="red",
                           mesh_deflection=0.00001,
                           hidden=True)

    # subtracting inside from outside
    @Part
    def fuselage_subtracted(self):
        return SubtractedSolid(shape_in=self.fuselage_lofted_solid_outer,
                               tool=self.fuselage_lofted_solid_inner,
                               color="orange",
                               mesh_deflection=0.00005,
                               transparency=0.5)

    # create floor by placing a box at relevant location
    @Part
    def floor(self):
        return Box(length=self.diameter_fuselage_outer,
                   width=self.length_fuselage,
                   height=self.height_floor,
                   centered=True,
                   position=translate(self.position,
                                      "z", -self.height_shoulder - self.height_floor / 2,
                                      "x", self.length_fuselage / 2 - 0.1),
                   hidden=True)

    # create ceiling by placing a box at relevant location
    @Part
    def ceiling(self):
        return Box(length=self.diameter_fuselage_outer,
                   width=self.length_fuselage,
                   height=0.1,
                   centered=True,
                   position=translate(self.position,
                                      "z", -self.height_shoulder + 2.2,
                                      "x", self.length_fuselage / 2 + 0.1),
                   hidden=True)

    # cut floor box with fuselage
    @Part
    def floor_cut(self):
        return CommonSolid(shape_in=self.floor,
                           tool=self.fuselage_lofted_solid_inner,
                           hidden=False,
                           mesh_deflection=0.00001)

    # cut ceiling box with fuselage
    @Part
    def ceiling_cut(self):
        return CommonSolid(shape_in=self.ceiling,
                           tool=self.fuselage_lofted_solid_inner,
                           hidden=False,
                           mesh_deflection=0.00001,
                           transparency=0.5)

    @Attribute
    def k_cabin(self):
        if self.n_aisles == 1:
            k_cabin1 = 1.08
        elif self.n_aisles == 2:
            k_cabin1 = 1.17
        return k_cabin1

    @Attribute
    def n_rows_front(self):
        return int(np.floor((self.length_nosecone - self.length_cockpit) / (0.8 * self.k_cabin)))

    @Attribute
    def n_rows_middle(self):
        return int(np.floor((self.length_fuselage - self.length_nosecone - self.length_tailcone)
                                             / (0.9 * self.k_cabin)))

    @Attribute
    def n_rows_rear(self):
        return int((self.n_pax - self.seats_abreast * int(np.floor((self.length_fuselage
                                                                                     - self.length_nosecone
                                                                                     - self.length_tailcone)
                                                                                    / (0.9 * self.k_cabin)))
                                     - (self.seats_abreast - 2) * int(np.floor((self.length_nosecone
                                                                                - self.length_cockpit)
                                                                               / (0.8 * self.k_cabin))))
                                    / (self.seats_abreast - 2))

    # Place seats in front part (less seats abreast as fuselage is slimming down)
    # Uses seat row class
    @Part
    def seats_front(self):
        return SeatRow(width_aisle=self.width_aisle,
                       width_seat=self.width_seat,
                       width_armrest=self.width_armrest,
                       n_aisles=self.n_aisles,
                       height_shoulder=self.height_shoulder,
                       seats_abreast=self.seats_abreast - 2,
                       quantify=self.n_rows_front,
                       position=translate(self.position,
                                          'x', self.length_cockpit + child.index * 0.8 * self.k_cabin),
                       hidden=False)

    # Place seats in middle part until length is full
    # Uses seat row class
    @Part
    def seats_middle(self):
        return SeatRow(width_aisle=self.width_aisle,
                       width_seat=self.width_seat,
                       width_armrest=self.width_armrest,
                       seats_abreast=self.seats_abreast,
                       n_aisles=self.n_aisles,
                       height_shoulder=self.height_shoulder,
                       quantify=self.n_rows_middle,
                       position=translate(self.position,
                                          'x', self.length_nosecone + child.index * 0.9 * self.k_cabin),
                       hidden=False)

    # Place remaining seats in rear part with les seats abreast to not clash with fuselage
    # Uses seat row class
    @Part
    def seats_rear(self):
        return SeatRow(width_aisle=self.width_aisle,
                       width_seat=self.width_seat,
                       width_armrest=self.width_armrest,
                       n_aisles=self.n_aisles,
                       height_shoulder=self.height_shoulder,
                       seats_abreast=self.seats_abreast - 2,
                       quantify=self.n_rows_rear,
                       position=translate(self.position,
                                          'x',
                                          self.length_fuselage-self.length_tailcone + child.index * 0.8 * self.k_cabin),
                       hidden=False)


# class that creates a model of a seat with several boxes that cut away from each other and a nice fillet
class Seat(GeomBase):
    n_aisles = Input(Fuselage().n_aisles)
    width_seat = Input(Fuselage().width_seat)

    @Attribute
    def k_cabin(self):
        if self.n_aisles == 1:
            k_cabin1 = 1.08
        elif self.n_aisles == 2:
            k_cabin1 = 1.17
        return k_cabin1

    @Attribute
    def l_feet(self):
        if self.n_aisles == 1:
            l_feet1 = 0.48
        elif self.n_aisles == 2:
            l_feet1 = 0.57
        return l_feet1

    @Attribute
    def l_seat(self):
        if self.n_aisles == 1:
            l_seat1 = 0.98
        elif self.n_aisles == 2:
            l_seat1 = 1.07
        return l_seat1

    @Attribute
    def fillets(self):
        e1 = self.seatbox.top_face.edges
        return e1

    @Part
    def leg1(self):
        return Box(length=self.width_seat / 3,
                   width=self.k_cabin,
                   height=0.4,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.2,
                                      "x", self.k_cabin / 2.,
                                      'y', self.width_seat / 3),
                   hidden=True
                   )

    @Part
    def leg2(self):
        return Box(length=self.width_seat / 3,
                   width=self.k_cabin,
                   height=0.4,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.2,
                                      "x", self.k_cabin / 2.,
                                      'y', -self.width_seat / 3),
                   hidden=True
                   )

    @Part
    def seatbox(self):
        return Box(length=self.width_seat,
                   width=self.k_cabin,
                   height=1.3,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.65,
                                      "x", self.k_cabin / 2),
                   hidden=True
                   )

    @Part
    def feetspace(self):
        return Box(length=self.width_seat,
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
        return Box(length=self.width_seat,
                   width=self.l_seat,
                   height=0.8,
                   centered=True,
                   position=translate(self.position,
                                      "z", 0.5 + 0.4,
                                      "x", self.l_seat / 2),
                   hidden=True)

    @Part
    def seat_filleted(self):
        return FilletedSolid(self.seatbox, radius=0.2, edge_table=self.fillets,
                             hidden=True)

    @Part
    def seat(self):
        return SubtractedSolid(shape_in=self.seat_filleted,
                               tool=(self.feetspace, self.leg1, self.leg2, self.seatspace),
                               mesh_deflection=0.00005)


# class that creates one row of seats dependent on seats-abreast
# uses the seat class
class SeatRow(GeomBase):
    width_aisle = Input(Fuselage().width_aisle)
    width_seat = Input(Fuselage().width_seat)
    width_armrest = Input(Fuselage().width_armrest)
    seats_abreast = Input(Fuselage().seats_abreast)
    n_aisles = Input(Fuselage().n_aisles)
    height_shoulder = Input(Fuselage().height_shoulder)

    @Attribute
    def n_aisles(self):
        if self.seats_abreast < 7:
            n_aisle = 1
        else:
            n_aisle = 2
        return n_aisle

    # creates a list of position of each seat relative to the first on in its row, dependent on amopunt seats and aisles
    @Attribute
    def seat_spacing(self):
        if self.seats_abreast == 2:  # 1 seat, aisle, 1 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 3:  # 2 seats, aisle, 1 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 3 * self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 4:  # 2 seats, aisle, 2 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 3 * self.width_armrest + self.width_aisle,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 5:  # 3 seats, aisle, 2 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 2 * self.width_armrest,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle,
                        4 * self.width_seat + 5 * self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 6:  # 3 seats, aisle, 3 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 2 * self.width_armrest,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle,
                        4 * self.width_seat + 5 * self.width_armrest + self.width_aisle,
                        5 * self.width_seat + 6 * self.width_armrest + self.width_aisle])
        elif self.seats_abreast == 7:  # 2 seats, aisle, 3 seats, aisle, 2 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 3 * self.width_armrest + self.width_aisle,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle,
                        4 * self.width_seat + 5 * self.width_armrest + self.width_aisle,
                        5 * self.width_seat + 7 * self.width_armrest + 2 * self.width_aisle,
                        6 * self.width_seat + 8 * self.width_armrest + 2 * self.width_aisle])
        elif self.seats_abreast == 8:  # 2 seats, aisle, 4 seats, aisle, 2 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 3 * self.width_armrest + self.width_aisle,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle,
                        4 * self.width_seat + 5 * self.width_armrest + self.width_aisle,
                        5 * self.width_seat + 6 * self.width_armrest + self.width_aisle,
                        6 * self.width_seat + 8 * self.width_armrest + 2 * self.width_aisle,
                        7 * self.width_seat + 9 * self.width_armrest + 2 * self.width_aisle])
        elif self.seats_abreast == 9:  # 3 seats, aisle, 3 seats, aisle, 3 seats
            spacing = ([0,
                        1 * self.width_seat + 1 * self.width_armrest,
                        2 * self.width_seat + 2 * self.width_armrest,
                        3 * self.width_seat + 4 * self.width_armrest + self.width_aisle,
                        4 * self.width_seat + 5 * self.width_armrest + self.width_aisle,
                        5 * self.width_seat + 6 * self.width_armrest + self.width_aisle,
                        6 * self.width_seat + 8 * self.width_armrest + 2 * self.width_aisle,
                        7 * self.width_seat + 9 * self.width_armrest + 2 * self.width_aisle,
                        8 * self.width_seat + 10 * self.width_armrest + 2 * self.width_aisle])
        return spacing

    # dependen ton the number of seats and ailses determine the total with of a row (centre of seat to centre of seat)
    @Attribute
    def row_width(self):
        if self.seats_abreast == 2:
            width = 1 * self.width_seat + 2 * self.width_armrest + self.width_aisle
        elif self.seats_abreast == 3:
            width = 2 * self.width_seat + 3 * self.width_armrest + self.width_aisle
        elif self.seats_abreast == 4:
            width = 3 * self.width_seat + 4 * self.width_armrest + self.width_aisle
        elif self.seats_abreast == 5:
            width = 4 * self.width_seat + 5 * self.width_armrest + self.width_aisle
        elif self.seats_abreast == 6:
            width = 5 * self.width_seat + 6 * self.width_armrest + self.width_aisle
        elif self.seats_abreast == 7:
            width = 6 * self.width_seat + 8 * self.width_armrest + 2 * self.width_aisle
        elif self.seats_abreast == 8:
            width = 7 * self.width_seat + 9 * self.width_armrest + 2 * self.width_aisle
        elif self.seats_abreast == 9:
            width = 8 * self.width_seat + 10 * self.width_armrest + 2 * self.width_aisle
        return width

    # place every seat of a row
    @Part
    def seat_row(self):
        return Seat(n_aisles=self.n_aisles,
                    width_seat=self.width_seat,
                    quantify=int(self.seats_abreast),
                    position=translate(self.position,
                                       'y', self.row_width / 2 - self.seat_spacing[child.index],
                                       "z", -self.height_shoulder),
                    hidden=False)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Fuselage()
    display(obj)
