clc
clear all
close all

fid = fopen('simm_airfoil.dat','r'); %filename
airfoil = fscanf(fid, '%g %g',[2 Inf])';
fclose(fid);

%load RAE2822_FIT

k = (size(airfoil(:,1))-1)/2;
m = size(airfoil);
m = m(1);
k = k(1);

yt = airfoil(:,2);
XL = airfoil(1:k,1);
XU = airfoil(k+1:m,1);
xcoord = airfoil(:,1);


Winit = [-1 -1 -1 -1 -1 1 1 1 1 1]; % initial weights

% Run the optimization code
[Wopt]=fmincon(@(W) airfoilfit(W,yt,XL,XU,0),Winit,[],[],[],[],ones(1,10)*-1,ones(1,10),[]);

% Generate the CST airfoil with optimum weights
[ycoord] = CST_airfoil_fit(Wopt,XL,XU,0);

% Plot and compare
% plot(xcoord,ycoord,'b--')
% hold on
% plot(xcoord,yt,'r')
% legend('CST','Target')
% set(gcf,'color','w')