K_phi_values = {'2,5','3,5','4,5','5', '5,5','6,5', '8,5'};
%K_phi_values = ["2,5","5","8,5"];
plotLength = 200;

hold on
for i = 1:length(K_phi_values)
    tab = readtable("pos_log_"+string(K_phi_values(i))+".csv");
    for row=1:length(tab.theta)
        if tab.theta(row) > 0
            startIndex = row;
            endIndex = row + plotLength - 1;
            break
        end
    end
    xData = tab.timestamp(startIndex:endIndex) - tab.timestamp(startIndex) ;
    yData = 90 -  tab.theta(startIndex:endIndex);
    plot(xData,yData, 'DisplayName',string(K_phi_values(i)))
end
ylabel("\theta^R - \theta [deg]")
xlabel("t [ms]")
lgd = legend;
lgd.Title.String = 'Value of K_{\Psi}';
fontsize(gcf,scale=1.2)
hold off