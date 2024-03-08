# CAN - J1939
This repository illustrates how to send single and multipacket messages to a CAN bus using the J1939 standard based on the framework provided [here](https://github.com/milhead2/python-j1939)

#### Logic of the implementation: 

- retrieve the data fromt the .txt file and sort it according to the names of the columns in the .txt file. 

- initialize the objects corresponding to the messages 

- while loop while data is streamed and consequently sent to the CAN bus

It is worth noting that the code also allows the use of custom counters which are often found in J1939 payloads. 
Moreover it is possible to send a multipacket message related to the GNSS connection of the system or simulator used. 

In the current implementation it is possible to send messages related to: the yaw-pitch-roll position of the vehicle, its speed and course over ground and its GNSS RTK corrected positioning 

To install the dependecies needed, download `requirements.txt` and run in your terminal
`pip install -r requirements.txt`
