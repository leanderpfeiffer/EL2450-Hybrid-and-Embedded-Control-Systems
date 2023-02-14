
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <cstdlib>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/poll.h>
#include <netdb.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>
#include "Serial.h"

#define PORT_CONTROLLER "43125" //uses port 43125 for the controller connection between Python and C
#define PORT_MOCAP "43126" //uses port 43126 for the controller connection between Python and C
#define BACKLOG 10 // for the listening sockets to determine how big the queue of pending connections can get
#define MAXDATASIZE 100 // maximal size of the buffer

#define PI 3.14159265

/* Variables for communication via a socket */

int socket_controller, socket_accept_controller, socket_mocap, socket_accept_mocap; // ints for sockets
int control_open; // checks if connection to controller socket is open or closed
int mocap_open; // checks if connection to mocap socket is open or closed
struct pollfd ufds_control[1],ufds_mocap[1]; // used to check the activity of the sockets which connect Python and C

int status; // auxiliary variable to check if initialization of the sockets was successful
socklen_t addr_size;
struct addrinfo hints, *res;
struct sockaddr_storage their_addr;

/* Variables for the controller */

//create a buffer state enumeration
enum buffer_state {
  BUFFER_EMPTY,
  STATE_QUERY,
  MANUAL_CONTROL,
  POSE_DATA,
  START_GOAL,
  BUFFER_INVALID
};

//initialize variables for the buffer of the controller commands
const int buffer_size = 100;
char buffer_msg[100];
char buffer[100];
char junk[100];
char manual_buffer[16];
char pose_buffer[21];

//initialize variables for the buffer of the mocap commands
char buffer_msg_mocap[100];
char buffer_mocap[100];
char junk_mocap[100];

//initialize variables for the controller outputs
int left=0;
int right=0;

// "measured" states by the mocap system
int x=0;
int y=0;
int theta=0;

// true robot values coming from the robot model
double x_true = 0;
double y_true = 0;
double theta_true = 0;

void updateRobotState(double dt) //updating the robots state
{
    double R_true = 0.1001405119340;
    double L_true = 0.5052864456892;

    // limit the control input (again in case the students did not do it)
    if (left >= 800)
    {
        left=800;
    }
    if (left <= -800)
    {
        left=-800;
    }
    if ( right >= 800)
    {
        right=800;
    }
    if ( right <= -800)
    {
        right=-800;
    }

    // state space model for the robot
    x_true = x_true + 0.5*R_true*(left+right)*cos(theta_true*PI/180)*dt;
    y_true = y_true + 0.5*R_true*(left+right)*sin(theta_true*PI/180)*dt;
    theta_true = theta_true + R_true/L_true*(right-left)*dt;
    //limit theta to (-180,180]
    if (theta_true > 180) {
        theta_true=theta_true-360;
    }
    if (theta_true<=-180) {
        theta_true=theta_true+360;
    }
}

//Functions for using the buffers
#include "BufferFunctions.c"

void createListeningSocketToController(void) // creates a socket which listens for connections to the GUI, which correspond to controller commands
{
    memset(&hints,0,sizeof hints);
    hints.ai_family=AF_INET;
    hints.ai_socktype=SOCK_STREAM;
    hints.ai_flags=AI_PASSIVE;
    if ((status=getaddrinfo("127.0.0.1",PORT_CONTROLLER,&hints,&res)) != 0) // using the IP 127.0.0.1 indicates that we do a communication between programs on the local host
    {
        printf("getaddrinfo error: %s\n",gai_strerror(status));
        exit(1);
    }

    socket_controller=socket(res->ai_family,res->ai_socktype,res->ai_protocol); // create socket
    if (socket_controller<0)
    {
        printf("opening socket error: %s \n", strerror(errno));
        exit(1);
    }

    int yes=1;
    if (setsockopt(socket_controller,SOL_SOCKET,SO_REUSEADDR,&yes,sizeof(int)) == -1) // makes port 43125 reusable in case a new socket has to be created
    {
        printf("Socket option error");
    }

    status=bind(socket_controller,res->ai_addr,res->ai_addrlen); // bind socket to adress
    if (status != 0)
    {
        printf("bind error: %s",strerror(errno));
        exit(1);
    }

    status=listen(socket_controller,BACKLOG); // start listening for a connection
    if (status != 0)
    {
        printf("listen error: %s",strerror(errno));
        exit(1);
    }
}

