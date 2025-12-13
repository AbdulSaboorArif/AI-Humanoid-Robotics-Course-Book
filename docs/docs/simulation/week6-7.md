---
sidebar_position: 4
title: 'Weeks 6-7: Gazebo & Unity Simulation'
---

# Weeks 6-7: Gazebo & Unity Simulation

## Learning Outcomes

By the end of these two weeks, students will be able to:

- Understand the principles and applications of robot simulation environments
- Create and configure simulation worlds in both Gazebo and Unity
- Integrate ROS 2 with simulation environments for sensorimotor learning
- Implement physics-based robot models with accurate dynamics
- Design simulation scenarios for testing and training robotic systems
- Evaluate the fidelity and transferability of simulation-to-reality systems

## Overview

Simulation environments are crucial for developing and testing robotic systems safely and efficiently. This module explores two major simulation platforms: Gazebo, the standard for ROS-based robotics simulation, and Unity, which offers advanced graphics and physics capabilities for complex scenarios.

### The Role of Simulation in Robotics

Simulation serves several critical functions in robotics development:

- **Safety**: Test algorithms without risk to physical robots or humans
- **Cost-effectiveness**: Reduce hardware costs and accelerate development cycles
- **Repeatability**: Create controlled, reproducible testing conditions
- **Scalability**: Test multiple scenarios simultaneously in parallel simulations
- **Prototyping**: Validate concepts before physical implementation

### Simulation Fidelity and the Reality Gap

A key challenge in robotics simulation is the "reality gap" - the difference between simulated and real-world behavior. We'll explore techniques to maximize simulation fidelity while maintaining computational efficiency.

## Core Concepts

### 1. Gazebo Simulation

Gazebo is the standard simulation environment for ROS-based robotics, offering:

#### Physics Engine
- **ODE (Open Dynamics Engine)**: Fast, stable physics simulation
- **Bullet**: Alternative physics engine with different characteristics
- **Simbody**: Multi-body dynamics simulation for complex systems

#### Sensor Simulation
- **Camera sensors**: RGB, depth, and stereo vision simulation
- **LIDAR sensors**: 2D and 3D laser range finder simulation
- **IMU sensors**: Inertial measurement unit simulation
- **Force/torque sensors**: Contact force and joint torque simulation

#### Robot Modeling
- **URDF (Unified Robot Description Format)**: Robot structure and kinematics
- **SDF (Simulation Description Format)**: Simulation-specific properties
- **Gazebo plugins**: Custom simulation behaviors and interfaces

### 2. Unity Simulation

Unity provides advanced capabilities for robotics simulation:

#### Graphics and Visualization
- **High-fidelity rendering**: Photorealistic environments and materials
- **Lighting systems**: Dynamic and realistic lighting conditions
- **Post-processing effects**: Advanced visual enhancements

#### Physics Engine
- **PhysX**: NVIDIA's physics engine for realistic collision and dynamics
- **Custom physics**: Integration with specialized robotics physics

#### ROS Integration
- **Unity Robotics Hub**: Tools for ROS-Unity integration
- **ROS#**: C# ROS client library
- **Robotics Simulation Framework**: Pre-built robotics components

### 3. Simulation-to-Reality Transfer

Techniques for bridging the simulation-to-reality gap include:

#### Domain Randomization
- Varying environmental parameters during training
- Randomizing object textures, lighting, and physics properties
- Improving model robustness to real-world variations

#### System Identification
- Measuring real robot dynamics and parameters
- Calibrating simulation models to match real behavior
- Iterative refinement of simulation accuracy

## Practical Implementation with Gazebo

### Creating a Basic Gazebo World

Here's an example of a simple Gazebo world file:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="simple_world">
    <!-- Include a ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Include a sun light -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Create a simple box obstacle -->
    <model name="box">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
            <specular>1 0 0 1</specular>
          </material>
        </visual>
      </link>
    </model>

    <!-- Create a simple robot -->
    <model name="simple_robot">
      <pose>0 0 0.5 0 0 0</pose>
      <link name="chassis">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.3 0.2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.3 0.2</size>
            </box>
          </geometry>
          <material>
            <ambient>0 0.5 0 1</ambient>
            <diffuse>0 1 0 1</diffuse>
            <specular>0 1 0 1</specular>
          </material>
        </visual>
        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.01</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.01</iyy>
            <iyz>0</iyz>
            <izz>0.01</izz>
          </inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

### ROS 2 Integration with Gazebo

