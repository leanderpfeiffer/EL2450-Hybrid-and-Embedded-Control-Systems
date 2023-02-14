
#include "Serial.h"
//Constructor
serial::serial()
{
    std::memset(buffer_serial,'\0',256);
    buffer_index=0;
}

//write String into buffer
void serial::print(char str[])
{
    int n = (int) strlen(str);
    for (int j = buffer_index;j<buffer_index+n;j++) {
        buffer_serial[j]=str[j-buffer_index];
    }
    buffer_index+=n;
}

//Write a floating point variable into the buffer with a certain precision, default prescision i=2
void serial::print(double d, int i)
{
    std::ostringstream temp;
    temp << std::fixed << std::setprecision(i) << d;
    //temp <<d;
    std::string str_tmp = temp.str();
    const char* str = str_tmp.c_str();
    int n = (int) strlen(str);
    for (int j = buffer_index;j<buffer_index+n;j++) {
        buffer_serial[j]=str[j-buffer_index];
    }
    buffer_index+=n;

}

//Write an integer into the buffer with a certain base, default value base=10
void serial::print(int i, int base)
{
    if (i<0)
    {
        i=-i;
        print("-");
    }
    std::ostringstream temp;
    temp << std::setbase(base) <<i;
    std::string str_tmp = temp.str();
    const char* str = str_tmp.c_str();
    int n = (int) strlen(str);
    for (int j = buffer_index;j<buffer_index+n;j++) {
        buffer_serial[j]=str[j-buffer_index];
    }
    buffer_index+=n;

}

// return buffer content for sending it away
char* serial::sendSerialMsg()
{
    std::memcpy(buffer_return,buffer_serial,256);
    std::memset(buffer_serial,'\0',256);
    buffer_index=0;
    return buffer_return;
}
