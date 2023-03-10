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
Ts = 4
    % Discretize the continous controller, save it in state space form
F_disc = ss(c2d(F,Ts,'ZOH'));
A_discretized = F_disc.A;
B_discretized = F_disc.B;
C_discretized = F_disc.C;
D_discretized = F_disc.D;
    
simOut = sim('tanksDisc.mdl');
discretizisedSignal = y;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Discrete Control design
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Ts = 4
A = [-1/Tau 0 ; 1/Tau -1/(gamma_tank * Tau)];
B = [k_tank/Tau ; 0];
C = [0 1];
D = 0;

% Discretize the continous state space system, save it in state space form
Sys_disc = ss(c2d(ss(A,B,C,D), Ts, 'ZOH'));
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
L=acker(Phi,Gamma,pdisc);
%L=acker(Phi,Gamma,[0.5 0.5]);

% observer gain
K = (acker(Phi',C',[0 0]))'
% reference gain
lr = 1/(C*inv(eye(2)-Phi+Gamma*L)*Gamma);

% augmented system matrices
Aa = [Phi -Gamma*L; K*C Phi-Gamma*L-K*C];
Ba = [Gamma*lr; Gamma*lr];
Ca = [0 1 0 0];
G = @(s) Ca'*(s*eye(4)-Aa)\Ba;
sysaug= ss(Aa,Ba,[0 1 0 0],D);
sysmin = minreal(sysaug);
paug=pole(sysmin);

simOut=sim('tanksDiscDesign.mdl');
discretedesignSignal = y;

figure
hold on
plot(analogSignal)
plot(discretizisedSignal)
plot(discretedesignSignal)
legend("Analog PID controller", "discretizised controller", "discrete designed controller")
hold off
%%

j=1;
m=5;
%performanceDiscQuant=zeros(m,3);
<<<<<<< HEAD
%discretequantSignal= zeros(55,m); %size needs to be changed when changing time
=======
<<<<<<< Updated upstream
discretequantSignal= zeros(55,m); %change with time
=======
discretequantSignal= zeros(255,m); %size needs to be changed when changing time
>>>>>>> Stashed changes
>>>>>>> 757c3501f1d00e2d44a7007d99b5ddf10a13b799
figure;
for quantint = linspace(0.05,100,m)
set_param('tanksDiscQuant/Quantizer','QuantizationInterval',num2str(quantint))
set_param('tanksDiscQuant/Quantizer1','QuantizationInterval',num2str(quantint))
simOut=sim('tanksDiscQuant.mdl');
 %discretequantSignal(:,j) = y.Data;
 
 plot(y)
 hold on
 %performanceDiscQuant(j,:) = analyseOutput(y);
 j=j+1;
end
plot(discretedesignSignal)
xlabel Time
ylabel Amplitude
legend(["Qlevel=0.05","Qlevel=0.1","Qlevel=0.15","Qlevel=0.2","Qlevel=0.25","without quantization"])
hold off
output = [ [" ", "T_r", "M", "T_set"];
            "Analog", performanceAnalog;
            "ZOH", performanceZOH(1,:);
            "Discretized", performanceDisc(1,:)]

figure
hold on
plot(analogSignal)

plot(zohSignal)

plot(discretizisedSignal)

plot(discretedesignSignal)
xlabel Time
ylabel Amplitude
legend(["Analog","ZOH","Discretized","Discrete Design"])
hold off