To integrate ROS 2 with Gazebo, you can use the `ros_gz` bridge or the older `gazebo_ros_pkgs`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class GazeboRobotController(Node):
    def __init__(self):
        super().__init__('gazebo_robot_controller')

        # Publisher for velocity commands
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriber for laser scan data
        self.scan_subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Gazebo robot controller initialized')

    def scan_callback(self, msg):
        """Process laser scan data from Gazebo"""
        # Simple obstacle avoidance based on laser scan
        if len(msg.ranges) > 0:
            # Check front, left, and right sectors
            front_sector = msg.ranges[len(msg.ranges)//2]
            left_sector = msg.ranges[0]  # Simplified - in practice, average multiple readings
            right_sector = msg.ranges[-1]  # Simplified - in practice, average multiple readings

            self.navigate_based_on_scan(front_sector, left_sector, right_sector)

    def navigate_based_on_scan(self, front, left, right):
        """Simple navigation based on scan data"""
        cmd = Twist()

        if front < 0.8:  # Obstacle detected in front
            # Turn away from the closest obstacle
            if left < right:
                cmd.angular.z = -0.5  # Turn right
            else:
                cmd.angular.z = 0.5   # Turn left
        else:
            # Move forward if path is clear
            cmd.linear.x = 0.5

        self.cmd_vel_publisher.publish(cmd)

    def control_loop(self):
        """Main control loop - currently just sends the last computed command"""
        pass

def main(args=None):
    rclpy.init(args=args)
    controller = GazeboRobotController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Practical Implementation with Unity

Unity simulation requires different approaches but offers unique advantages:

### Unity Robotics Setup

1. Install Unity Hub and Unity Editor (2021.3 LTS or later)
2. Import the Unity Robotics Hub package
3. Set up ROS communication using ROS# or the Unity ROS TCP Connector
4. Create robot models with appropriate colliders and physics materials

### Example Unity C# Script for Robot Control

```csharp
using UnityEngine;
using System.Collections;
using Unity.Robotics.ROSTCPConnector;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Geometry;

public class UnityRobotController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 1.0f;
    [SerializeField] private float rotateSpeed = 1.0f;

    private ROSConnection ros;
    private string robotTopic = "/unity_robot/cmd_vel";

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.Subscribe<TwistMsg>(robotTopic, CmdVelCallback);
    }

    void CmdVelCallback(TwistMsg cmd)
    {
        // Convert ROS Twist message to Unity movement
        Vector3 movement = new Vector3(0, 0, (float)cmd.linear.x) * moveSpeed * Time.deltaTime;
        Vector3 rotation = new Vector3(0, (float)cmd.angular.z, 0) * rotateSpeed * Time.deltaTime;

        transform.Translate(movement);
        transform.Rotate(rotation);
    }

    void Update()
    {
        // Additional Unity-specific logic can go here
    }
}
```

## Labs and Mini-Projects

### Lab 3: Simulation Environment Setup
- **Objective**: Configure both Gazebo and Unity for robotics simulation
- **Tasks**:
  1. Install and configure Gazebo with ROS 2 integration
  2. Set up Unity with Robotics Hub and ROS connection
  3. Create simple robot models in both environments
  4. Implement basic sensor simulation (camera, LIDAR)
  5. Test communication between ROS 2 and simulation environments

### Mini-Project 3: Navigation in Simulation
- **Objective**: Implement a complete navigation system in simulation
- **Tasks**:
  1. Design a complex environment with obstacles and goals
  2. Implement SLAM (Simultaneous Localization and Mapping)
  3. Create a path planning algorithm
  4. Implement obstacle avoidance
  5. Test the complete system in both Gazebo and Unity
  6. Compare performance and characteristics of both simulators

## Key Readings and Resources

### Academic Papers
1. Koos, S., et al. (2013). Fast and accurate simulations of evolutionary robotics. *IEEE Congress on Evolutionary Computation*, 2013, 1598-1605.
2. Tedrake, R. (2022). *Underactuated Robotics: Algorithms for Walking, Running, Swimming, Flying, and Manipulation*. MIT Press.
3. Sadeghi, F., & Levine, S. (2017). CADRL: Learning collision avoidance using deep reinforcement learning. *IEEE/RSJ International Conference on Intelligent Robots and Systems*, 6567-6572.

### Technical Documentation
- [Gazebo Classic Documentation](http://gazebosim.org/tutorials)
- [Ignition Gazebo Documentation](https://ignitionrobotics.org/)
- [Unity Robotics Hub](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
- [ROS-Unity Integration](https://github.com/syuntoku14/fetch_ros_unity)

## Summary

Weeks 6-7 have covered the essential simulation environments for robotics development, including both Gazebo and Unity. Students should now understand:

- The role and importance of simulation in robotics development
- How to configure and use Gazebo for ROS-based robotics
- How to set up Unity for advanced robotics simulation
- Techniques for bridging the simulation-to-reality gap
- The comparative advantages of different simulation platforms

The next module will explore NVIDIA Isaac, the AI platform that brings deep learning and artificial intelligence capabilities to robotics systems.