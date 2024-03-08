import numpy as np
import can
import j1939
import os
import pandas as pd

class CoG:
    def __init__(self, dataArray, CANId, PGN, priority):
        self.dataArray = dataArray
        self.canID = CANId
        self.pgn = j1939.PGN(PGN)
        self.priority = priority
        self.aid = j1939.ArbitrationID(pgn=self.pgn, source_address=0x14, destination_address=0xFF, priority=priority)
        self.bus = j1939.Bus(channel=0, bustype='kvaser', timeout=0.01, broadcast=True, bitrate=250000)
        self.PrevCoG = 0  # Initialize previous course over ground

        # Mapping from column names to indices, assuming 'yaw' and 'speed' are required
        self.column_indices = {'yaw': dataArray.columns.get_loc('yaw'),
                               'speed': dataArray.columns.get_loc('speed')}

    def calculate_cog(self, yaw):
        """
        Calculate the course over ground based on yaw angle.
        """
        cog = (yaw + np.pi) % (2 * np.pi)
        return cog

    def prepare_data(self):
        """
        Prepares data for sending, calculating course over ground and speed.
        """
        latest_data = self.dataArray.tail(1).iloc[0]
        yaw = latest_data['yaw']
        speed = abs(latest_data['speed'])  # Absolute speed value

        cog = self.calculate_cog(yaw)
        self.PrevCoG = cog  # Update previous CoG

        # Convert values to the format needed for CAN transmission
        cog_bytes = self.value_to_bytes(cog, 'float32')
        speed_bytes = self.value_to_bytes(speed, 'float32')

        return cog_bytes + speed_bytes

    @staticmethod
    def value_to_bytes(value, dtype='float32', byteorder='little', signed=False, length=4):
        """
        Convert a value to bytes.
        """
        # Example conversion; adjust as needed for specific data types and precision
        value = int(value * (10 ** 7)) if dtype == 'float32' else value
        return value.to_bytes(length, byteorder, signed=signed)

    def send_data(self):
        """
        Sends prepared data to the CAN bus.
        """
        data_bytes = self.prepare_data()
        pdu = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=data_bytes)

        try:
            self.bus.send(pdu)
            print("Message sent")
        except can.CanError as e:
            print(f"Message NOT sent: {e}")

    def execute(self):
        """
        Public method to trigger sending data.
        """
        self.send_data()

    def shutdown_bus(self):
        """
        Safely shutdown the CAN bus.
        """
        self.bus.shutdown()
