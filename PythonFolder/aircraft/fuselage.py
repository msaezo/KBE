import numpy as np
from parapy.core import *
from parapy.geom import *
import Import_Input as I



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

    density_luggage = Input(170)
    density_cargo = Input(160)
    kos = Input(0.74) # overhead storage factor
    area_os_lat = Input(0.2) # overhead storage area lat
    area_os_centre = Input(0.24)  # overhead storage area centre
    n_compartments_lat = Input(2)

    fuselage_sections = Input([1,10, 80, 100, 100, 100, 100, 100, 80, 10,1])
    fuselage_sections_z = Input([-0.3,-0.3, -0.10, 0, 0, 0, 0, 0, 0.21, 0.62, 0.65])

    @Attribute
    def seats_abreast(self):
        seats = 0.45*np.sqrt(self.n_pax)
        return np.ceil(seats)

    @Attribute
    def n_aisles(self):
        if self.seats_abreast <7:
            n_aisle = 1
        else:
            n_aisle = 2
        return n_aisle

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
        return (self.diameter_fuselage_inner/2)/2 - self.height_shoulder

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
    def section_length(self):
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

    @Attribute  # used by the superclass LoftedSolid. It could be removed if the @Part profile_set /
    # would be renamed "profiles" and LoftedSolid specified as superclass for Fuselage
    def profiles(self):
        return self.profile_set  # collect the elements of the sequence profile_set

    @Part
    def outer_profile_set(self):
        return Circle(quantify=len(self.fuselage_sections), color="Black",
                      radius=self.section_radius_outer[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(
                          rotate(self.position, "y", np.deg2rad(90)),
                          "z", self.section_length[child.index]*self.length_fuselage,
                          "-x", self.fuselage_sections_z[child.index] * self.diameter_fuselage_outer/2))

    @Part
    def inner_profile_set(self):
        return Circle(quantify=len(self.fuselage_sections), color="Black",
                      radius=self.section_radius_inner[child.index],
                      # fuselage along the X axis, nose in XOY
                      position=translate(
                          rotate(self.position, "y", np.deg2rad(90)),
                          "z", self.section_length[child.index] * self.length_fuselage,
                          "-x",self.fuselage_sections_z[child.index] * self.diameter_fuselage_outer / 2 ))

    @Part  # This part is redundant as far as LoftedSolid is a Fuselage's superclass.
    def fuselage_lofted_shell_outer(self):
        return LoftedShell(profiles=self.outer_profile_set,
                           color="red",
                           mesh_deflection=0.00001,
                           hidden=False)

    @Part  # This part is redundant as far as LoftedSolid is a Fuselage's superclass.
    def fuselage_lofted_shell_inner(self):
        return LoftedShell(profiles=self.inner_profile_set,
                           color="green",
                           mesh_deflection=0.00001,
                           hidden=False)

if __name__ == '__main__':
    from parapy.gui import display
    obj = Fuselage()
    display(obj)



















