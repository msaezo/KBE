import xlrd
from parapy.core import *

workbook = xlrd.open_workbook('aircraft\KBE_Input.xls')
worksheet = workbook.sheet_by_name('Input')

# Fuselage parameters
for i in range(2, 16):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value

    exec(Name + "=Value")

# Wing parameters
for i in range(18, 23):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value

    exec(Name + "=Value")

# Engine parameters
for i in range(25, 30):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value

    exec(Name + "=Value")

# CG parameters
for i in range(32, 41):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value
    exec(Name + "=Value")
for i in range(42, 50):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value
    exec(Name + "=Value")

# Landing gear parameters
for i in range(52, 55):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value
    exec(Name + "=Value")

# Empennage parameters
for i in range(57, 66):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value
    exec(Name + "=Value")

# Flight parameters
for i in range(68, 73):
    Name = worksheet.cell(i, 1).value
    Value = worksheet.cell(i, 2).value
    exec(Name + "=Value")
