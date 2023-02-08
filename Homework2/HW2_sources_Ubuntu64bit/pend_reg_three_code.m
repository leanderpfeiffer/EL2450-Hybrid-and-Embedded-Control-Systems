function [exectime, data] = pend_reg_three_code(segment,data)
global executionTime
switch segment,
    
 case 1,
  
  inp(1) = ttAnalogIn(data.theta_Chan);
  
  data.u = data.C*data.state+ data.D*inp(1); 
  data.state = data.A*data.state + data.B*inp(1);
  exectime = executionTime; 
  
 case 2,
  ttAnalogOut(data.uChan, data.u);
  exectime = -1;
end