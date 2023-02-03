simOut = sim('inv_pend_three.mdl');

%plot theta
figure
plot(Theta)
ylabel 'Theta [rad]'
xlabel 'Time [s]'
legend(["Pendulum 1","Pendulum 2","Pendulum 3"])

%plot schedule
figure
plot(Schedule)
ylabel ''
xlabel 'Time [s]'
xlim([0 0.15])
ylim([0 4])
legend(["Pendulum 1","Pendulum 2","Pendulum 3"])