import numpy as np
import pandas as pd
import can
import j1939
import os
import time

class DataToCan:
    def __init__(self, dataArray, canID, recorded, seqID, PGN, priority):
        self.dataArray = dataArray
        self.recorded = recorded
        self.canID = canID
        self.seqIDctrl = seqID
        self.pgn = j1939.PGN(PGN)
        self.priority = priority
        self.aid = j1939.ArbitrationID(pgn=self.pgn, source_address=0x14, destination_address=0xFF, priority=priority)

        # Assuming a single bus for simplicity; adjust as needed for your setup
        self.bus = j1939.Bus(channel=0, bustype='kvaser', timeout=0.01, broadcast=True, bitrate=250000)

        # Column name to index mapping
        self.column_indices = {value: idx for idx, value in enumerate(dataArray.columns)}

    def _get_latest_data(self):
        """Retrieve the latest row from the data array."""
        return self.dataArray.tail(1).iloc[0]

    def _prepare_data(self, seq=None):
        """Prepare data for sending, including sequence ID if applicable."""
        latest_data = self._get_latest_data()

        # Example of preparing data; adjust according to your data format and requirements
        data_bytes = []
        for col in self.dataArray.columns:
            value = latest_data[col]
            data_bytes.extend(self._value_to_bytes(value))

        if self.seqIDctrl and seq is not None:
            # Prepend or append sequence ID to data_bytes as required
            seq_bytes = self._value_to_bytes(seq, byteorder='big', length=1)  # Adjust as per your sequence ID format
            data_bytes = seq_bytes + data_bytes

        return data_bytes

    @staticmethod
    def _value_to_bytes(value, dtype='float32', byteorder='little', signed=True, length=4):
        """Convert a value to bytes."""
        if dtype == 'float32':
            value = int(value * (10 ** 7))  # Example scaling; adjust as needed
        return value.to_bytes(length, byteorder, signed=signed)

    def send_data(self, seq=None):
        """Send data to the CAN bus."""
        data_bytes = self._prepare_data(seq)
        pdu = j1939.PDU(timestamp=time.time(), arbitration_id=self.aid, data=data_bytes)
        try:
            self.bus.send(pdu)
            print("Message sent")
        except can.CanError as e:
            print(f"Message NOT sent: {e}")

    def execute(self, seq=None):
        """Public method to trigger sending data."""
        self.send_data(seq)

    def shutdown_bus(self):
        """Shutdown the CAN bus safely."""
        self.bus.shutdown()
