# Physical AI & Humanoid Robotics Course Book

This Docusaurus-based course book provides a comprehensive 13-week curriculum on Physical AI and Humanoid Robotics, covering everything from fundamental sensor systems to advanced Vision-Language-Action integration.

## Course Structure

The course is organized into 5 core modules plus a capstone project:

1. **Introduction** (Weeks 1-2): Foundations of Physical AI & Sensors
2. **ROS 2 Fundamentals** (Weeks 3-5): Robot Operating System and communication
3. **Simulation** (Weeks 6-7): Gazebo & Unity environments
4. **AI Platform** (Weeks 8-10): NVIDIA Isaac for intelligent robotics
5. **Humanoid Systems** (Weeks 11-12): Kinematics, dynamics, and locomotion
6. **VLA Systems** (Week 13): Vision-Language-Action integration
7. **Capstone Project**: Autonomous humanoid robot implementation

## Getting Started

### Prerequisites

- Node.js version 18.0 or above
- npm or yarn package manager
- Git for version control

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd docs
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run start
   ```

The course book will be available at http://localhost:3000

### Building for Production

To build the static site for deployment:

```bash
npm run build
```

The built site will be in the `build/` directory and can be deployed to any static hosting service.

## Course Content

All course materials are organized in the `docs/` directory:

- `intro/` - Introduction module (Weeks 1-2)
- `ros2/` - ROS 2 fundamentals (Weeks 3-5)
- `simulation/` - Simulation environments (Weeks 6-7)
- `isaac/` - NVIDIA Isaac platform (Weeks 8-10)
- `humanoid/` - Humanoid robotics (Weeks 11-12)
- `vla/` - Vision-Language-Action systems (Week 13)
- `references.md` - Comprehensive reference list

## Code Examples

Companion code examples for each module are available in the parent directory under `code-examples/`:

- `ros2/` - ROS 2 code examples
- `gazebo/` - Gazebo simulation examples
- `unity/` - Unity simulation examples
- `isaac/` - NVIDIA Isaac examples
- `capstone/` - Capstone project starter code

## Quality Validation

The course includes automated quality validation scripts in `.specify/scripts/quality/`:

- `readability.py` - Flesch-Kincaid Grade Level checking
- `citation.py` - APA citation style verification
- `plagiarism.py` - Plagiarism detection
- `fact_check.py` - Technical fact verification

## Contributing

This course book follows Docusaurus best practices for documentation. When contributing:

1. Follow the existing content structure
2. Maintain consistent formatting and style
3. Include proper citations in APA format
4. Ensure content readability (Grade 11-13 level)
5. Test all code examples in the specified environment

## Deployment

The site can be deployed to GitHub Pages, Netlify, Vercel, or any static hosting service. The Docusaurus configuration is already set up for GitHub Pages deployment.

## Support

For questions about the course content, please open an issue in the repository. For technical issues with the Docusaurus site, consult the [Docusaurus documentation](https://docusaurus.io/).
