% Initialization of the tank model
% The variables have names starting with "tank_" to avoid having them
% accidentally overwritten by students.

tank_h10 = 0.1;
tank_A = pi*(0.04445/2)^2;
tank_A1 = tank_A;
tank_a1 = pi*(0.0047625/2)^2;
tank_a2 = pi*(0.0047625/2)^2;
alpha1 = tank_a1/tank_A;
alpha2 = tank_a2/tank_A;

tank_Kpump = 4.55e-6; % m^3/s*V  (This value is given in the user's manual)
beta = tank_Kpump/tank_A;
tank_H1 = 0.25; % m
tank_init_h1 = 0.1; % m

% Lower Tank:
tank_A2 = pi*(0.04445/2)^2; % m^2 (This value is given in the user's manual)
tank_H2 = 0.25; % m
tank_init_h2 = 0.1; 