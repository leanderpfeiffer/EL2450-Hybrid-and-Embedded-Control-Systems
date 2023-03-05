switch(task_number){
    case 6:
        theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
        w = K_Psi * (theta_goal - theta);
        v = 0;
        break;    

    case 8:
        w = 0;
        
        d_0 = cos(theta * PI/180) * (x0 - x) + sin(theta * PI/180) * (y0 - y);
        v =  K_omega * d_0;
        break;

    case 9:
        theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
        w = K_Psi * (theta_goal - theta);
        
        d_0 = cos(theta * PI/180) * (x0 - x) + sin(theta * PI/180) * (y0 - y);
        v =  K_omega * d_0;
        break;
    
    case 11:
    	theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
    	w = 0;
    	d_0 = cos(theta_goal * PI/180) * abs(xg - x) + sin(theta_goal * PI/180) * abs(yg - y);
    	v =  K_omega * d_0;
    	break;
    
    case 14:
    	theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
    	v = 0;
    	dp = (x+p*cos(theta*PI/180)-x0)*sin(theta_goal*PI/180)-(y+p*sin(theta*PI/180)-y0)*cos(theta_goal*PI/180);
    	w = K_Psi * dp *180/PI;
    	break;
    	
    case 15:
    	theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
    	dp = (x+p*cos(theta*PI/180)-x0)*sin(theta_goal*PI/180)-(y+p*sin(theta*PI/180)-y0)*cos(theta_goal*PI/180);
    	w = K_Psi * dp;
    	d_0 = cos(theta * PI/180) * (xg - x) + sin(theta_goal * PI/180) * (yg - y);
    	v =  K_omega * d_0;

    	break;
    	
    case 17:
    	if (xg != x0)
    	{
    		theta_ref = atan2(yg - y0,xg - x0) * (180/PI);
    	}
    	else if (yg>y0)
    	{
    		theta_ref = 90;
    	}
    	else if (yg<y0)
    	{
    		theta_ref = -90;
    	}
    	error_rotation = theta_ref - theta;
    	d_0 = cos(theta_ref * PI / 180) * (xg - x) + sin(theta_ref * PI / 180) * (yg - y);

    	if (state == 1 && abs(error_rotation) <= epsilon_rotation) 
    	{
    	    state = 2;
    	}

    	if (state == 2 && abs(d_0) <= epsilon_d)
    	{
    	    state = 3;
    	}
    	if (state ==3 && abs(d_0) > epsilon_d)
    	{
    		state = 1;
    	}
    	Serial.print("Current state:");
    	Serial.print(state, DEC);
    	Serial.print("\nError rotation:");
    	Serial.print(error_rotation, 3);
    	Serial.print("\nError go to goal:");
    	Serial.print(dp, 3);
    	
    	if(state == 1){
        	theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
        	d_0 = cos(theta * PI/180) * abs(x - x0) + sin(theta * PI/180) * abs(y - y0);
    		w = K_Psi * (theta_goal - theta);
    		v = K_omega * d_0  ;
    	}
    	else if (state == 2){
        	theta_goal = atan2(yg - y0,xg - x0) * (180/PI);
        	dp = (x+p*cos(theta*PI/180)-x0)*sin(theta_goal*PI/180)-(y+p*sin(theta*PI/180)-y0)*cos(theta_goal*PI/180);
        	w = K_Psi * dp;
        	d_0 = cos(theta * PI/180) * (xg - x) + sin(theta_goal * PI/180) * (yg - y);
        	v =  K_omega * d_0;
    	}
    	else if (state == 3){
    		v = 0;
    		w = 0;
    	}
    	break;
    	
}

left = int(v - w/2);
right = int(v + w/2);