 function init_pend_three
 
global executionTime
executionTime = 0.006; %executiontime for the controller

schedulingPolicy = 'prioDM'; %the scheduling policy used in the simulation
ttInitKernel(schedulingPolicy);

T = [0.02 0.029 0.035]; % Task periods
names= {'pid_task1', 'pid_task2', 'pid_task3'};

wVec = [9.9 7 5.7];
% Create three tasks
for i = 1:3
    w = wVec(i);
    % Design a LQG-controller
    sys = tf(w^2, [1 0 -(w^2)]);
    [cont,~,~,~,~,~] = lqgcalculation(sys, [1 0;0 0.002],0.1*eye(2),0.1,T(i),0);
    [A B C D] = ssdata(cont);
    
    data.A = A;
    data.B = B;
    data.C = C;
    data.D = D;
    data.state = [0; 0; 0];
    data.u = 0;
    data.theta_Chan = i;
    data.uChan = i;
    data.late=0;
    ttCreatePeriodicTask(names{i}, 0.0,T(i), 'pend_reg_three_code', data);
end





