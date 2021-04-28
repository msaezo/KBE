This file exists so you can run this program from any computer. The following programs and plug-ins must
be in your computer:
    - ParaPy
    - PyCharm
    - Matlab
The following "pip install --" imports are also necessary:
    - numpy
    - matlab
The code runs matlab from python to run the aerodynamic analysis with Q3D, the following procedure must be followed to install
the python engine on matlab:
    - Open matlab and write in the terminal "matlabroot"
    - Copy the printed line (In my case -- C:\Program Files\MATLAB\R2020b --)
    - Open Command Prompt with administrator rights and change the directory to C:\Program Files\MATLAB\R2020b
    - then type cd extern\engines\python and press enter
    - then type python setup.py install
        - (In case it does not recognize python version 3.7)
        - copy the location of python.exe where python 3.7 is installed
        - then type C:\Users\juanpedro\AppData\Local\Programs\Python\Python37\python.exe setup.py install
    - you have completed the installation!

To run your files:
Once all the packages are installed you can use aircraft\KBE_Input.xls to enter the chosen configuration details in column C. Do not forget to safe before running!
After that you should be able to open the AircraftGeometry.py file and run it.
Once done some potential warnings might pop up depending on the chosen configuration and the ParaPy GUI will open with the final result.

To check the results:
One can observe all rsults in the ParaPy GUI
Alternatively all calculated atteributes are also printed out in output.txt
And one can generate a .stp file of the configuration in the ParaPy GUI. 

Recommended inputs:
This program is also designed to be used with realistic inputs for short to medium range passenger aircraft.
As an example we also have included the ReferenceAircraft_input.xlxs file in which one can copy a several parameters of existing 
aircraft to the aircraft\KBE_Input.xls. 
Please note that this does not change all input parameters. For example the relative c.g. locations and tail volumes remain unaffected and
might need to be adapted manually for a realistic output.