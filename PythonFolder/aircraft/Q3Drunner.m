function [CLdes,CDdes] = Q3Drunner(span,root_chord,tip_chord,twist_chord,twist_tip,dihedral,sweep,airSpeed,airDensity,altitude,Reynolds,Mach,AoA,Cl)



% Wing planform geometry 
%                x    y                z                chord(m)       twist angle (deg) 
AC.Wing.Geom = [0     0                0                root_chord         twist_chord;
                span/2*tand(sweep)  span/2   span/2*sind(dihedral)     tip_chord          twist_tip];
            
% Wing incidence angle (degree)
AC.Wing.inc  = 0;   

% Airfoil coefficients input matrix
%                    | ->     upper curve coeff.  <-|  | ->  lower curve coeff.       <-| 
AC.Wing.Airfoils = [0.2171 0.3450 0.2975 0.2685 0.2893 -0.1299 -0.2388 -0.1635 -0.0476 0.0797;
                    0.2171 0.3450 0.2975 0.2685 0.2893 -0.1299 -0.2388 -0.1635 -0.0476 0.0797];
                
AC.Wing.eta = [0;1];  % Spanwise location of the airfoil sections

% Viscous vs inviscid
AC.Visc  = 1;              % 0 for inviscidand 1 for viscous analysis

% Flight Conditions
AC.Aero.V     = airSpeed;            % flight speed (m/s)
AC.Aero.rho   = airDensity;         % air density  (kg/m3)
AC.Aero.alt   = altitude;             % flight altitude (m)
AC.Aero.Re    = Reynolds;        % reynolds number (bqased on mean aerodynamic chord)
AC.Aero.M     = Mach;           % flight Mach number 
% AC.Aero.CL    = Cl;         % lift coefficient -comment this line to run the code for given alpha%
AC.Aero.Alpha = AoA;             % angle of attack - comment this line to run the code for given cl ient - comment this line to run the code for given alpha%

%% 
% tic

Res = Q3D_solver(AC);

% t=toc

%%

CLdes = Res.CLwing;
CDdes = Res.CDwing;

end
