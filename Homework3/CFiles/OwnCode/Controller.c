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
}

left = v - w/2;
right = v + w/2;