import numpy as np 
import pandas as pd 
import json

class dataRetrieve:
    def __init__(self, dtype_path='dftype.json', columns_path='columns.json', data_path='dataToCan.txt'):
        with open(dtype_path, 'r') as f:
            dftype = json.load(f)
        with open(columns_path, 'r') as f:
            columns = json.load(f)
        
        # Convert string types to actual numpy dtypes
        self.dftype = {key: np.dtype(value) for key, value in dftype.items()}

        # Ensure column indices are integers
        self.dict = {int(key): value for key, value in columns.items()}

        self.df1 = pd.read_csv(data_path, header=None)
        self.df1 = self.df1.rename(columns=self.dict)
        self.df1 = self.df1.astype(self.dftype)

    def completeData(self):
        return self.df1

    def retrieve(self, col):
        arr = self.df1[col].copy()
        return arr



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