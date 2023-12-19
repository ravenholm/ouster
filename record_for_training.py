from contextlib import closing
from datetime import datetime

from more_itertools import nth, time_limited
from ouster import client, pcap
import cv2
import numpy as np

# establish sensor connection
hostname = 'os-122251002135.local'
lidar_port = 7502
imu_port = 7503

# connect to sensor and record lidar/imu packets
n_seconds = 90\

config = client.SensorConfig()

# set the values that you need: see sensor documentation for param meanings
config.operating_mode = client.OperatingMode.OPERATING_NORMAL
config.lidar_mode = client.LidarMode.MODE_1024x20
config.udp_port_lidar = 7502
config.udp_port_imu = 7503



with closing(client.Sensor(hostname, lidar_port, imu_port, buf_size=640)) as source:

    # make a descriptive filename for metadata/pcap files
    time_part = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta = source.metadata
    fname_base = f"{meta.prod_line}_{meta.sn}_{meta.mode}_{time_part}"
    print(f"Saving sensor metadata to: {fname_base}.json")
    source.write_metadata(f"{fname_base}.json")
    print(f"Writing to: {fname_base}.pcap (Ctrl-C to stop early)")
    source_it = time_limited(n_seconds, source)
    n_packets = pcap.record(source_it, f"{fname_base}.pcap")
    print(f"Captured {n_packets} packets")

