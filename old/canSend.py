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
Class used for the creation of the other standard messages using raw or already preprocessed data from the simulator 
'''


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

####################################################################################################################################################

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