void createListeningSocketToMOCAP (void) // creates a socket which listens for connections to the GUI, which correspond to mocap commands
{
    memset(&hints,0,sizeof hints);
    hints.ai_family=AF_INET;
    hints.ai_socktype=SOCK_STREAM;
    hints.ai_flags=AI_PASSIVE;
    if ((status=getaddrinfo("127.0.0.1",PORT_MOCAP,&hints,&res)) != 0)
    {
        printf("getaddrinfo error: %s\n",gai_strerror(status));
        exit(1);
    }

    socket_mocap=socket(res->ai_family,res->ai_socktype,res->ai_protocol); // create socket
    if (socket_mocap<0)
    {
        printf("opening socket error: %s \n", strerror(errno));
        exit(1);
    }

    int yes=1;
    if (setsockopt(socket_mocap,SOL_SOCKET,SO_REUSEADDR,&yes,sizeof(int)) == -1) // makes port 43126 reusable in case a new socket has to be created
    {
        printf("Socket option error");
    }

    status=bind(socket_mocap,res->ai_addr,res->ai_addrlen); // bind socket to adress
    if (status != 0)
    {
        printf("bind error: %s",strerror(errno));
        exit(1);
    }
    status=listen(socket_mocap,BACKLOG); // listen for a connection
    if (status != 0)
    {
        printf("listen error: %s",strerror(errno));
        exit(1);
    }
}

