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


class DataToCan:

    '''
    Inputs: the data array to process , the CAN ID of the message, bool Flag if the data is recored or live streamed, 
    the sequence ID bool Flag , the J1939 PGN , the priority of the message 
    '''
    def __init__(self, dataArray, canID, recorded, seqID, PGn, priorit):
        
        self.dataArray = dataArray  # 2/3xN numpy array with data from FS19 -- > dynamically update it ?  
        self.recorded = recorded     # [bool] whether the data is recorded 
        self.canID = canID     
        self.seqIDctrl = seqID      # FALSE IF MESSAGE DOES NOT HAVE IT    
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
                      'travelD':17}  # dictionary used to retrieve the data based on the col names 

        colNames = dataArray.columns
        colNames = list(colNames)
        self.indces = []

        for key in colNames:
            self.indces.append(rvrsDct.get(key))


        
        self.pgn = j1939.PGN()
        self.pgn.value = PGn
        self.SAEbus = j1939.Bus(channel=0, bustype='kvaser', timeout=0.01, broadcast=True, bitrate = 250000)  # creating the CAN connection according to J1939 STANDARD 
        self.aid = j1939.ArbitrationID(pgn=self.pgn, source_address=0x14, destination_address=0xFF, priority = priorit)

        self.bus = can.interface.Bus(bustype='kvaser', channel = 0, bitrate = 1000000) # normal CAN BUS -- not used 

        self.path = r'C:\Users\M. Tilocca\Documents\My Games\FarmingSimulator2019\dataToCan.txt'  # Path to acess our data 
    



    def data2canrand(self, ch): # send random data to the CAN bus to test specific channel is working. 
    
        bus = can.interface.Bus(bustype='kvaser', channel = ch, bitrate = 250000)  # fix error # bustype = kvaser 
        msg = can.Message(arbitration_id = 0xc0ffee, data=[0, 25, 0, 1, 3, 1, 4,1], is_extended_id = False)

        counter = 50
        msg_sent = 0 
        errors = 0 


        for i in range(0, counter):
    #time.sleep(0.00001)   # 0.000001 sec of pause 
            try:       
                bus.send(msg)
                print("message sent on {}".format(bus.channel_info))
                msg_sent= msg_sent+1

            except can.CanError:
                print("Message NOT sent")
                errors = errors +1 
        

        self.msg_sent = msg_sent
        self.errors = errors

        self.printstats()


    def sorting(self): # sorting the given array and extracting the last row --. so to get latest data from FS19
       
        arr = self.dataArray.tail(1)
         # ndArray[row_index][column_index]
        return arr
       

    def sortRec(self, row):  # sort recorded data 
       
        arr = self.dataArray

        lent = arr.shape
        lent = list(lent)
        lent = int(lent[0]) # ndArray[row_index][column_index]
          
            
        tosend = arr[row]

        return tosend 
        

    def dataSend(self):
        #def data2can(arbID, dataCAN, idext): 


        if self.seqIDctrl != False:
            msg = can.Message(arbitration_id = self.canID , data= self.dataCANSeq , is_extended_id = False)  # TODO: create the dataCAN and idext 
        else:
            msg = can.Message(arbitration_id = self.canID , data= self.dataCAN , is_extended_id = False)  # TODO: create the dataCAN and idext 
 
   
        msg_sent = 0
        errors = 0 
 

    #for i in range(0,5):
        #time.sleep(0.001)
        try:
            if self.bus.get_stats().bus_load > 9000:
                time.sleep(0.015)
                self.bus.send(msg)
                print()
                #print(self.dataCAN)
                print("message sent on {}".format(self.bus.channel_info))
                msg_sent= msg_sent+1
            else: 
               
                self.bus.send(msg)
                print()
                #print(self.dataCAN)
                print("message sent on {}".format(self.bus.channel_info))
                msg_sent= msg_sent+1

        except can.CanError:

            print()
            #print(self.dataCAN)
            print("Message NOT sent {}".format(can.CanError.errno))
            time.sleep(0.015)
            self.bus.flush_tx_buffer()

            errors = errors +1 

        #print()
        #print(self.bus.get_stats())
        print()
        print("-----------------------------------------------------------------------------------------------------------------------")
        self.msg_sent = msg_sent
        self.errors = errors
        #self.printstats(self)

        #a = 1 

        #return a

    def shutBus(self):  # close CAN BUS 
        self.bus.shutdown()

    def join(a,b):

        c = a + b 

        return c 


    def updateData(self): # MAIN function used to retrieve the data 

        if os.path.exists(self.path) == True:

            try:
                dfP = pd.read_csv(self.path, engine = 'python',  header = None, usecols= self.indces ) # error   

                self.dfPrevios = dfP

            except:

                print("out of synchro")
                dfP = self.dfPrevios
        
        else:
            dfP = self.dfPrevios


        dfPcolL = len(dfP.columns)

        if dfPcolL ==2 and self.seqIDctrl == False :
            dfP = dfP.astype(np.float32)

            dt = dfP.tail(1).values

            print("data values:", dt)
            print("data 0:", dt[0][0])
            print("data 1:", dt[0][1])


            a = (np.float32(dt[0][0]))
            b = (np.float32(dt[0][1]))

            self.dataCAN = []

            a = np.rad2deg(a)
            a = a *(10**7)
            a = int(a); 

            #print("latitude", a)
            #print(list(a.to_bytes(4, 'little', signed = True)))
            
            b = np.rad2deg(b)
            b = b *(10**7)
            b = int(b);

            print("longitude", b)
            print(list(b.to_bytes(4, 'little', signed = True)))


            self.dataCAN = list(a.to_bytes(4, 'little', signed = True)) + list(b.to_bytes(4, 'little', signed = True))
            print(self.dataCAN) # [0, 160, 68, 255, 0, 66, 18, 11] big || 

        elif dfPcolL == 3 and self.seqIDctrl == True: 
            
            dfP = dfP.astype(np.float16)
                
            dt = dfP.tail(1).values

           # print("data values:", dt)  # DEBUG 
           # print("data 0:", dt[0][0])
            #print("data 1:", dt[0][1])
            #print("data 2:", dt[0][2])



            a = (np.float16(dt[0][0]))
            b = (np.float16(dt[0][1]))
            c = (np.float16(dt[0][2]))

            
            a = a *(10**4)
            a = int(a); 
        
            b = b *(10**4)
            b = int(b); 


            c = c *(10**4)
            c = int(c);



            self.dataCAN = []
            self.dataCAN = list(b.to_bytes(2, 'little', signed = True)) + list(a.to_bytes(2, 'little', signed = True)) + list(c.to_bytes(2, 'little', signed = True))
            #print(self.dataCAN)

    def encodeSID(self, seq):

        seq = np.int8(seq)

        self.seqE = seq
        

 
    def PGNsend(self):  # MAIN FUNCTION USED TO SEND THE DATA TO THE BUS ACCORDING TO J1939 STANDARD

              
        #msg = can.Message(arbitration_id = self.canID , data= self.dataCAN , is_extended_id = False)  # TODO: create the dataCAN and idext 
 
   
        msg_sent = 0
        errors = 0 
 

        pdu = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=self.dataCAN, info_strings=None) 
        
        try:
            #if self.SAEbus.get_stats().bus_load > 9000:
            time.sleep(0.015)
            self.SAEbus.send(pdu)
            print()
            #print(self.dataCAN)
           # print("message sent on {}".format(self.SAEbus.channel_info))
            print("message sent")
            msg_sent= msg_sent+1
            #else: 
               
            #self.SAEbus.send(pdu)


            #print()
            #print(self.dataCAN)
            #print("message sent on {}".format(self.SAEbus.channel_info))
            #msg_sent= msg_sent+1

        except can.CanError:

            print()
        #print(self.dataCAN)
            #print("Message NOT sent {}".format(self.SAEbus.CanError.errno))
            print("message NOT sent")
            time.sleep(0.015)
            #self.SAEbus.flush_tx_buffer()
            

            errors = errors +1 

        #print()
        #print(self.bus.get_stats())
        print()
        print("-----------------------------------------------------------------------------------------------------------------------")
        self.msg_sent = msg_sent
        self.errors = errors
   




    
    def execute(self, seq): # by default we assume we don't have the seqID in the MSG, needs to be specified and updated 

        '''
        1] sort the data and get only the latest row --> most updated reading from FS19
        2] convert both the sequence ID and the data 
        3] join the two byte arrays together 
        4] send the data to the CAN 
        '''

        if self.seqIDctrl == True: 

            self.updateData()
            #self.encodeSID(seq)
            self.dataCAN = [seq] + self.dataCAN + [255]
            #= self.seqE + self.dataCAN # join the 2 arrays 
            #self.dataSend() # send data to CAN
            self.dataCAN = self.dataCAN
            self.PGNsend()
        else: 

            self.updateData()
            self.dataCAN = self.dataCAN
            #self.dataSend() # send data to CAN
            self.PGNsend()

    
    


    def printstats(self):
        
        print()
        print("Successfully sent messages: ", self.msg_sent) # without sleep  1764/2000 // with time.sleep (0.00001) 2000/2000 10 millisec of delay // 1 millisec of delay 2000/2000
        print()
        print("Messages not sent: ", self.errors)

    def executeRec(self, rowNm, seqIDcount = False):  # send recorded data to the BUS 

        if seqIDcount != False: 

            self.sortRec(rowNm) # select row equal to current rowNm 
            payload = self.encode(self.tosendData) # encode last row 
            seqID = self.encodeSeqID(seqIDcount) # encode seqID 
            self.dataCAN = self.join(seqID, payload) # join the 2 arrays 
            self.dataSend() # send data to CAN

        else: 

            self.sorting() # select last row -- How to retrieve last row  in real time ? 
            payload = self.encode(self.tosendData) # encode last row 
            self.dataCAN = payload 
            self.dataSend() # send data to CAN


    
