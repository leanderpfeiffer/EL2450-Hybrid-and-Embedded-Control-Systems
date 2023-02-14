#ifndef SERIAL_H_INCLUDED
#define SERIAL_H_INCLUDED

#include <string.h>
#include <cstring>
#include <stdio.h>
#include <cstdlib>
#include <sstream>
#include <iomanip>
#include <iostream>

#define DEC 10
#define HEX 16
#define OCT 8
#define BIN 2

class serial
{
    public:
        serial();
        void print(char[]);
        void print(int, int = DEC);
        void print(double, int = 2);
        char* sendSerialMsg(void);
    private:
        char buffer_serial[256];
        char buffer_return[256];
        int buffer_index;
};

#endif // SERIAL_H_INCLUDED
