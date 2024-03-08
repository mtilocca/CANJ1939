import multiprocessing
from dataRetrieve import dataRetrieve
from DataToCan import DataToCan
from CoG import CoG
from MultiPacket import MultiPacket
import time

class CanBusSystem:
    def __init__(self):
        self.counter = 0  # Sequence ID counter
        self.dataSet = dataRetrieve()

        # Define PGNs and IDs
        self.PGNs = [0x0000, 0x0000, 0x0000]  # Example PGNs
        self.IDs = [0, 0, 0]

        # Initialize CAN messages
        self.initialize_messages()

    def initialize_messages(self):
        """Initialize the objects corresponding to the CAN messages."""
        Wgs84 = self.dataSet.retrieve(['lat', 'lon'])
        Ypr = self.dataSet.retrieve(['yaw', 'pitch', 'roll'])
        CoG_Data = self.dataSet.retrieve(['yaw', 'Speed'])
        MultiData = self.dataSet.retrieve(['lat', 'lon', 'h'])

        self.MsgWGS = DataToCan(Wgs84, self.IDs[2], False, False, self.PGNs[1], 2)
        self.MsgYPR = DataToCan(Ypr, self.IDs[0], False, True, self.PGNs[0], 3)
        self.MsgCoG = CoG(CoG_Data, self.IDs[1], self.PGNs[2], 7)
        self.MsgMulti = MultiPacket(MultiData)

    def seq_id(self):
        """Update and return the new sequence ID."""
        self.counter = (self.counter + 1) % 252  # Loop back after 251
        return self.counter

    def execute_messages(self, counter):
        """Send CAN messages based on the current sequence ID."""
        # This method now only prepares the messages and returns them
        # Actual sending will be handled in parallel
        messages = [self.MsgWGS, self.MsgYPR, self.MsgCoG]
        for msg in messages:
            msg.prepare(counter)  # Assume a prepare method that sets up the message
        return messages

    def send_message(self, message):
        """Function to send a single CAN message."""
        message.execute()

    def run(self):
        """Main loop for sending CAN messages using multiprocessing."""
        try:
            start_time = time.time()
            with multiprocessing.Pool() as pool:
                while True:
                    if time.time() - start_time >= 1:
                        self.counter = self.seq_id()  # Update counter once per second
                        messages = self.execute_messages(self.counter)
                        # Use pool.map or pool.apply_async to send messages in parallel
                        pool.map(self.send_message, messages)
                        start_time = time.time()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Shut down CAN bus interfaces properly."""
        print("CAN bus interfaces have been shut down.")
        # Implement actual shutdown logic as needed

if __name__ == "__main__":
    can_bus_system = CanBusSystem()
    can_bus_system.run()
