"""
Launch gscam2 to receive Pepper's front camera GStreamer stream.

The Pepper robot streams its front camera via UDP/RTP/JPEG on port 3000.
This launch file consumes that stream and publishes it as a ROS 2 topic,
using the URDF-standard frame name so it integrates with naoqi_driver2's TF tree.

Before launching this, start the stream on the robot:
    ssh nao@172.29.111.240 '~/start_camera.sh'
And after shutting this down, stop it:
    ssh nao@172.29.111.240 '~/stop_camera.sh'

Topics published:
    /pepper/front/image_raw      (sensor_msgs/Image)
    /pepper/front/camera_info    (sensor_msgs/CameraInfo)

QoS: Best Effort. Set viewers (rqt_image_view, RViz2) to Best Effort.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

# Calibration file for Pepper's front camera (run camera_calibration to generate it)
camera_info_url = 'file://' + os.path.join(
    get_package_share_directory('gscam2'), 'cfg', 'pepper_front_calibration.yaml')


def generate_launch_description():
    front_pipeline = (
        "udpsrc port=3000 ! "
        "application/x-rtp,encoding-name=JPEG,payload=26 ! "
        "rtpjpegdepay ! jpegdec ! videoconvert"
    )

    gscam_node = Node(
        package='gscam2',
        executable='gscam_main',
        name='pepper_front_camera',
        output='screen',
        parameters=[{
            'gscam_config': front_pipeline,
            'frame_id': 'CameraTop_optical_frame',
            'camera_name': 'pepper_front',
            'camera_info_url': camera_info_url,
            'use_gst_timestamps': False,
            'sync_sink': False,
            'preroll': False,
        }],
        remappings=[
            ('image_raw', '/pepper/front/image_raw'),
            ('camera_info', '/pepper/front/camera_info'),
        ],
    )

    return LaunchDescription([gscam_node])