int main()
{

    //initialize variables for the robots start and goal positions
    int x0=0;
    int y0=0;
    int xg=0;
    int yg=0;

    fd_set read_fds,read_fds_master; // declares sets of sockets which are used for checking if the GUI wants to establish a connection with the simulation
    struct timeval timeout_select; // timeout for the select function is set to one millisecond
    timeout_select.tv_sec = 0;
    timeout_select.tv_usec = 1000;
    // clear the read sets
    FD_ZERO(&read_fds);
    FD_ZERO(&read_fds_master);
    int poll_answer,select_answer; // variables to check what happened with the poll and select function


    double dt,last_time_update,current_time,timer_val; // time variables to determine the time step for the simulation
    struct timespec timer;

    //auxiliary variables to check if a connection exists
    control_open = 0;
    mocap_open = 0;

    /* define your own variable here */

    #include "OwnCode/OwnVariables.c"

    /*================*/

    //creates sockets for listening to
    createListeningSocketToController();
    FD_SET(socket_controller,&read_fds_master);
    int fdmax = socket_controller;
    createListeningSocketToMOCAP();
    FD_SET(socket_mocap,&read_fds_master);
    if (socket_mocap > socket_controller)
    {
        fdmax=socket_mocap;
    }

    ufds_control[0].events = POLLIN ;
    ufds_mocap[0].events = POLLIN ;

    serial Serial = serial();

    int msg_len, bytes_sent;
    char str_mocap[128]; // string variable for the return values of the mocap system (pose and time)
    char* str_serial; // string variable for returning the serial.print outputs
    clock_gettime(CLOCK_MONOTONIC,&timer);
    last_time_update = (double) timer.tv_sec + (double) timer.tv_nsec/1000000000;
    printf("Starting simulation\n");

    while (1)
    {
        read_fds = read_fds_master; // this is necessary because select changes read_fds
        select_answer = select(fdmax+1,&read_fds,NULL,NULL,&timeout_select);
        if (select_answer == -1)
        {
            perror("select");
            exit(4);
        } else if ( select_answer == 0) {
            //printf("Timeout occured \n");
        }
        if (control_open == 0) // if no controller connection established, do this
        {
            if(FD_ISSET(socket_controller,&read_fds)) { // checks if the control on button is pressed
                printf("Creating controller connection with python\n");
                addr_size=sizeof their_addr;
                socket_accept_controller=accept(socket_controller,(struct sockaddr *) &their_addr,&addr_size); // accepts connection
                if (status == -1)
                {
                    printf("accept error: %s",strerror(errno));
                    exit(1);
                }
                ufds_control[0].fd=socket_accept_controller; // adds newly created socket to the array used for checking if something happens in the controller connection
                control_open=1;

            } //if to check if we have a control connection available

        } // if control_open == 0

        if (mocap_open == 0) // if no mocap connection established, do this
        {
            //printf("Look for mocap connection \n");
            if(FD_ISSET(socket_mocap,&read_fds)) {// checks if the mocap on button is pressed
                printf("Creating mocap connection with python\n");
                addr_size=sizeof their_addr;
                socket_accept_mocap=accept(socket_mocap,(struct sockaddr *) &their_addr,&addr_size); // accept connection
                if (status == -1)
                {
                    printf("accept error: %s",strerror(errno));
                    exit(1);
                }
                ufds_mocap[0].fd=socket_accept_mocap; // adds newly created socket to the array used for checking if something happens in the mocap connection
                mocap_open=1;

            } //if to check if we have a mocap connection available

        } // if mocap_open == 0

        if (mocap_open == 1)
        {
            poll_answer=poll(ufds_mocap,1,1);
            if (poll_answer == -1) {
                perror("poll");
            } else {
                if (ufds_mocap[0].revents & POLLIN) {
                    switch(read_buffer_mocap()) {
                    case BUFFER_EMPTY:
                        break;
                    case STATE_QUERY:
                        clock_gettime(CLOCK_MONOTONIC,&timer);
                        timer_val = (double) timer.tv_sec + (double) timer.tv_nsec/1000000000;
                        sprintf(str_mocap,":state %f %f %f %f;",x_true,y_true,theta_true,timer_val*1000000); // send robot state and timestamp in microseconds
                        msg_len=strlen(str_mocap);
                        bytes_sent=send(socket_accept_mocap,str_mocap,msg_len,0);
                        if (bytes_sent == -1)
                        {
                            perror("recv");
                            exit(1);
                        }
                        break;
                    case BUFFER_INVALID:
                        break;
                    } //switch for reading mocap buffer


                } // if mocap send something
            } // else poll found something

        } // if mocap_open

        if (control_open == 1)
        {
            poll_answer=poll(ufds_control,1,1); // checks what happens to the socket used for the controller connection
            if (poll_answer == -1) {
                perror("poll");
            } else {
                if (ufds_control[0].revents & POLLIN) { // if the socket receives some data...

                    switch(read_buffer()) { //... the data is read out and checked which command it is
                    case BUFFER_EMPTY://empty buffer
                        break;
                    case MANUAL_CONTROL://manual control
                        memcpy(manual_buffer,buffer,16);
                        sscanf(manual_buffer, "manual %d %d",&left,&right);
                        Serial.print("SYS: ");
                        Serial.print(":!set left=");
                        Serial.print(left, DEC);
                        Serial.print(" right=");
                        Serial.print(right, DEC);
                        Serial.print(";\n");
                        str_serial=Serial.sendSerialMsg();
                        msg_len=strlen(str_serial);
                        bytes_sent=send(socket_accept_controller,str_serial,msg_len,0);
                        break;
                    case STATE_QUERY://send state/state query
                        Serial.print(":state ");
                        Serial.print(left, DEC);
                        Serial.print(" ");
                        Serial.print(right, DEC);
                        Serial.print(";");
                        str_serial=Serial.sendSerialMsg();
                        msg_len=strlen(str_serial);
                        bytes_sent=send(socket_accept_controller,str_serial,msg_len,0); // send the current control value to the gui
                        break;
                    case POSE_DATA://pose_data
                        memcpy(pose_buffer,buffer,21);
                        sscanf(pose_buffer, "pose %d %d %d", &x, &y, &theta);
                        Serial.print("SYS: ");
                        Serial.print(":!pose_x=(cm)");
                        Serial.print(x, DEC);
                        Serial.print(" pose_y=(cm)");
                        Serial.print(y, DEC);
                        Serial.print(" pose_theta=(degree)");
                        Serial.print(theta, DEC);
                        Serial.print(";\n");
                        /* put your controller here */

                        #include "OwnCode/Controller.c" //here the controller function written by the students is included

                        /*=============*/
                        /* end of controller */

                        Serial.print("SYS: ");
                        Serial.print(":!set left=");
                        Serial.print(left, DEC);
                        Serial.print(" right=");
                        Serial.print(right, DEC);
                        Serial.print(";\n");
                        str_serial=Serial.sendSerialMsg();
                        msg_len=strlen(str_serial);
                        bytes_sent=send(socket_accept_controller,str_serial,msg_len,0);

                        break;
                    case START_GOAL://start goal
                        sscanf(buffer, "startgoal %d %d %d %d", &x0, &y0, &xg, &yg); // reads out the new start position and destination
                        Serial.print("SYS: ");
                        Serial.print(":!start_x=(cm)");
                        Serial.print(x0, DEC);
                        Serial.print(" start_y=(cm)");
                        Serial.print(y0, DEC);
                        Serial.print(":!goal_x=(cm)");
                        Serial.print(xg, DEC);
                        Serial.print("goal_y=(cm)");
                        Serial.print(yg, DEC);
                        Serial.print(";\n");
                        str_serial=Serial.sendSerialMsg();
                        msg_len=strlen(str_serial);
                        bytes_sent=send(socket_accept_controller,str_serial,msg_len,0);
                        /* Renew control state upon receiving new goals*/
                        /*========*/
                        #include "OwnCode/RenewControllerState.c" // student code for renewing the controller state
                        /*=======*/
                        break;
                    case BUFFER_INVALID://invalid buffer
                        left=0;
                        right=0;
                        Serial.print("SYS: ");
                        Serial.print("got an invalid command");
                        str_serial=Serial.sendSerialMsg();
                        msg_len=strlen(str_serial);
                        bytes_sent=send(socket_accept_controller,str_serial,msg_len,0);
                        break;
                    } //switch case read buffer
                } // if controller send something
            } // else
        } // control open

        //update the robots state/pose
        clock_gettime(CLOCK_MONOTONIC,&timer);
        current_time =  (double) timer.tv_sec + (double) timer.tv_nsec/1000000000; // get the current time
        dt=current_time-last_time_update; // take the time difference for the state space of the robot
        updateRobotState(dt); // update robot state
        last_time_update = current_time; // update the last time update
        usleep(1000); // let the execution sleep for 1ms to keep the cpu usage low
    } // while loop
    printf("end of while loop\n");
    return 0;
}
