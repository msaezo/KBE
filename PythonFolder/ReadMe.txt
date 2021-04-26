This file exists so you can run this program from any computer. The following programs and plug-ins must
be in your computer:
    - ParaPy
    - PyCharm
    - Matlab
The following "pip install --" imports are also necessary:
    - numpy
    - matlab
The code runs matlab from python to run the aerodynamic, the following procedure must be followed to install
the python engine on matlab:
    - Open matlab and write in the terminal "matlabroot"
    - Copy the printed line (In my case -- C:\Program Files\MATLAB\R2020b --)
    - Open Command Prompt with administrator rights and change the directory to C:\Program Files\MATLAB\R2020b
    - then type cd extern\engines\python and press enter
    - then type python setup.py install
        - (In case it does not recognize python3.7)
        - copy the location of python.exe where python 3.7 is installed
        - then type C:\Users\juanpedro\AppData\Local\Programs\Python\Python37\python.exe setup.py install
    - you have completed the installation!