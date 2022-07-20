from canSend import DataToCan, CoG, MultiPacket
from DataSet import dataRetrieve
import time 
import numpy as np 
from timeit import default_timer as timer
import multiprocessing # could be used to speed up the process 
import can 
import j1939



'''
LOGIC OF THE CODE: 

1] we retrieve the data fromt the .txt file and sort it according to the names of the columns in the .txt file. The names need to be matching otherwise 
the uopdate function in the canSend.py classes cannot retrieve the and update the data which is sent to the bus 

2] initialize the objects corresponding to the messages 

3] while loop where data is streamed. The multipacket message is sent only once per second and the sequence ID is update once per second as well 
'''


def seq_ID(counter):

    '''
    Function used to update the sequence ID 
    
    '''
    if counter <= 251: 
        counter +=1
    else:
        counter = 0
       # counter +=1

    new_counter = counter 
    return new_counter 


# Data retrieve from the .txt file   -- STEP 1] 

dataSet = dataRetrieve()
Wgs84 = dataSet.retrieve(['lat', 'lon'])
Ypr = dataSet.retrieve(['yaw', 'pitch', 'roll'])
CoG_Data = dataSet.retrieve(['yaw', 'Speed'])
MultiData = dataSet.retrieve(['lat', 'lon', 'h'])
# IDS [(yaw, pitch, roll), (course over ground & speed over ground), (latitude & longitude), 


#  --------------------- STEP 2] ------------------


IDs = [233904404, 167248404, 167248148]
PGNs = [0x0000, 0x0000, 0x0000] # Put here your PGN 



MsgWGS = DataToCan(Wgs84, IDs[2], False, False, PGNs[1], 2)
MsgYPR = DataToCan(Ypr, IDs[0], False, True, PGNs[0], 3)
MsgCoG = CoG(CoG_Data, IDs[1], PGNs[2], 7) 
MsgMulti = MultiPacket(MultiData)


# Sending the data: 
counter = 0 # seq ID counter initialization 0
start = 0
end = 0
res = 3 
ctrl = 0


def timingSt():
    return time.time()

try: 
    while True:
        #time.sleep(1)
        #ctrl = ctrl+1 


        #if ctrl == 10:
        
        #ctrl = 0

        if ctrl == 0:
            start = timingSt()
            ctrl = 1

        print(counter) # update the seq_ID counter for data synchronization -- update counter only once per sec 

        elapsed = time.time() - start

        if int(elapsed) == 1:  # multipacket sent only once per second 
            counter = seq_ID(counter)
            MsgMulti.execute(counter)
            start = 0 
            MsgWGS.execute(None)
            MsgYPR.execute(counter)
            MsgCoG.execute(counter)
            ctrl = 0
        

        else:
            MsgWGS.execute(None)
            MsgYPR.execute(counter)
            MsgCoG.execute(counter)
        
    
except KeyboardInterrupt:

    MsgWGS.shutBus()
    MsgYPR.shutBus()
    MsgCoG.shutBus()
    
    # shut down the bus 1
    # shut down the bus 2
    # shut down the bus 3 

