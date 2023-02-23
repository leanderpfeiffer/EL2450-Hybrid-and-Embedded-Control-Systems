
tab0 = readtable("pos_log_combined.csv");
[d0_trajectory_combined, theta_trajectory_combined] = create_trajectories(tab0);

tab1 = readtable("pos_log_v0.csv");
[d0_trajectory_v0, theta_trajectory_v0] = create_trajectories(tab1);

tab2 = readtable("pos_log_omega0.csv");
[d0_trajectory_omega0, theta_trajectory_omega0] = create_trajectories(tab2);

hold on
plot(d0_trajectory_combined)
plot(d0_trajectory_v0)
plot(d0_trajectory_omega0)
ylabel("d_0 [m]")
xlabel("t [ms]")
lgd = legend("Combined controller", "v = 0", "\omega = 0");
fontsize(gcf,scale=1.2)
%axis([0 1000 -1 1 ])
hold off

% hold on
% plot(theta_trajectory_combined)
% plot(theta_trajectory_v0)
% plot(theta_trajectory_omega0)
% ylabel("\theta^R - \theta(t) [deg]")
% xlabel("t [ms]")
% lgd = legend("Combined controller", "v = 0", "\omega = 0");
% fontsize(gcf,scale=1.2)
% axis([0 6500 -90 90 ])
% hold off


function [d0_trajectory, theta_trajectory] = create_trajectories(tab)
    startValue = tab.x(1);
    endIndex = length(tab.x);
    theta_R = tab.theta(end);
   
    for row=1:endIndex
        if tab.x(row) ~= startValue 
            startIndex = row;
            x0 = tab.x(row);
            y0 = tab.y(row);
            break
        end
    end
    d0_trajectory = zeros(endIndex - startIndex, 2);
    theta_trajectory = zeros(endIndex - startIndex, 2);
    startTime = tab.timestamp(startIndex);

    for step = startIndex:endIndex
        theta = tab.theta(step);
        v_c = [cos(theta/180 * pi) sin(theta/180*pi)];
        Delta_0 = [x0 - tab.x(step); y0 - tab.y(step)];
        d_0 = v_c * Delta_0;
        timestamp = tab.timestamp(step) - startTime;

        d0_trajectory(step, : ) = [timestamp d_0]; 
        theta_trajectory(step, : ) = [timestamp theta_R - theta];
    end
end
