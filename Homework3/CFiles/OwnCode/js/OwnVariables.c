double v = 0;
double w = 0;

const double h=1;
double theta_goal;
double d_0;
double dp;
double p = 2;
int state;

const double K_Psi = 2*(L_true/R_true)*1/p -1; // 2.5 pretty good
const double K_omega = 10-2;
const double epsilon_rotation = 0.01;
const double epsilon_d = 0.1;
double error_rotation;
double error_go_to_goal;
double theta_ref;

const int task_number = 17;