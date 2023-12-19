import os

import cv2
import numpy as np
from contextlib import closing
from ouster import client
from ouster import pcap

metadata_path = '/home/ubuntu/ouster/ouster/data/al-wadi-vehicles/'
img_path = '/home/ubuntu/ouster/ouster/data/al-wadi-vehicles-range/'

# Iterate through each file in the metadata_path
for filename in os.listdir(metadata_path):
    if filename.endswith('.json'):  # Assuming you want to process only JSON files
        json_file_path = os.path.join(metadata_path, filename)
        pcap_file_path = os.path.join(metadata_path, filename.replace('.json', '.pcap'))

        with open(json_file_path, 'r') as f:
            # Extract the desired value from the file path
            value_to_extract = os.path.splitext(os.path.basename(json_file_path))[0]

            # Create a folder with the extracted value in the img_path
            folder_path = os.path.join(img_path, value_to_extract)

            # Check if the folder already exists, if not, create it
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Folder '{value_to_extract}' created successfully in '{img_path}'.")
            else:
                print(f"Folder '{value_to_extract}' already exists in '{img_path}'.")

            metadata = client.SensorInfo(f.read())
            # current_fov = client.SensorInfo(f.read()).config['beam_azimuth_angles']
            source = pcap.Pcap(pcap_file_path, metadata)
            counter = 0
            with closing(client.Scans(source)) as scans:
                for scan in scans:
                    counter += 1
                    ref_field = scan.field(client.ChanField.RANGE)
                    ref_val = client.destagger(source.metadata, ref_field)
                    ref_img = ref_val.astype(np.uint8)
                    filename = folder_path + '/extract' + str(counter) + '.jpg'
                    cv2.imwrite(filename, ref_img)
