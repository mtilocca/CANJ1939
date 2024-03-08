from multiprocessing import Process
import time
from dataRetrieve import dataRetrieve
from DataToCan import DataToCan
from CoG import CoG
from MultiPacket import MultiPacket

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

    def send_message(self, message, counter):
        """Function to send a single message, intended to be used in a separate process."""
        message.execute(counter)

    def execute_messages(self):
        """Execute CAN messages in parallel."""
        processes = []
        # Prepare processes for each message that needs to be sent
        processes.append(Process(target=self.send_message, args=(self.MsgWGS, None)))
        processes.append(Process(target=self.send_message, args=(self.MsgYPR, self.counter)))
        processes.append(Process(target=self.send_message, args=(self.MsgCoG, self.counter)))

        # Start all processes
        for process in processes:
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

    def run(self):
        """Main loop for sending CAN messages."""
        try:
            start_time = time.time()
            while True:
                if time.time() - start_time >= 1:
                    self.counter = self.seq_id()  # Update counter once per second
                    self.MsgMulti.execute(self.counter)  # Send multipacket once per second
                    start_time = time.time()

                self.execute_messages()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Shut down CAN bus interfaces properly."""
        self.MsgWGS.shutBus()
        self.MsgYPR.shutBus()
        self.MsgCoG.shutBus()
        print("CAN bus interfaces have been shut down.")

if __name__ == "__main__":
    can_bus_system = CanBusSystem()
    can_bus_system.run()
