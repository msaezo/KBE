#International Standard Atmosphere Calculator
print "INTERNATIONAL STANDARD ATMOSPHERE CALCULATOR"
print "Introduce desired height in meters"

def print_menu():
    print "Units for height?"
    print "1. Height in meters"
    print "2. Height in feet"
    print "3. Height in Flight Levels"
    print "4. Exit" 
def print_menu2():
    print "Standard Atmosphere calculator or Altimeter?"
    print "1. Standard Atmosphere calculator"
    print "2. Altimeter"
    print "3. Geopotential to Geometric"
    print "4. Exit"
            
import math
from math import e
from math import log
alt = [0,11000,20000,32000,47000,51000,71000,84852,100000]
al = [-0.0065,0,0.001,0.0028,0,-0.0028,-0.002,0]
Press = [101325,22632,5474.9,868.02,110.91,66.939,3.9564,0.3734]
Temp = [288.15,216.65,216.65,228.65,270.65,214.65,186.35,186.35]
R = 287.00 
g = 9.80665
Re = 6371000
rho0=1.225
def calc(): #standard atmosphere altitude finder
    n=0
    for n in range(len(alt)):
        if hm<=alt[n+1]:
            break
        else:
            n = n+1
    #temperature pressure and density
    if al[n] == 0:
        Tf = Temp[n]
        Pf = Press[n]*(e)**((-g/(R*Tf))*(hm-alt[n]))
        rhof = Pf/(R*Tf)
    else:
        Tf = Temp[n]+al[n]*(hm-alt[n])
        Pf = Press[n]*(Tf/Temp[n])**(-g/(al[n]*R))
        rhof = Pf/(R*Tf)
        
    print "Temperature = ",Tf ,"K"
    print "Pressure = ",Pf ,"Pa"
    print "Desnsity = ", rhof ,"kg/m^3"
    print "Relative to Sea level:"
    print "Pressure = ", Pf/Press[0]*100,"%"
    print "Density = ", rhof/rho0*100,"%"
    
def altimeter(): #altimeter calculations
    Pf = float(raw_input("Pressure = "))
    n=0
    for n in range(len(Press)):
        if Pf>=Press[n+1]:
            break
        else:
            n = n+1
        #altitude
    if al[n] == 0:
        Tf = Temp[n]
        hm= -((R*Tf)/g)*(log((Pf/Press[n]),e))+alt[n]
        
    else:
        Tf = Temp[n]*(Pf/Press[n])**(-(al[n]*R)/g)
        hm= ((Tf - Temp[n])/al[n])+alt[n]    

    print_menu()
    choice = input("Enter your choice [1-4]: ")
    if choice==1:
        print "Height in meters has been selected"
        print "Height in meters = ", hm
                    
            
    elif choice==2:
        print "height in feet has been selected"
        hf = hm/0.3048
        print "Height in feet = ", hf
        
    elif choice==3:
        print "height in Flight Levels have been selected"
        hFL = hm/(100*0.3048)
        if 0<hFL<10:
            print "Height in Flight Levels = FL00",int(hFL)
            
        elif 10<=hFL<100:
            print "Height in Flight Levels = FL0",int(hFL) 
        else:
            print "Height in Flight Levels = FL",int(hFL)

    elif choice==4:
        exit   
while True:    
    print_menu2()
    choice = input("Enter your choice [1-4] ")
    if choice==1:
        print "Atmosphere Calculator Selected"

        print_menu()
        choice = input("Enter your choice [1-4]: ")

        if choice==1:
            print "Height in meters has been selected"
            hm = float(raw_input("height = "))
        
        elif choice==2:
            print "height in feet has been selected"
            h = float(raw_input("height = "))
            hm = h*0.3048
        elif choice==3:
            print "height in Flight Levels have been selected"
            h = float(raw_input("Write the numbers next to the FL = "))
            hm = h*100*0.3048

        elif choice==4:
            exit
        else:
            print "wrong choice given"
            exit 

        calc()

    elif choice==2:
        print "Altimeter Selected"
        altimeter()

    elif choice==3:
        hgeop = float (raw_input("Enter geopotential altitude ="))
        hgeom = ((Re)/(Re-hgeop))*hgeop
        print_menu()
        choice = input("Enter your choice [1-4]: ")
        if choice==1:
            print "Height in meters has been selected"
            print "Height in meters = ",hgeom
                        
                
        elif choice==2:
            print "height in feet has been selected"
            hf = hgeom/0.3048
            print "Height in feet = ",hf
            
        elif choice==3:
            print "height in Flight Levels have been selected"
            hFL = hgeom/(100*0.3048)
            if 0<hFL<10:
                print "Height in Flight Levels = FL00",int(hFL)
                
            elif 10<=hFL<100:
                print "Height in Flight Levels = FL0",int(hFL) 
            else:
                print "Height in Flight Levels = FL",int(hFL)

        elif choice==4:
            exit
    dummy = raw_input("Press enter")
