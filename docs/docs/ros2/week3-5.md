---
sidebar_position: 3
title: 'Weeks 3-5: ROS 2 Fundamentals'
---

# Weeks 3-5: ROS 2 Fundamentals

## Learning Outcomes

By the end of these three weeks, students will be able to:

- Understand the architecture and core concepts of ROS 2
- Create and manage ROS 2 packages, nodes, topics, and services
- Implement message passing and service communication between nodes
- Configure and launch complex robotic systems using launch files
- Design distributed robotic applications using ROS 2's client libraries
- Integrate sensor data processing with ROS 2 nodes and actions

## Overview

These weeks focus on the Robot Operating System 2 (ROS 2), the middleware framework that enables communication and coordination between different components of a robotic system. We'll explore ROS 2's architecture, programming interfaces, and best practices for building robust robotic applications.

### Why ROS 2?

ROS 2 represents a significant evolution from the original ROS framework, addressing key limitations such as:

- **Real-time capabilities**: Support for real-time systems and deterministic behavior
- **Security**: Built-in security features including authentication, authorization, and encryption
- **Distributed systems**: Better support for multi-robot systems and edge computing
- **Professional deployment**: Production-ready features for commercial applications

### Core ROS 2 Concepts

#### Nodes
Nodes are the fundamental execution units in ROS 2. Each node typically performs a specific task and communicates with other nodes through topics, services, or actions.

#### Topics and Publishers/Subscribers
Topics enable asynchronous, one-way communication between nodes using a publish-subscribe pattern. Publishers send messages to topics, while subscribers receive messages from topics.

#### Services and Clients
Services provide synchronous, request-response communication between nodes. A client sends a request to a service and waits for a response.

#### Actions
Actions provide goal-oriented communication with feedback and status updates. They're ideal for long-running tasks with intermediate results.

## Core Concepts

### 1. ROS 2 Architecture

ROS 2 uses the Data Distribution Service (DDS) as its underlying communication middleware. This provides:

- **Discovery**: Automatic discovery of nodes and their interfaces
- **Communication**: Reliable message delivery between nodes
- **Quality of Service (QoS)**: Configurable policies for message delivery (reliability, durability, etc.)

### 2. Client Libraries

ROS 2 supports multiple client libraries:
- **rclcpp**: C++ client library
- **rclpy**: Python client library (used in this course)
- **rclrs**: Rust client library
- **rclc**: C client library

### 3. Package Management

ROS 2 packages are organized using the ament build system and contain:

- **package.xml**: Package manifest with dependencies and metadata
- **CMakeLists.txt**: Build configuration for C++ packages
- **setup.py**: Python package configuration
- **src/**: Source code files
- **launch/**: Launch files for system configuration
- **config/**: Configuration files
- **test/**: Unit and integration tests

## Practical Implementation with ROS 2

### Creating a Basic ROS 2 Node

Let's create a simple ROS 2 node that demonstrates the publish-subscribe pattern:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
import random

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')

        # Create publisher for robot commands
        self.command_publisher = self.create_publisher(String, 'robot_commands', 10)

        # Create subscriber for sensor data
        self.sensor_subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10
        )

        # Timer to periodically send commands
        self.timer = self.create_timer(0.5, self.send_command)

        self.get_logger().info('Robot controller initialized')

    def scan_callback(self, msg):
        """Process incoming laser scan data"""
        # Find the minimum distance in the scan
        if len(msg.ranges) > 0:
            valid_ranges = [r for r in msg.ranges if r != float('inf')]
            if valid_ranges:
                min_distance = min(valid_ranges)
                self.get_logger().info(f'Minimum distance: {min_distance:.2f}m')

    def send_command(self):
        """Send random movement commands"""
        commands = ['FORWARD', 'LEFT', 'RIGHT', 'STOP']
        command = random.choice(commands)

        msg = String()
        msg.data = command
        self.command_publisher.publish(msg)
        self.get_logger().info(f'Published command: {command}')

def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()

    try:
        rclpy.spin(robot_controller)
    except KeyboardInterrupt:
        pass
    finally:
        robot_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Creating a Service Server

Here's an example of implementing a ROS 2 service:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {request.a} + {request.b} = {response.sum}')
        return response

def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()

    try:
        rclpy.spin(minimal_service)
    except KeyboardInterrupt:
        pass
    finally:
        minimal_service.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Labs and Mini-Projects

### Lab 2: ROS 2 Node Communication
- **Objective**: Implement and test different communication patterns in ROS 2
- **Tasks**:
  1. Create publisher and subscriber nodes for sensor data
  2. Implement a service for robot navigation commands
  3. Create an action server for path planning
  4. Test communication reliability under various conditions
  5. Analyze Quality of Service (QoS) settings and their effects

### Mini-Project 2: Distributed Sensor Network
- **Objective**: Build a distributed system with multiple ROS 2 nodes
- **Tasks**:
  1. Create nodes for different sensor types (camera, LIDAR, IMU)
  2. Implement a central fusion node that processes all sensor data
  3. Design a visualization node to display the fused information
  4. Test the system with simulated robot data
  5. Evaluate system performance and reliability

## Key Readings and Resources

### Academic Papers
1. Quigley, M., et al. (2009). ROS: an open-source Robot Operating System. *ICRA Workshop on Open Source Software*, 3(3.2), 5.
2. Macenski, S., et al. (2022). ROS 2: Next generation robot middleware. *IEEE Robotics & Automation Magazine*, 29(1), 104-115.
3. Dornhege, C., et al. (2013). The skill layer: A domain-specific component model for robotic behavior. *IEEE Transactions on Robotics*, 29(6), 1463-1475.

### Technical Documentation
- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [ROS 2 Design](https://design.ros2.org/)

## Summary

Weeks 3-5 have established the foundation for ROS 2 development, covering its architecture, core concepts, and practical implementation. Students should now understand:

- The fundamental differences between ROS 1 and ROS 2
- How to create and manage ROS 2 packages and nodes
- Different communication patterns available in ROS 2
- Best practices for building distributed robotic systems

The next weeks will focus on simulation environments that allow us to test and validate our ROS 2 implementations in virtual worlds before deploying them to physical robots.