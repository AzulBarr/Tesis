#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_msgs.msg import TFMessage
from math import pi
import tf_transformations

class IntelDatasetNode(Node):

    def __init__(self):
        super().__init__('intel_dataset_node')

        self.scan_pub = self.create_publisher(LaserScan, '/base_scan', 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom_combined', 10)
        self.tf_pub = self.create_publisher(TFMessage, '/tf', 10)

        self.file = open('intel.clf', 'r')

        # timer para simular tiempo
        self.timer = self.create_timer(0.05, self.process_line)

        self.static_tf_sent = False

    def process_line(self):
        line = self.file.readline()

        if not line:
            self.get_logger().info("Fin del dataset")
            self.timer.cancel()
            return

        tokens = line.strip().split()

        if len(tokens) < 2:
            return

        if tokens[0] != 'FLASER':
            return

        num_scans = int(tokens[1])

        if num_scans != 180:
            return

        # -------------------------
        # LaserScan
        # -------------------------
        ranges = []
        raw_ranges = tokens[2:2 + num_scans]

        for r in raw_ranges:
            val = float(r)
            # if val < 0.1 or val > 80.0:
            #     val = float('inf')
            ranges.append(val)

        # pose odometry
        x = float(tokens[5 + num_scans])
        y = float(tokens[6 + num_scans])
        theta = float(tokens[7 + num_scans])

        t = self.get_clock().now().to_msg()

        # LaserScan msg
        scan = LaserScan()
        scan.header.stamp = t
        scan.header.frame_id = 'laser_link'
        scan.angle_min = -pi/2
        scan.angle_max = pi/2
        scan.angle_increment = pi / (num_scans-1)
        scan.range_min = 0.1
        scan.range_max = 81.3
        scan.ranges = ranges

        self.scan_pub.publish(scan)

        # -------------------------
        # 🚗 Odometry
        # -------------------------
        odom = Odometry()
        odom.header.stamp = t
        odom.header.frame_id = 'odom_combined'
        odom.child_frame_id = 'base_footprint'

        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y

        q = tf_transformations.quaternion_from_euler(0, 0, theta)
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]

        self.odom_pub.publish(odom)

        # -------------------------
        # 🔁 TF: odom → base_link
        # -------------------------
        tf_msg = TFMessage()

        trans = TransformStamped()
        trans.header.stamp = t
        trans.header.frame_id = 'odom_combined'
        trans.child_frame_id = 'base_footprint'
        trans.transform.translation.x = x
        trans.transform.translation.y = y
        trans.transform.translation.z = 0.0

        trans.transform.rotation.x = q[0]
        trans.transform.rotation.y = q[1]
        trans.transform.rotation.z = q[2]
        trans.transform.rotation.w = q[3]

        tf_msg.transforms.append(trans)

        # -------------------------
        # 🔒 TF estático base_footprint → laser_link
        # -------------------------
        if not self.static_tf_sent:
            static_tf = TransformStamped()
            static_tf.header.stamp = t
            static_tf.header.frame_id = 'base_footprint'
            static_tf.child_frame_id = 'laser_link'
            static_tf.transform.rotation.w = 1.0

            tf_msg.transforms.append(static_tf)
            self.static_tf_sent = True

        self.tf_pub.publish(tf_msg)


def main():
    rclpy.init()
    node = IntelDatasetNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()