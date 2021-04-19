function [CLdes,CDdes] = Q3Drunner(Ww,Wf_c,sweep,b,lambda_in,lambda_out,root,twist_in,twist_out,Au_r,Al_r,Au_t,Al_t)


% Wing planform geometry
chord_kink = root*lambda_in;
tip = chord_kink*lambda_out;
Y_kink = 5.616;
sweep_kink = 5.37;
sweep_out = sweep;
X_kink = root-chord_kink+tand(sweep_kink)*Y_kink;
sweep_in  = atand(X_kink/Y_kink);

AC.Wing.Geom = [];
AC.Wing.Geom(1,1) = 0;
AC.Wing.Geom(1,2) = 0;
AC.Wing.Geom(1,3) = 0;
AC.Wing.Geom(1,4) = root;
AC.Wing.Geom(1,5) = 0;
AC.Wing.Geom(2,1) = X_kink;
AC.Wing.Geom(2,2) = Y_kink;
AC.Wing.Geom(2,3) = 0;
AC.Wing.Geom(2,4) = root+Y_kink*tand(sweep_kink)-(Y_kink*tand(sweep));
AC.Wing.Geom(2,4) = chord_kink;
AC.Wing.Geom(2,5) = twist_in;
AC.Wing.Geom(3,1) = Y_kink*tand(sweep_in)+(b/2-Y_kink)*tand(sweep_out);
AC.Wing.Geom(3,2) = b/2;
AC.Wing.Geom(3,3) = 0;
AC.Wing.Geom(3,4) = tip;
AC.Wing.Geom(3,5) = twist_out;
S_in = (AC.Wing.Geom(1,4)+AC.Wing.Geom(2,4))*AC.Wing.Geom(2,2)*0.5;                      %inboard surface
S_out = (AC.Wing.Geom(3,4)+AC.Wing.Geom(2,4))*(AC.Wing.Geom(3,2)-AC.Wing.Geom(2,2))*0.5;  %inboard surface
S = 2*(S_in+S_out);                     %total surfaceMAC
lambda_in = AC.Wing.Geom(2,4)/AC.Wing.Geom(1,4);
lambda_out = AC.Wing.Geom(3,4)/AC.Wing.Geom(2,4);
MAC_in = 2/3*AC.Wing.Geom(1,4)*((1+lambda_in+lambda_in^2)/(1+lambda_in));
MAC_out = 2/3*AC.Wing.Geom(2,4)*((1+lambda_out+lambda_out^2)/(1+lambda_out));
MAC = (MAC_in*S_in+MAC_out*S_out)/(S_in+S_out);

% Wing incidence angle (degree)
AC.Wing.inc  = 0;   
                        
% Airfoil coefficients input matrix

Au_k = ((Au_t - Au_r)/(b/2))*(Y_kink/2) + Au_r;
Al_k = ((Al_t - Al_r)/(b/2))*(Y_kink/2) + Al_r;

%                    | ->     upper curve coeff.                <-|   | ->       lower curve coeff.       <-| 
AC.Wing.Airfoils   = [Au_r(1) Au_r(2) Au_r(3) Au_r(4) Au_r(5) Au_r(6) Al_r(1) Al_r(2) Al_r(3) Al_r(4) Al_r(5) Al_r(6);
                      Au_k(1) Au_k(2) Au_k(3) Au_k(4) Au_k(5) Au_k(6) Al_k(1) Al_k(2) Al_k(3) Al_k(4) Al_k(5) Al_k(6);
                      Au_t(1) Au_t(2) Au_t(3) Au_t(4) Au_t(5) Au_t(6) Al_t(1) Al_t(2) Al_t(3) Al_t(4) Al_t(5) Al_t(6)];

AC.Wing.eta = [0;Y_kink/b;1];  % Spanwise location of the airfoil sections

% Viscous vs inviscid
AC.Visc  = 1;              % 0 for inviscid and 1 for viscous analysis

% Flight Condition
W_AW = (29323-4280)*9.81;
MTOW = Wf_c + Ww + W_AW;
MTOW_des = sqrt(MTOW*(MTOW-Wf_c));
n = 1;
% Flight Condition
AC.Aero.M     = 0.74;           % flight Mach number  at 7924.8m
AC.Aero.alt   = 9807.8;         % flight altitude (m)
AC.Aero.rho   = 0.422620;        % air density  (kg/m3)
d_visc = 0.0000147581;        
AC.Aero.V     = AC.Aero.M*300.300;           % flight speed (m/s)
AC.Aero.Re    = AC.Aero.rho*MAC*AC.Aero.V/d_visc;          %reynolds number (based on mean aerodynamic chord)
q=1/2*AC.Aero.rho*AC.Aero.V^2;
AC.Aero.CL    = MTOW_des*n/(q*S);          % lift coefficient - comment this line to run the code for given alpha%

%% 
% tic

Res = Q3D_solver(AC);


% t=toc

%%

CLdes = Res.CLwing;
CDdes = Res.CDwing;

end
