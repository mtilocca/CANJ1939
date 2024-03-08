import numpy as np
import j1939
import datetime
import json  # Import json module

class MultiPacket:
    def __init__(self, dataArray, column_indices_file='column_indices.json'):
        self.dataArray = dataArray
        # Load column indices from a JSON file
        with open(column_indices_file, 'r') as file:
            self.column_indices = json.load(file)
        self.pgn = j1939.PGN(0x0000)  # Change this with your PGN
        self.bus = j1939.Bus(channel=0, bustype='kvaser', timeout=0.01, broadcast=True, bitrate=250000)
        self.aid = j1939.ArbitrationID(pgn=self.pgn, source_address=0x14, destination_address=0xFF, priority=3)
        self.posDate = self.calculate_pos_date()
        self.ctrl = 0

    def calculate_pos_date(self):
        today = datetime.date.today()
        ref = datetime.date(1970, 1, 1)
        days = (today - ref).days
        return list(days.to_bytes(2, 'little', signed=False))

    def prepare_data_payload(self, seqID):
        """
        Prepares the data payload for the multipacket message.
        This is where you use column_indices to select specific fields.
        """
        static_payload = [seqID] + self.posDate
        # Example of adding specific fields based on column_indices
        for column, index in self.column_indices.items():
            value = self.dataArray.iloc[-1, index]  # Get the last row's value for each column
            # Convert value to bytes and add to payload as needed
            # This is a placeholder - adjust conversion based on your data's needs

        return static_payload
    
    def send_multipacket(self, payload):
        """
        Sends a multipacket message.
        """
        for i, part in enumerate(self.chunk_payload(payload, 7)):
            frame_count = (self.ctrl * 32 + i) & 0xFF
            pdu_data = [frame_count] + part
            pdu = j1939.PDU(timestamp=0.0, arbitration_id=self.aid, data=pdu_data)
            try:
                self.bus.send(pdu)
                print("Multipacket message part sent")
            except can.CanError as e:
                print(f"Multipacket message part NOT sent: {e}")

        self.ctrl = (self.ctrl + 1) % 8  # Update control for next message sequence

    @staticmethod
    def chunk_payload(payload, chunk_size):
        """
        Splits the payload into chunks of specified size.
        """
        return [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]

    def execute(self, seqID):
        """
        The main method to trigger the multipacket sending process.
        """
        payload = self.prepare_data_payload(seqID)
        self.send_multipacket(payload)