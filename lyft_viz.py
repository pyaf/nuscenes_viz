import argparse
import psutil
import numpy as np
from pyquaternion import Quaternion
from lyft_dataset_sdk.lyftdataset import LyftDataset
from lyft_dataset_sdk.utils.data_classes import LidarPointCloud
from lyft_dataset_sdk.utils.geometry_utils import view_points
import mayavi.mlab as mlab
from utils import draw_lidar, draw_gt_boxes3d


def get_lidar_points(lyftdata, lidar_token):
    '''Get lidar point cloud in the frame of the ego vehicle'''
    sd_record = lyftdata.get("sample_data", lidar_token)
    sensor_modality = sd_record["sensor_modality"]

    # Get aggregated point cloud in lidar frame.
    sample_rec = lyftdata.get("sample", sd_record["sample_token"])
    chan = sd_record["channel"]
    ref_chan = "LIDAR_TOP"
    pc, times = LidarPointCloud.from_file_multisweep(
        lyftdata, sample_rec, chan, ref_chan, num_sweeps=1
    )
    # Compute transformation matrices for lidar point cloud
    cs_record = lyftdata.get("calibrated_sensor", sd_record["calibrated_sensor_token"])
    pose_record = lyftdata.get("ego_pose", sd_record["ego_pose_token"])
    vehicle_from_sensor = np.eye(4)
    vehicle_from_sensor[:3, :3] = Quaternion(cs_record["rotation"]).rotation_matrix
    vehicle_from_sensor[:3, 3] = cs_record["translation"]

    ego_yaw = Quaternion(pose_record["rotation"]).yaw_pitch_roll[0]
    rot_vehicle_flat_from_vehicle = np.dot(
        Quaternion(scalar=np.cos(ego_yaw / 2), vector=[0, 0, np.sin(ego_yaw / 2)]).rotation_matrix,
        Quaternion(pose_record["rotation"]).inverse.rotation_matrix,
    )
    vehicle_flat_from_vehicle = np.eye(4)
    vehicle_flat_from_vehicle[:3, :3] = rot_vehicle_flat_from_vehicle
    points = view_points(
        pc.points[:3, :], np.dot(vehicle_flat_from_vehicle, vehicle_from_sensor), normalize=False
    )
    return points



def plot_lidar_with_depth(lyftdata, sample):
    '''plot given sample'''

    print(f'Plotting sample, token: {sample["token"]}')
    lidar_token = sample["data"]["LIDAR_TOP"]
    pc = get_lidar_points(lyftdata, lidar_token)
    _, boxes, _ = lyftdata.get_sample_data(
        lidar_token, flat_vehicle_coordinates=True
    )
    fig = mlab.figure(figure=None, bgcolor=(0,0,0),
                      fgcolor=None, engine=None, size=(1000, 500))

    # plot lidar points
    draw_lidar(pc.T, fig=fig)

    # plot boxes one by one
    for box in boxes:
        corners = view_points(box.corners(), view=np.eye(3), normalize=False)
        draw_gt_boxes3d([corners.T], fig=fig, color=(0, 1, 0))
    mlab.show(1)


def plot_one_sample(lyftdata, sample_token):
    ''' plots only one sample's top lidar point cloud '''
    sample = lyftdata.get('sample', sample_token)
    plot_lidar_with_depth(lyftdata, sample)
    input_str=input('Press any key to terminate \n')
    mlab.close()
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()


def plot_one_scene(lyftdata, scene_token):
    scene = lyftdata.get('scene', scene_token)
    token = scene['first_sample_token']
    while token != '':
        sample = lyftdata.get('sample', token)
        plot_lidar_with_depth(lyftdata, sample)
        token = sample['next']
        input_str=input('Press any key to continue to next sample, enter "kill" to terminate \n')
        mlab.close()
        for proc in psutil.process_iter():
            if proc.name() == "display":
                proc.kill()

        if input_str == "kill":
            break




if __name__=='__main__':
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Mayavi visualization of nuscenes dataset')
    parser.add_argument('-d', '--dataroot', type=str, default="./data/lyft/", metavar='N',
                        help='data directory path  (default: ./data/lyft/)')
    parser.add_argument('--scene', type=str, default=None, metavar='N', help='scene token')
    parser.add_argument('--sample', type=str, default=None, metavar='N', help='sample token')

    args = parser.parse_args()
    dataroot = Path(args.dataroot)
    json_path = dataroot / 'data/'
    print('Loading dataset with Lyft SDK ...')
    lyftdata = LyftDataset(data_path=str(dataroot), json_path=str(json_path), verbose=True)
    print('Done!, starting 3d visualization ...')

    if args.scene:
        plot_one_scene(lyftdata, args.scene)
    elif args.sample:
        plot_one_sample(lyftdata, args.sample)
