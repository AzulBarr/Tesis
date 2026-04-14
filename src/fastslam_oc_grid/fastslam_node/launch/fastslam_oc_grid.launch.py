import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1. Definir los argumentos que se pueden pasar por terminal o XML
    # Esto reemplaza tu función get_launch_arguments()
    declare_fastslam_prefix_cmd = DeclareLaunchArgument(
        'fastslam_prefix',
        default_value='',
        description='Set of commands to precede the node (e.g. "valgrind" or "gdb")'
    )

    # 2. Definir la referencia al valor del argumento
    # Esto es lo que se inyecta en el campo 'prefix' del nodo
    slam_prefix = LaunchConfiguration('slam_prefix')

    fastslam_node = Node(
        package="fastslam_node",  
        executable="fastslam_node", 
        name="fastslam_oc_grid",
        output="screen",
        parameters=[{
            "use_sim_time": True,
            "num_particles": 500,
            "odom_frame": "odom_combined", 
            "base_frame": "base_footprint", 
            "publish_trajectory": False,
        }],
        arguments=["--ros-args", "--log-level", "WARN"],
        remappings=[
            ("/scan", "/base_scan"), # para el bag del MIT
        ],
        #prefix=LaunchConfiguration('slam_prefix') # para el bag de Beluga
    )

    return LaunchDescription([
        declare_fastslam_prefix_cmd,
        fastslam_node
    ])

'''
MIT bag y Intel Dataset:
"odom_frame": "odom_combined", 
"base_frame": "base_footprint",

("/scan", "/base_scan")

ROSbag de Beluga:
"odom_frame": "odom",
"base_frame": "base",

prefix=LaunchConfiguration('slam_prefix')
'''