

figure
%axis([0 2 -0.2 0.2])
hold on
for tau = 0.01:0.01:0.04
    sim("inv_pend_delay.mdl")
    plot(theta)
    
end
legend("tau = " +string(0.01:0.01:0.04)+"s")
xlabel("t [s]")
ylabel("theta [rad]")
hold off

% 0.15 - -0.15