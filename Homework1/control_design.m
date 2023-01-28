%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Hybrid and Embedded control systems
% Homework 1
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Initialization
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear
init_tanks;
g = 9.82;
Tau = 1/alpha1*sqrt(2*tank_h10/g);
k_tank = 60*beta*Tau;
gamma_tank = alpha1^2/alpha2^2;
uss = alpha2/beta*sqrt(2*g*tank_init_h2)*100/15; % steady state input
yss = 40; % steady state output

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Continuous Control design
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
uppertank = tf(k_tank,[Tau, 1]); % Transfer function for upper tank
lowertank = tf(gamma_tank, [Tau* gamma_tank, 1]); % Transfer function for upper tank
G = uppertank*lowertank; % Transfer function from input to lower tank level

% Calculate PID parameters
chi = 0.5;
zeta = 0.8;
omega0 = 0.2;

[K, Ti, Td, N] = polePlacePID(chi, omega0, zeta,Tau,gamma_tank,k_tank);
F = K * (tf(1) + tf(1,[Ti,  0]) + tf([Td * N , 0 ], [1, N]));
sys = F*G/(1+F*G);
S1 = stepinfo(sys);
T_r = S1.RiseTime
M = S1.Overshoot
T_set = S1.SettlingTime

w_c = getGainCrossover(F*G,1);

sim('tanks.mdl');
analogSignal = y;
performanceAnalog = analyseOutput(y);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Digital Control design
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
j=1;
n=20;
performanceZOH=zeros(n,3);
performanceDisc=zeros(n,3);


for Ts = linspace(0.1,2,n) % Sampling time

    simOut = sim('tanksZOH.mdl');
    zohSignal = y;
    
    performanceZOH(j,:) = analyseOutput(y);
    
    
    % Discretize the continous controller, save it in state space form
    F_disc = ss(c2d(F,Ts,'ZOH'));
    A_discretized = F_disc.A;
    B_discretized = F_disc.B;
    C_discretized = F_disc.C;
    D_discretized = F_disc.D;
    
    simOut = sim('tanksDisc.mdl');
    discretizisedSignal = y;
    performanceDisc(j,:) = analyseOutput(y);
    j=j+1;
    
end
figure;
scatter(performanceZOH(:,1),linspace(0.1,2,n))
hold on
scatter(performanceDisc(:,1),linspace(0.1,2,n))
plot([6 6],[0 2])
xlabel T_r
ylabel T_s
legend(["ZOH","Discretized","Upper Bound"])
hold off
figure;
scatter(performanceZOH(:,2),linspace(0.1,2,n))
hold on
scatter(performanceDisc(:,2),linspace(0.1,2,n))
plot([0.35 0.35],[0 2])
xlabel M
ylabel T_s
legend(["ZOH","Discretized","Upper Bound"])
hold off
figure;
scatter(performanceZOH(:,3),linspace(0.1,2,n))
hold on
scatter(performanceDisc(:,3),linspace(0.1,2,n))
plot([30 30],[0 2])
xlabel T_{set}
ylabel T_s
legend(["ZOH","Discretized","Upper Bound"])
hold off

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Discrete Control design
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

A = [-1/Tau 0 ; 1/Tau -1/(gamma_tank * Tau)];
B = [k_tank/Tau ; 0];
C = [0 1];
D = 0;

% Discretize the continous state space system, save it in state space form
Sys_disc = ss(c2d(ss(A,B,C,D), 4, 'ZOH'));
Phi = Sys_disc.A;
Gamma = Sys_disc.B;
C = Sys_disc.C;
D = Sys_disc.D;

% Observability and reachability
Wc = 1;
Wo = 1;

% State feedback controller gain
p=eig(A);
pdisc = exp(Ts*p);
L=acker(Phi,Gamma,pdisc)

% observer gain
K = (acker(Phi',C',[0 0]))'
% reference gain
lr = 1;

% augmented system matrices
Aa = 1;
Ba = 1;

output = [ [" ", "T_r", "M", "T_set"];
            "Analog", performanceAnalog;
            "ZOH", performanceZOH(n,:);
            "Discretized", performanceDisc(n,:)]

figure
hold on
plot(analogSignal)

plot(zohSignal)

plot(discretizisedSignal)
xlabel Time
ylabel Amplitude
legend(["Analog","ZOH","Discretized"])
hold off