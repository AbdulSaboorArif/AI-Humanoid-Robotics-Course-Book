#!/usr/bin/env python3
"""
Autonomous Humanoid Robot Controller for Capstone Project
Implements the main control logic for the capstone project robot
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan, Imu
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np
import json
from typing import Dict, List, Tuple, Optional

class AutonomousRobot(Node):
    """
    Main robot controller that integrates perception, navigation, manipulation,
    and natural language processing for the capstone project.
    """

    def __init__(self):
        super().__init__('autonomous_robot')

        # Initialize CV Bridge for image processing
        self.bridge = CvBridge()

        # Robot state
        self.current_pose = None
        self.current_scan = None
        self.current_image = None
        self.current_imu = None
        self.battery_level = 100.0
        self.is_operational = True

        # Task planning state
        self.current_task = None
        self.task_queue = []
        self.action_plan = []

        # ROS 2 subscribers
        self.image_subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.scan_subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.imu_subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.command_subscription = self.create_subscription(
            String,
            '/natural_language_command',
            self.command_callback,
            10
        )

        # ROS 2 publishers
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.action_publisher = self.create_publisher(String, '/robot_action', 10)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)

        # Timer for main control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Autonomous Robot Controller initialized')

    def image_callback(self, msg):
        """Process incoming camera images"""
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def scan_callback(self, msg):
        """Process incoming LIDAR scan data"""
        self.current_scan = msg

    def imu_callback(self, msg):
        """Process incoming IMU data for balance and orientation"""
        self.current_imu = msg

    def command_callback(self, msg):
        """Process natural language commands"""
        command = msg.data
        self.get_logger().info(f'Received command: {command}')

        # Parse and process the command
        action_plan = self.parse_natural_language_command(command)

        if action_plan:
            self.execute_action_plan(action_plan)
        else:
            self.get_logger().warn(f'Could not parse command: {command}')

    def parse_natural_language_command(self, command: str) -> Optional[List[Dict]]:
        """
        Parse natural language command and generate action plan
        This is a simplified implementation - in practice, this would use NLP/LLM
        """
        command_lower = command.lower()

        # Simple rule-based parsing for demonstration
        if 'go to' in command_lower or 'move to' in command_lower:
            # Extract location
            location = self.extract_location(command_lower)
            if location:
                return [{'action': 'NAVIGATE', 'target': location}]

        elif 'pick up' in command_lower or 'grasp' in command_lower:
            # Extract object
            obj = self.extract_object(command_lower)
            if obj:
                return [
                    {'action': 'NAVIGATE', 'target': f'NEAR_{obj.upper()}'},
                    {'action': 'GRASP', 'object': obj}
                ]

        elif 'bring' in command_lower and 'to' in command_lower:
            # Complex command: bring X to Y
            obj = self.extract_object(command_lower)
            dest = self.extract_location(command_lower)
            if obj and dest:
                return [
                    {'action': 'NAVIGATE', 'target': f'NEAR_{obj.upper()}'},
                    {'action': 'GRASP', 'object': obj},
                    {'action': 'NAVIGATE', 'target': dest},
                    {'action': 'PLACE', 'target': dest}
                ]

        # Default response for unrecognized commands
        return None

    def extract_location(self, command: str) -> Optional[str]:
        """Extract location from command"""
        locations = ['kitchen', 'bedroom', 'living room', 'office', 'dining room', 'bathroom']
        for loc in locations:
            if loc in command:
                return loc.upper().replace(' ', '_')
        return None

    def extract_object(self, command: str) -> Optional[str]:
        """Extract object from command"""
        objects = ['cup', 'book', 'ball', 'box', 'bottle', 'apple', 'phone']
        for obj in objects:
            if obj in command:
                return obj
        return None

    def execute_action_plan(self, plan: List[Dict]):
        """Execute a sequence of actions"""
        self.action_plan = plan
        self.get_logger().info(f'Executing action plan with {len(plan)} steps')

        # Publish the plan to the action system
        plan_msg = String()
        plan_msg.data = json.dumps(plan)
        self.action_publisher.publish(plan_msg)

    def control_loop(self):
        """Main control loop"""
        if not self.is_operational:
            return

        # Check robot status
        self.check_robot_status()

        # Execute next action in plan if available
        if self.action_plan:
            next_action = self.action_plan[0]
            self.execute_single_action(next_action)

            # Remove completed action from plan
            if self.is_action_completed(next_action):
                self.action_plan.pop(0)

                if not self.action_plan:
                    self.get_logger().info('Action plan completed')
                    # Publish completion status
                    status_msg = String()
                    status_msg.data = json.dumps({
                        'status': 'completed',
                        'battery': self.battery_level
                    })
                    self.status_publisher.publish(status_msg)

    def execute_single_action(self, action: Dict):
        """Execute a single action"""
        action_type = action.get('action')

        if action_type == 'NAVIGATE':
            self.navigate_to_location(action.get('target'))
        elif action_type == 'GRASP':
            self.grasp_object(action.get('object'))
        elif action_type == 'PLACE':
            self.place_object(action.get('target'))
        else:
            self.get_logger().warn(f'Unknown action type: {action_type}')

    def is_action_completed(self, action: Dict) -> bool:
        """Check if an action is completed"""
        # This is a simplified check - in practice, you'd have more sophisticated completion detection
        return True  # Placeholder - implement based on actual robot feedback

    def navigate_to_location(self, location: str):
        """Navigate to a specific location"""
        self.get_logger().info(f'Navigating to {location}')

        # In a real implementation, this would interface with navigation stack
        # For now, we'll just publish a simple movement command
        cmd = Twist()
        cmd.linear.x = 0.5  # Move forward
        cmd.angular.z = 0.0  # No rotation
        self.cmd_vel_publisher.publish(cmd)

    def grasp_object(self, obj: str):
        """Grasp an object"""
        self.get_logger().info(f'Attempting to grasp {obj}')
        # In a real implementation, this would control robot arms/hands

    def place_object(self, location: str):
        """Place object at location"""
        self.get_logger().info(f'Placing object at {location}')
        # In a real implementation, this would control robot arms/hands

    def check_robot_status(self):
        """Check robot operational status"""
        # Simulate battery drain
        self.battery_level = max(0.0, self.battery_level - 0.01)

        if self.battery_level < 10.0:
            self.get_logger().warn('Battery level low!')
            self.is_operational = False

def main(args=None):
    rclpy.init(args=args)
    robot = AutonomousRobot()

    try:
        rclpy.spin(robot)
    except KeyboardInterrupt:
        robot.get_logger().info('Shutting down autonomous robot controller')
    finally:
        robot.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()