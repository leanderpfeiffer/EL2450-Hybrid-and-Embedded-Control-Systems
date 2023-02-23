K_omega_values = {'6','7','8','9','9,5','10','10,5','11','12','13','14'};

%K_omega_values = {'1,2','1,4','1,6','1,8','2','2,5','3','3,5','4','4,5'};



hold on
for i = 1:length(K_omega_values)
    tab = readtable("pos_log_"+string(K_omega_values(i))+".csv");
    
    startIndex = 0;
    endIndex = length(tab.x);
    startValue = tab.x(1);
    endValue = tab.x(end);

    for row=1:endIndex
        if tab.x(row) > startValue && startIndex == 0
            startIndex = row;
            break
        end
    end
    xData = tab.timestamp(startIndex:endIndex) - tab.timestamp(startIndex) ;
    yData = 1 - (tab.x(startIndex:endIndex) - startValue)/(endValue - startValue);
    plot(xData,yData, 'DisplayName',string(K_omega_values(i)))
end
ylabel("\Delta_0 / \Delta_0(t=0) [-]")
xlabel("t [ms]")
lgd = legend;
lgd.Title.String = 'Value of K_{\omega}';
fontsize(gcf,scale=1.2)
axis([0 6500 -0.2 1 ])
hold off