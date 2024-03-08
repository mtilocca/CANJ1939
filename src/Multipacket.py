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
Class used for the ceation of a Multipacket message. as it is only one and its data are known we only need to pass 
the array containing the FS19 retrieved values  
'''


class MultiPacket:

    def __init__(self, dataArray):

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


        self.pgn = j1939.PGN()
        self.pgn.value = 0x0000 # change this with your PGN 
        self.SAEbus = j1939.Bus(channel=0, bustype='kvaser', timeout=0.01, broadcast=True, bitrate = 250000)
        self.aid = j1939.ArbitrationID(pgn=self.pgn, source_address=0x14, destination_address=0xFF, priority=3)
        print(self.aid)
        # Standard payloads parameters 

        self.SeqID = [0]  # 1 byte 
        self.PosDate = [0] # 2 bytes 
        self.PosTime = [0] # 4 bytes 
        self.Lat = [0] # 8 bytes 
        self.Lon = [0]# 8 bytess 
        self.Alt = [0] # 8 bytes 


        #self.TypeSys = 0000  # check better -- 4 bits 
        #self.MTHd = 0001 # check later -- 4 bits 

        self.TypeSysMTHd = [16]


        #self.integrity = 0 # 2 bits 
        #self.NMEa = 0 # 6 its 

        self.IntNMEA = [63] 

        self.NSvs = [12]; # 1 byte -- range 0-252 
        self.HDOp = 1.0; self.HDOp = self.HDOp * (10**2);self.HDOp = list(int(self.HDOp).to_bytes(2, 'little', signed = True)) # 2 bytes 
        self.PDOp = 1.0; self.PDOp = self.PDOp * (10**2);self.PDOp = list(int(self.PDOp).to_bytes(2, 'little', signed = True)) # 2 bytes 
        self.GeodSep = 0.0;self.GeodSep = self.GeodSep * (10**2) ;self.GeodSep = list(int(self.GeodSep).to_bytes(4, 'little', signed = True)) # 4 bytes 
        self.NrefStat = [1] # 1 byte 


        self.RefStTypeStID = 145; self.RefStTypeStID = list(self.RefStTypeStID.to_bytes(2, 'little', signed = False)) 

        self.AgeDGNSS = 100; self.AgeDGNSS = list(self.AgeDGNSS.to_bytes(2, 'little', signed = False)) # 2 bytes 

        self.ctrl = 0

        # days calc 

        today = datetime.date.today()
        ref = datetime.date(1970, 1, 1)

        days = (today - ref).days
        print("days", days)
        self.PosDate = list(days.to_bytes(2, 'little', signed = False))


    def updateData(self):

        today = datetime.date.today()
        ref = datetime.date(1970, 1, 1)

        days = (today - ref).days
        print("days", days)

        if os.path.exists(self.path) == True:

            try:
                dfP = pd.read_csv(self.path, engine = 'python',  header = None, usecols= self.indces ) # error   

                self.dfPrevios = dfP

            except:

                print("out of synchro")
                dfP = self.dfPrevios
        
        else:
            dfP = self.dfPrevios


        # sort values and filter them 
        dfP = dfP.astype(np.float64)
                
        dt = dfP.tail(1).values

            
        a = (np.float64(dt[0][0])) ; a = np.rad2deg(a)# latitude
        b = (np.float64(dt[0][1])); b = np.rad2deg(b) # longitude
        c = (np.float64(dt[0][2])) # altitude

        #print(a)
        #print(b)
            
        a = a *(10**16)
        a = int(a); 
        
        b = b *(10**16)
        b = int(b); 


        c = c *(10**6)
        c = int(c);


        # seconds 
        tim = time.localtime()
        current_time = time.strftime("%H:%M:%S", tim)
        date_time = datetime.datetime.strptime(current_time, "%H:%M:%S")
        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        seconds = a_timedelta.total_seconds()
        self.PosTime = 0
        self.PosTime = list(int(seconds).to_bytes(4, 'little', signed = False))


        self.dataCAN = []
        self.dataCAN = list(a.to_bytes(8, 'little', signed = False)) + list(b.to_bytes(8, 'little', signed = False)) + list(c.to_bytes(8, 'little', signed = False))
        #print(self.dataCAN)
        

    def DataOrg(self, seqID):
        
        n = 0


        if self.ctrl == 0:
            n = 0
        elif self.ctrl == 1: 
            n = 32 
        elif self.ctrl ==2:
            n =64
        elif self.ctrl ==3: 
            n = 96
        elif self.ctrl == 4:
            n = 128 
        elif self.ctrl == 5:
            n = 160
        elif self.ctrl == 6:
            n = 192    
        elif self.ctrl == 7:
            n = 224
        
        #

        def FrameCount(n, Id):
            return [n+Id]

       

        self.Data =  [seqID] + self.PosDate + self.PosTime  + self.dataCAN +[66, 253, 10, 200, 0, 190, 0, 0, 0, 0, 0,0, 255, 255, 255, 255, 255] #self.TypeSysMTHd + self.IntNMEA + self.NSvs + self.HDOp + self.PDOp + self.GeodSep + self.NrefStat + self.RefStTypeStID + self.AgeDGNSS # + self.RefStTypeStIDN + self.AgeDGNSSN 
        
        f0 = FrameCount(n, 0)
        self.Pload0 = f0 + [47] + self.Data[0:6];# print(len(self.Pload0)); #print(self.Data[0:6])
       
        f1 = FrameCount(n, 1)
        self.Pload1 = f1 + self.Data[6:13];

        

        f2 = FrameCount(n, 2)


        
        
        self.Pload2 = f2 + self.Data[13:20];# print(len(self.Pload2)); #print(self.Data[13:20])
        
        f3 = FrameCount(n, 3)

        self.Pload3 = f3 + self.Data[20:27];# print(len(self.Pload3)); #print(self.Data[20:27])
        

        f4 = FrameCount(n, 4)

        self.Pload4 = f4 + self.Data[27:34];# print(len(self.Pload4)); #print(self.Data[27:34])
        
        
        f5 = FrameCount(n, 5)

        self.Pload5 = f5 + self.Data[34:41]; #print(len(self.Pload5)); #print(self.Data[34:41])
        

        f6 = FrameCount(n, 6)

        self.Pload6 = f6 + self.Data[41:]# + [255] # 255, 255, 255, 255]; 
        
        if self.ctrl < 7:
            self.ctrl+=1
        else:
            self.ctrl = 0

    def PGNsend(self):

              
        #msg = can.Message(arbitration_id = self.canID , data= self.dataCAN , is_extended_id = False)  # TODO: create the dataCAN and idext 
 
   
        msg_sent = 0
        errors = 0 
 

        pdu0 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload0, info_strings=None) 
        pdu1 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload1, info_strings=None) 
        pdu2 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload2, info_strings=None) 
        pdu3 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload3, info_strings=None) 
        pdu4 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload4, info_strings=None) 
        pdu5 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload5, info_strings=None) 
        pdu6 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload6, info_strings=None) 
        
        #pdu7 = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.Pload7, info_strings=None) 
        


        def sending(pdu):
            #time.sleep(0.15)
            a =1
            try:
                if a ==1 : #self.SAEbus.get_stats().bus_load > 9000:
                #time.sleep(0.0015)
                    self.SAEbus.send(pdu)

                    print()
            #print(self.dataCAN)
                    print("Multipacket message sent")# {}".format(self.SAEbus.channel_info))
                    #msg_sent= msg_sent+1
                    self.SAEbus.flush_tx_buffer()

                else: 

                    self.SAEbus.send(pdu);

                    print()
            #print(self.dataCAN)
                    print("Multipacket message sent")# {}".format(self.SAEbus.channel_info))
                    #msg_sent= msg_sent+1
                    self.SAEbus.flush_tx_buffer()

            except can.CanError:

                print()
        #print(self.dataCAN)
                print("Message NOT sent")# {}".format(self.SAEbus.CanError.errno))
                #time.sleep(0.015)
            #self.SAEbus.flush_tx_buffer()

                #errors = errors +1 

        sending(pdu0); sending(pdu1); sending(pdu2); sending(pdu3); sending(pdu4); sending(pdu5); sending(pdu6)
        
        print()
        print("-----------------------------------------------------------------------------------------------------------------------")
       




    def execute(self, seq): # by default we assume we don't have the seqID in the MSG, needs to be specified
        
        #self.SeqID = seq
        
        self.updateData()
        self.DataOrg(seq)
        self.PGNsend() # SAE J1939 protocol 

