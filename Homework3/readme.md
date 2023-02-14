# HW3 Lab Code

This is the code that we use in the lab for HW3.
There are three empty files that you need to fill in the folder `OwnCode`.

You do not need to run this code on your own machine if you do not want to.
Instead, you can test your code on our online simulator at http://167.71.51.167:8081/robot_frontend.html or http://167.172.162.86:8081/robot_frontend.html.

Of course, if you have an Unix OS or an Unix virtual machine, you may also run this code directly from your computer.
However, you still have to check that your code works in the online simulator.

Remember to upload the threee files contained in the folder `OwnCode` together with your homework report! (Make sure that you fill in the files first; do not upload the empty files.)


## Running the code on your computer

To run the software on an Unix computer or virtual machine, execute this commands in a terminal from within this folder.

    ./CompileExecuteCFiles.sh
    ./ExecuteGUI.sh.


## Structure

The structure is as follows:

* `ArduinoFiles/hybrid_control.ino`: The code for the Arduino for the students to fill in.
* `ArduinoFiles/libraries`: Arduino libraries for the robot. The have to be copied into `sketchbook/libraries` to work with the Arduino IDE.
* `CFiles`: Contains the C++ files for the simulation. Students put their own code the three files in `CFiles/OwnCode`
* `Python files`: This contains the controller GUI files. This is both to control the simulation was well was the actual robot. The entry point in `PythonFiles/gui.py`. The core program sits in `PythonFiles/ui/mainwindow.py` The actual GUI code is created with QT creator and is contained in the file `PythonFiles/ui/mainwindow.ui` from which `PythonFiles/ui/UI_mainwindow.py` gets generated.



## Running the robot in the lab

Do not be scared by these instructions.
The TAs will help you to set up your code in the lab.
Just make sure that your code works well on the online simulator.

### Software needed

* `python 2.7`
* `pyqt4`
* arduino IDE
* Nexus driver in `/home/sketchbook/libraries`

### Arduino

* Board: Ardiuno Duemilanove w/ATmega 328
* Select Tools -> serial port once arduino is connected
* Remove Jumper to flash the board
* Don't select SS usb ports
* Make sure the headers are the unix way (all headers with .h)


## Control application

1. `cd ./Desktop/hybrid\ lab\ var/control\ application/`
2. `python gui.py`
3. check serial port: `dmesg`

For debugging: in *arduino ide*, select *right port*, *tools*, *serial monitor*.



## Info on the lab MoCap system

### To run

1. Open track manager
2. Open new file
3. Body number is the list position on the body list (settings)

### To create new body

1. record file
2. shift+drag to select makers
3. right click --> create new body
4. name the body
5. close the file and open a new one
