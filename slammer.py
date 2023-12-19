from ouster import client
from ouster.mapping.slam import KissBackend
import numpy as np
from ouster import client
from ouster.pcap import Pcap
import ouster.osf as osf
from ouster.sdkx.parsing import default_scan_fields
from ouster.sdk.util import resolve_metadata
import ipaddress
from functools import partial
from ouster.viz import SimpleViz, ScansAccumulator

# establish sensor connection
hostname = 'os-122251002135.local'
LIDAR_PORT = 7502
imu_port = 7503


def load_source(source):
    if source.endswith('.pcap'):
        metadata = open(resolve_metadata(source), "r").read()
        info = client.SensorInfo(metadata)
        pcap = Pcap(source, info)
        fields = default_scan_fields(info.format.udp_profile_lidar, flags=True)
        scans = client.Scans(pcap, fields=fields)
    elif source.endswith('.osf'):
        scans = osf.Scans(source)
        info = scans.metadata
    elif source.endswith('.local') or ipaddress.ip_address(source):
        scans = client.Scans.stream(hostname=source, lidar_port=LIDAR_PORT, complete=False, timeout=1)
        info = scans.metadata
    else:
        raise ValueError("Not a valid source type")

    return scans, info


pcap_path = '/home/ubuntu/ouster/LiDAR_first/OS-1-64-U02_122251002135_1024x10_20231207_114639.pcap'

scans, info = load_source(pcap_path)

# scans, info = load_source('os-122251002135.local')

slam = KissBackend(info, max_range=75, min_range=1, voxel_size=1.0)
last_scan_pose = np.eye(4)

scans_w_poses = map(partial(slam.update), scans)
scans_acc = ScansAccumulator(info,
                             accum_max_num=10,
                             accum_min_dist_num=1,
                             map_enabled=True,
                             map_select_ratio=0.01)

SimpleViz(info, scans_accum=scans_acc, rate=0.0).run(scans_w_poses)

for idx, scan in enumerate(scans):
    scan_w_poses = slam.update(scan)
    col = client.first_valid_column(scan_w_poses)
    # scan_w_poses.pose is a list where each pose represents a column points' pose.
    # use the first valid scan's column pose as the scan pose
    scan_pose = scan_w_poses.pose[col]
    print(f"idx = {idx} and Scan Pose {scan_pose}")

    # calculate the inverse transformation of the last scan pose
    inverse_last = np.linalg.inv(last_scan_pose)
    # calculate the pose difference by matrix multiplication
    pose_diff = np.dot(inverse_last, scan_pose)
    # extract rotation and translation
    rotation_diff = pose_diff[:3, :3]
    translation_diff = pose_diff[:3, 3]
    print(f"idx = {idx} and Rotation Difference: {rotation_diff}, "
          f"Translation Difference: {translation_diff}")
