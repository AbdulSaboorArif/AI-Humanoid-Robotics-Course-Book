import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro', 'intro/week1-2'],
    },
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: ['ros2/week3-5'],
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: ['simulation/week6-7'],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac)',
      items: ['isaac/week8-10'],
    },
    {
      type: 'category',
      label: 'Module 4: Humanoid Kinematics, Dynamics, Locomotion',
      items: ['humanoid/week11-12'],
    },
    {
      type: 'category',
      label: 'Module 5: Vision-Language-Action (VLA)',
      items: ['vla/week13'],
    },
    {
      type: 'category',
      label: 'Capstone Project',
      items: ['vla/capstone_overview'],
    },
    {
      type: 'doc',
      id: 'references',
      label: 'References',
    },
  ],
};

export default sidebars;
