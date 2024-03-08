import numpy as np 
import can 
import pandas as pd 
from canlib import canlib 
import pyproj
import time
import os 
import j1939
import math
import datetime



'''
Class used for the creation of a message where the course over ground of the vehicle is calculated from the raw data 
'''



class CoG:
    

    '''
    The approach used is similar to the one used for the previous class
    INPUTS:  data array containing the data from the Simulator, the CAN ID, the PGN ID and the priority of the message 
    '''
    def __init__(self, dataArray, CANId, PGn, priorit):

        rvrsDct =   { 'alphaFR':0,
                      'alphaFL':1,
                      'Speed':2,
                      'Rpm':3,
                      'frame':4,
                      'GearRatio':5,
                      'alphaAxle':6,
                      'Ofl':7,
                      'Ofr':8,
                      'Orl':9,
                      'Orr':10,
                      'lat':11, 
                      'lon':12,
                      'h':13,
                      'pitch':14,
                      'yaw':15, 
                      'roll':16,
                      'travelD':17}

        colNames = dataArray.columns
        colNames = list(colNames)
        self.indces = []
        self.PrevCoG=0 # initialization of course over ground 

        for key in colNames:
            self.indces.append(rvrsDct.get(key))


        self.bus = can.interface.Bus(bustype='kvaser', channel = 0, bitrate = 1000000)
        self.canID = CANId


        self.pgn = j1939.PGN()
        self.pgn.value = PGn
        self.SAEbus = j1939.Bus(channel=0, bustype='kvaser', timeout=0.01, broadcast=True, bitrate = 250000)
        self.aid = j1939.ArbitrationID(pgn=self.pgn, source_address=0x14, destination_address=0xFF, priority = priorit)
        

   
    # CALCULATES THE CoG 
    def calculate(self, yaw):
        
        '''
        The calculation is based on the yaw angle TODO: calculate it from latitude and longitude
        '''
        cog = yaw 
        cog = cog + np.pi
        #cog = -cog 
        if yaw < 0:
            cog = cog +2*np.pi
        
        cog = cog % (2*np.pi)
        #print("cog [rad]", cog)
        return cog


    def shutBus(self):
        self.bus.shutdown()


    def encodeSeqID(id):

        id = np.int8(id)
        idn = id.hex()   # old --> id.bytes()

        return idn 

    def updateData(self):

        if os.path.exists(self.path) == True:

            try:
                dfP = pd.read_csv(self.path, engine = 'python',  header = None, usecols= self.indces )   

                self.dfPrevios = dfP

            except:

                print("out of synchro")
                dfP = self.dfPrevios #################################
        
        else:
            dfP = self.dfPrevios


        dfPcolL = len(dfP.columns)

        
        dfP = dfP.astype(np.float32)

        dt = dfP.tail(1).values


        preValues = self.dfPrevios.tail(1).values

        a = 0
        b=0

        if dt[0][0] != preValues[0][0] and dt[0][1] != preValues[0][1]: # check previous values are different from than current ones 

            yaw = dt[0][1] # 
            #speed = [preValues[0][1], dt[0][1]]

            a = self.calculate(yaw)
            self.PrevCoG = np.float16(a)
            a = (np.float16(a)) # CoG

            b = dt[0][0] # velocity 
            b = np.abs(b) # velocity 
            b = np.float16(b)

            #print("CoG: 1", a); print("SoG: 1", b)

        elif dt[0][0] == preValues[0][0] and dt[0][1] == preValues[0][1]:

            a = self.PrevCoG
            a = (np.float16(a)) # CoG
            b = (np.float16(dt[0][0]))

            #print("CoG: 1:", a); print("SoG: 1:", b)

        a = a *(10**4)
        a = int(a)

        b = b *(10**2)
        b = int(b); 
    
        self.dataCAN = list(a.to_bytes(2, 'little', signed = False)) + list(b.to_bytes(2, 'little', signed = False))


    def encodeSeqID(self, id):

        id = np.int8(id)
        self.seqE =id 


    # send data to the bus function: 

    def dataSend(self):
        #def data2can(arbID, dataCAN, idext):
        # 
     
        msg = can.Message(arbitration_id = self.canID , data= self.dataCAN , is_extended_id = False)  # TODO: create the dataCAN and idext 
 
   
        msg_sent = 0
        errors = 0 
 
        a = 1
    #for i in range(0,5):
        #time.sleep(0.001)
        try:
            if a ==1 :#self.bus.get_stats().bus_load > 9000:
                time.sleep(0.015)
                self.bus.send(msg)
                print()
                #print(self.dataCAN)
                print("message sent")# on {}".format(self.bus.channel_info))
                msg_sent= msg_sent+1
            else: 
               
                self.bus.send(msg)
                print()
                #print(self.dataCAN)
                print("message sent")# on {}".format(self.bus.channel_info))
                msg_sent= msg_sent+1

        except can.CanError:

            print()
            #print(self.dataCAN)
            print("message NOT sent")# {}".format(can.CanError.errno))
            time.sleep(0.015)
            #self.bus.flush_tx_buffer()

            errors = errors +1 

        #print()
        #print(self.bus.get_stats())
        print()
        print("-----------------------------------------------------------------------------------------------------------------------")
        self.msg_sent = msg_sent
        self.errors = errors
        
    def PGNsend(self):
    
        #msg = can.Message(arbitration_id = self.canID , data= self.dataCAN , is_extended_id = False)  # TODO: create the dataCAN and idext 
        msg_sent = 0
        errors = 0 

        pdu = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.dataCAN, info_strings=None) 
        
        a =1
        try:
            if a ==1 : #self.SAEbus.get_stats().bus_load > 9000:
                time.sleep(0.015)
                self.SAEbus.send(pdu)
                print()
            #print(self.dataCAN)
                print("message sent on")# {}".format(self.SAEbus.channel_info))
                msg_sent= msg_sent+1
                self.SAEbus.flush_tx_buffer()
            else: 
               
                self.SAEbus.send(pdu)
                self.SAEbus.flush_tx_buffer()


                print()
            #print(self.dataCAN)
                print("message sent on")# {}".format(self.SAEbus.channel_info))
                msg_sent= msg_sent+1

        except can.CanError:

            print()
        #print(self.dataCAN)
            print("Message NOT sent")# {}".format(self.SAEbus.CanError.errno))
            time.sleep(0.015)
            #self.SAEbus.flush_tx_buffer()
            self.SAEbus.flush_tx_buffer()
            errors = errors +1 

        #print()
        #print(self.bus.get_stats())
        print()
        print("-----------------------------------------------------------------------------------------------------------------------")
        self.msg_sent = msg_sent
        self.errors = errors
   

    def execute(self, seq): # by default we assume we don't have the seqID in the MSG, needs to be specified


        
        self.updateData()
        self.dataCAN = [seq, 63] + self.dataCAN + [255, 255]
        #self.dataCAN = bytearray(self.dataCAN)
        #self.dataSend() # send data to CAN
        self.PGNsend() # SAE J1939 protocol 



    
    def printstats(self):
        
        print()
        print("Successfully sent messages: ", self.msg_sent) # without sleep  1764/2000 // with time.sleep (0.00001) 2000/2000 10 millisec of delay // 1 millisec of delay 2000/2000
        print()
        print("Messages not sent: ", self.errors)



