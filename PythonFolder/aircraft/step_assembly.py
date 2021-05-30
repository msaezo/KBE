from parapy.core import Part
class STEP_Assembly(Geombase):

     label = "bigger box"

    @Part
    def child(self):
        return Box(pass_down="width, length",
                   height=self.height * 0.5,
                   color="blue",
                   label="smaller box")

    @Part
    def writer(self):
        return STEPWriter(trees=[self],
                          filename="path/to/your/file.stp")

assy = Assembly(1, 2, 3)
assy.writer.write()
