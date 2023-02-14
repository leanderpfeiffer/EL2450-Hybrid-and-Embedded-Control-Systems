int readBytesUntil(char c, char ret[],int n) // reads the buffer of the controller until a certain character c and saves it in the array ret, where n is the buffer size
{
    int i;
    char temp;
    for (i=0;i<n;i++) // iterate over all character in the buffer
    {
        temp=buffer_msg[i];
        if(temp==c) // check if the current character is the one we look for
        {
            ret[i]=temp;
            strncpy(buffer_msg,buffer_msg+i+1,n-i-1); // if not cut the parts of the buffer, which you don't want
            return ++i;
        }
        else
        {
            ret[i]=temp;
        }
    }
    return 0;
}

int readBytesUntilMOCAP(char c, char ret[],int n)  // reads the buffer of the mocap until a certain character c and saves it in the array ret, where n is the buffer size
{
    int i;
    char temp;
    for (i=0;i<n;i++) // iterate over all character in the buffer
    {
        temp=buffer_msg_mocap[i];
        if(temp==c) // check if the current character is the one we look for
        {
            ret[i]=temp;
            strncpy(buffer_msg_mocap,buffer_msg_mocap+i+1,n-i-1); // if not cut the parts of the buffer, which you don't want
            return ++i;
        }
        else
        {
            ret[i]=temp;
        }
    }
    return 0;
}

int is_manual_control() // checks if the user send a manual control
{
    if (strncmp(buffer,"manual",6) != 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

int is_state_query() // checks if the controller buffer contains a state query
{
    if (strncmp(buffer,"state?",6) != 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

int MOCAP_state_query() // checks if the mocap buffer contains a state query
{
    if (strncmp(buffer_mocap,"state?",6) != 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

int is_pose_data() // checks if the controller buffer contains a measurement of the pose
{
    if (strncmp(buffer,"pose",4) != 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

int is_start_goal() // checks if the controller buffer contains new destination for the robot to go to
{
    if (strncmp(buffer,"startgoal",9) != 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

int read_buffer() //returns what command the controller buffer contains
{
    int i,bytes_received;

    bytes_received=recv(socket_accept_controller,buffer_msg,MAXDATASIZE-1,0); // reads out the buffer for the controller

    if (bytes_received == -1) // checks if something went wrong while receiving the data
    {
        perror("recv");
        exit(1);
    }
    if (bytes_received == 0) // if no bytes were in the message the controller socket connection has closed
    {
        printf("Controller connection has closed down! \n");
        close(socket_accept_controller);
        control_open=0;
        return BUFFER_INVALID;
    }
    buffer_msg[bytes_received]='\0';

    readBytesUntil(':',junk,100);
    i=readBytesUntil(';',buffer,100);
    if (i==0) {
        return BUFFER_EMPTY;
    } else if (is_manual_control()) {
        return MANUAL_CONTROL;
    } else if (is_state_query()) {
        return STATE_QUERY;
    } else if (is_pose_data()) {
        return POSE_DATA;
    } else if (is_start_goal()) {
        return START_GOAL;
    } else{
        return BUFFER_INVALID;
    }
}

int read_buffer_mocap() //returns what command the mocap buffer contains
{
    int i,bytes_received;
    bytes_received=recv(socket_accept_mocap,buffer_msg_mocap,MAXDATASIZE-1,0); // reads out the buffer for the mocap simulation

    if (bytes_received == -1) // checks if something went wrong while receiving the data
    {
        perror("recv");
        exit(1);
    }
    if (bytes_received == 0) // if no bytes were in the message the mocap socket connection has closed
    {
        printf("Mocap connection has closed down! \n");
        close(socket_accept_mocap);
        mocap_open=0;
        return BUFFER_INVALID;
        //exit(1);
    }
    buffer_msg_mocap[bytes_received]='\0';


    readBytesUntilMOCAP(':',junk_mocap,100); // cuts of the parts of te buffer, which are not useful
    i=readBytesUntilMOCAP(';',buffer_mocap,100); // writes the actual message in the buffer
    if (i==0) {
        return BUFFER_EMPTY;
    } else if (MOCAP_state_query()) {
        return STATE_QUERY;
    } else{
        return BUFFER_INVALID;
    }
}
