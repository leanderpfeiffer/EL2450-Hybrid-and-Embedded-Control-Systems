function [performance] = analyseOutput(timeSignal)
    inputTime = 25;
    targetValue = 50;
    data = timeSignal.Data;
    time = timeSignal.Time;

    i = 1;
    
    while data(i) <= 41
        startTime = time(i);
        i = i + 1;
    end
    
    while data(i) <= 49
        T_r = time(i) - startTime;
        i = i + 1;
    end
  
    M = (max(data)- targetValue)/10;

    k = length(time);
    while abs(data(k) - targetValue) < targetValue * 0.02
        T_set = time(k) - inputTime;
        k = k - 1;
    end
    performance = [T_r M T_set];