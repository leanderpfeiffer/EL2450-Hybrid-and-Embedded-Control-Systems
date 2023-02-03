simOut = sim('inv_pend_three.mdl');

figure
plot(Theta)
ylabel 'Theta [rad]'
xlabel 'Time [s]'
legend(["Pendulum 1","Pendulum 2","Pendulum 3"])