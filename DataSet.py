import numpy as np 
import pandas as pd 


# EXPLANATION OF DATASTRUCT CONTENT 
''' 
The created data structure has 14 columns for N rows. 

each column represents: 

1] alpha front right 
2] alpha front left 

3] vehicle speed (m/s)
4] motor RPM 

5] frame number 
6] gear ratio 

7] alpha axle 
8] omega front left (rad/s)

9] omega front right (rad/s)
10] omega rear left (rad/s)

11] omega rear right (rad/s)
12] latitude (rad)

13] longitude (rad)
14] height (deg)

15] rotX -- pitch
16] rotY -- yaw 

17] rotZ -- roll 
18] traveled distance 

'''



class dataRetrieve:

    def __init__(self):

        self.dftype = {'alphaFR': np.float16,
                            'alphaFL': np.float16,
                            'Speed': np.float16,
                            'Rpm': np.float16,
                            'frame': int,
                            'GearRatio': np.float16,
                            'alphaAxle': np.float16,
                            'Ofl': np.float16,
                            'Ofr': np.float16,
                            'Orl': np.float16,
                            'Orr': np.float16,
                            'lat': np.float32,
                            'lon': np.float32,
                            'h': np.float16, 
                            'pitch': np.float16, 
                            'yaw': np.float16, 
                            'roll': np.float16}
        
        self.dict = { 0: 'alphaFR',
                      1 : 'alphaFL',
                      2 : 'Speed',
                      3 : 'Rpm',
                      4 : 'frame',
                      5 : 'GearRatio',
                      6 : 'alphaAxle',
                      7 : 'Ofl',
                      8 : 'Ofr',
                      9 : 'Orl',
                      10 : 'Orr',
                      11 : 'lat', 
                      12 : 'lon',
                      13 : 'h',
                      14 : 'pitch',
                      15 : 'yaw', 
                      16 : 'roll',
                      17 : 'travelD'}

        self.df1 = pd.read_csv(r'C:\Users\M. Tilocca\Documents\My Games\FarmingSimulator2019\dataToCan.txt', header = None ) #error
        self.df1 = self.df1.rename(columns=self.dict)
        self.df1 = self.df1.astype(self.dftype)

    #def info(self): # used to keep track of number of rows --> to be used for the recorded data mainly 
        #info = self.dataStruct.shape 

        #info = list(info)
        #rowN = info[0]

        #return rowN
        

    def completeData(self):
        return self.df1

    def retrieve(self, col):
        arr = self.df1[col].copy()
        
        return arr



