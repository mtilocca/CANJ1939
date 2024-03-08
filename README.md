# CAN - J1939 Communication

This repository demonstrates the process of sending single and multipacket messages to a CAN bus, adhering to the J1939 standard. The implementation is based on the framework provided by [python-j1939](https://github.com/milhead2/python-j1939).

## Overview

The code facilitates communication over a CAN network by:

- **Data Retrieval:** Extracting data from a `.txt` file, organizing it based on the column names specified within the file.
- **Message Initialization:** Setting up objects that represent the various messages to be sent over the CAN network.
- **Continuous Streaming:** Utilizing a while loop to stream and dispatch data to the CAN bus in real time.

Key features include the ability to utilize custom counters frequently employed in J1939 payloads, and the capability to dispatch multipacket messages pertinent to the GNSS connectivity of the system or simulator in use.

Currently, the implementation supports sending messages that convey information such as the vehicle's yaw-pitch-roll position, its speed and course over ground, and its GNSS RTK corrected positioning.

## Installation

To install the required dependencies, download the `requirements.txt` file and execute the following command in your terminal:

```sh
pip install -r requirements.txt
```

## Hardware Requirements

To enable communication between your computer and the embedded device using CANJ1939, a **USB to CAN adapter** is required. This adapter serves as the crucial link for transmitting and receiving CAN messages.

Ensure that the adapter is compatible with your system and properly installed before attempting to run the code in this repository.
