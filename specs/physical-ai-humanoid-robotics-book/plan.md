# Implementation Plan: Physical AI & Humanoid Robotics: AI Systems in the Physical World

**Branch**: `001-robotics-course-book` | **Date**: 2025-12-07 | **Spec**: specs/physical-ai-humanoid-robotics-book/spec.md
**Input**: Feature specification from `/specs/physical-ai-humanoid-robotics-book/spec.md` (to be created/updated)

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan outlines the complete creation of the Docusaurus-based book “Physical AI & Humanoid Robotics: AI Systems in the Physical World”, deployed on GitHub Pages. It follows the project Constitution and a future comprehensive Specification. The plan covers architectural design, content structure, phased implementation, research methodology, architectural decision documentation, and quality validation.

## Technical Context

**Language/Version**: JavaScript (Node.js), Markdown/MDX, Python (for ROS 2 examples)
**Primary Dependencies**: Docusaurus 3+, Node.js (LTS), Git, GitHub Actions, ROS 2 (latest stable), Gazebo (latest stable), Unity (LTS with ROS integration), NVIDIA Isaac Sim/ROS (latest stable), Python (for VLA models)
**Storage**: Git repository (source content, Docusaurus build output)
**Testing**: Docusaurus (build, link validation), GitHub Actions (deployment), Pytest (ROS 2 examples), unit/integration tests for VLA components.
**Target Platform**: Web (Docusaurus site on GitHub Pages), PDF export
**Project Type**: Documentation website/E-book
**Performance Goals**: Mobile-friendly + Lighthouse score > 90 (as per Constitution)
**Constraints**: APA 7th edition, 20,000 – 25,000 words, >= 20 sources (>=50% peer-reviewed), full reproducibility, Zero plagiarism, all diagrams in Mermaid.js or editable SVG.
**Scale/Scope**: Comprehensive 13-week course book covering Physical AI, ROS 2, Gazebo/Unity, NVIDIA Isaac, and VLA robotics.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This plan directly supports the following Core Principles and Output & Deployment requirements from the project Constitution:

- **Project Goal**: Bridge the gap between the digital brain and the physical body using ROS 2, Gazebo, Unity, NVIDIA Isaac Sim/ROS, and Vision-Language-Action models. (Architecture Sketch directly addresses this.)
- **Core Principles**:
    - Every technical claim must be validated against official docs or peer-reviewed papers. (Addressed in Research Strategy)
    - Clarity level: Flesch-Kincaid 11–13. (Addressed in content creation and review.)
    - Full reproducibility: all code & simulations must work out-of-the-box. (Addressed in Technical Validation)
    - Academic rigor. (Addressed in Research Strategy and Book Quality Validation)
    - Zero plagiarism. (Addressed in content creation and review.)
    - Entire book created using AI-native + Spec-Driven workflow. (Addressed by using /sp.plan itself.)
- **Output & Deployment**:
    - Docusaurus site deployed on GitHub Pages. (Addressed in Architecture Sketch and Phased Implementation)
    - PDF export version also generated. (Addressed in Phased Implementation)
    - Mobile-friendly + Lighthouse score > 90. (Addressed in Technical Context and Docusaurus Validation)

## Architecture Sketch

### Docusaurus & Global Book Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions for Docusaurus build & deploy to GitHub Pages
├── docs/                           # Main documentation content (MDX files)
│   ├── assets/                     # Shared images, diagrams (Mermaid.js, SVG)
│   ├── preface.mdx                 # Introduction, Course Overview
│   ├── module1-ros2/
│   │   ├── _category_.json         # Sidebar configuration for Module 1
│   │   ├── introduction.mdx
│   │   ├── ros2-nodes.mdx
│   │   └── ... (other ROS 2 topics)
│   ├── module2-digital-twin/
│   │   ├── _category_.json         # Sidebar configuration for Module 2
│   │   ├── gazebo-intro.mdx
│   │   ├── unity-integration.mdx
│   │   └── ...
│   ├── module3-nvidia-isaac/
│   │   └── ...
│   ├── module4-vla/
│   │   └── ...
│   ├── weekly-breakdown/
│   │   ├── _category_.json         # Sidebar for weekly content
│   │   ├── week1-2-intro.mdx
│   │   ├── week3-5-ros2.mdx
│   │   └── ... (Weeks 1-13)
│   ├── projects/
│   │   ├── _category_.json         # Sidebar for projects
│   │   ├── ros2-package-project.mdx
│   │   └── ... (other projects)
│   ├── capstone/
│   │   ├── _category_.json
│   │   └── autonomous-humanoid.mdx # Capstone project details
│   └── appendices/
│       └── references.mdx          # APA 7th edition references
├── blog/                           # (Optional) Blog for course updates, announcements
├── src/                            # Custom Docusaurus components, styles
│   ├── components/
│   └── css/
├── static/                         # Static assets (favicons, logos, custom CSS)
├── docusaurus.config.js            # Docusaurus configuration (title, navbar, plugins, themes)
└── sidebars.js                     # Centralized sidebar definition (auto-generated/maintained)
```

### Tooling Architecture

-   **Docusaurus + MDX**: Used for static site generation, content authoring with rich media, and interactive components. MDX enables embedding React components within Markdown for labs and interactive exercises.
-   **GitHub Pages deployment workflow**: GitHub Actions will be configured to automatically build the Docusaurus site on pushes to a specific branch (e.g., `main` or `gh-pages`) and deploy the static assets to GitHub Pages. This ensures continuous deployment.
-   **Spec-Kit Plus workflow**: The entire book creation process will follow Spec-Driven Development:
    -   `spec.md`: Detailed requirements for each module/chapter/project.
    -   `plan.md`: This architectural and implementation plan.
    -   `tasks.md`: Granular, testable tasks derived from the plan.
    -   Implementation: Creation of content, code examples, diagrams.

### Robotics Stack Architecture

-   **ROS 2 (Robot Operating System)**:
    -   **URDF**: Used for robot description files (kinematics, visuals, collision models).
    -   **Nodes**: Independent executable processes (e.g., sensor drivers, motor controllers, navigation stack).
    -   **Topics**: Asynchronous communication for streaming data (e.g., sensor readings, joint states).
    -   **Services**: Synchronous request/reply communication (e.g., querying robot state, triggering actions).
    -   **rclpy**: Python client library for ROS 2, used for developing nodes and interacting with the ROS graph.
-   **Gazebo + Unity (Digital Twin Pipeline)**:
    -   **Gazebo**: Primary simulator for physics-based robot interactions, sensor simulation (Lidar, cameras), and environment modeling. Used for realistic robot dynamics.
    -   **Unity**: Complementary simulator for high-fidelity rendering, advanced visualization, and potentially human-robot interaction (HRI) scenarios. ROS-Unity bridge for data exchange.
    -   **Pipeline**: URDF models from ROS are imported into Gazebo/Unity. Control loops (ROS 2 nodes) interact with the simulated robot via ROS interfaces.
-   **NVIDIA Isaac (AI Robot Platform)**:
    -   **Isaac Sim/ROS**: Integration with ROS 2 for simulating NVIDIA robots, leveraging advanced physics (PhysX), synthetic data generation for training AI models, and GPU-accelerated computing.
    -   **VSLAM**: Visual Simultaneous Localization and Mapping for robot pose estimation and environment mapping.
    -   **Nav2**: ROS 2 navigation stack for autonomous mobile robot navigation (path planning, obstacle avoidance).
    -   **Synthetic Data**: Generation of diverse datasets from simulation for robust deep learning model training, especially for perception tasks.
-   **VLA Pipeline (Vision-Language-Action)**:
    -   **Whisper**: Speech-to-text model for converting voice commands into text.
    -   **LLM Planning**: Large Language Model (e.g., GPT-4) for interpreting natural language commands, breaking them into sub-tasks, and generating a high-level action plan.
    -   **ROS Actions**: ROS 2 Action servers/clients for executing planned actions (e.g., move_to_location, pick_object, manipulate_joint). LLM output is translated into ROS 2 action goals.
    -   **Perception**: Integration with Isaac VSLAM and CV object detection for real-time environmental understanding to inform LLM planning and action execution.

## Section Structure / Docs Map

### Global Book Flow

**Preface**
-   Purpose: Introduce the course, target audience, prerequisites, and learning philosophy.
-   Prerequisites: Basic Python, Linux CLI, intro to robotics concepts.
-   Learning Outcomes: Understand the course structure and foundational concepts.

**Module 1: The Robotic Nervous System (ROS 2)**
-   Purpose: Core understanding of ROS 2 architecture and programming.
-   Prerequisites: Python basics, Linux CLI.
-   Learning Outcomes: Master ROS 2 nodes, topics, services, actions, parameters, URDF, rclpy.
-   Pages: `module1-ros2/introduction.mdx`, `module1-ros2/nodes-topics-services.mdx`, `module1-ros2/ros2-actions.mdx`, `module1-ros2/parameters-logging.mdx`, `module1-ros2/urdf-xacro.mdx`, `module1-ros2/rclpy-development.mdx`, `module1-ros2/tf2-coordinates.mdx`, `module1-ros2/build-system-colcon.mdx`

**Module 2: The Digital Twin (Gazebo + Unity)**
-   Purpose: Hands-on experience with robot simulation environments.
-   Prerequisites: Module 1 (ROS 2 fundamentals).
-   Learning Outcomes: Simulate robots in Gazebo, integrate ROS 2 with Unity, create custom environments.
-   Pages: `module2-digital-twin/gazebo-intro.mdx`, `module2-digital-twin/robot-modeling-simulation.mdx`, `module2-digital-twin/sensor-simulation.mdx`, `module2-digital-twin/ros-gazebo-integration.mdx`, `module2-digital-twin/unity-ros-bridge.mdx`, `module2-digital-twin/high-fidelity-rendering.mdx`

**Module 3: The AI-Robot Brain (NVIDIA Isaac)**
-   Purpose: Explore advanced AI capabilities for robotics using NVIDIA Isaac platform.
-   Prerequisites: Module 1 & 2.
-   Learning Outcomes: Implement VSLAM, use Nav2 with Isaac, generate synthetic data, understand Isaac ROS.
-   Pages: `module3-nvidia-isaac/isaac-sim-overview.mdx`, `module3-nvidia-isaac/vslam-and-mapping.mdx`, `module3-nvidia-isaac/nav2-integration.mdx`, `module3-nvidia-isaac/synthetic-data-generation.mdx`, `module3-nvidia-isaac/isaac-ros-packages.mdx`

**Module 4: Vision-Language-Action (VLA) Systems**
-   Purpose: Integrate LLMs and vision systems for natural language robot control.
-   Prerequisites: Module 1, 2, 3 (especially Nav2 and perception basics).
-   Learning Outcomes: Design VLA pipelines, implement LLM-based task planning, use speech-to-action.
-   Pages: `module4-vla/vla-introduction.mdx`, `module4-vla/speech-to-text-whisper.mdx`, `module4-vla/llm-task-planning.mdx`, `module4-vla/llm-ros-action-interface.mdx`, `module4-vla/vision-for-vla.mdx`, `module4-vla/full-vla-pipeline.mdx`

### Weekly Breakdown Pages

-   **Weeks 1–2: Introduction to Physical AI**: `weekly-breakdown/week1-2-intro.mdx` (Purpose: Foundational concepts, ethics; LO: Grasp Physical AI scope).
-   **Weeks 3–5: ROS 2 Fundamentals**: `weekly-breakdown/week3-5-ros2.mdx` (Purpose: Deep dive into Module 1; LO: ROS 2 proficiency).
-   **Weeks 6–7: Gazebo Simulation**: `weekly-breakdown/week6-7-gazebo.mdx` (Purpose: Focus on Gazebo aspects of Module 2; LO: Gazebo simulation skills).
-   **Weeks 8–10: NVIDIA Isaac**: `weekly-breakdown/week8-10-isaac.mdx` (Purpose: Deep dive into Module 3; LO: Isaac platform proficiency).
-   **Weeks 11–12: Humanoid Development**: `weekly-breakdown/week11-12-humanoids.mdx` (Purpose: Kinematics, bipedalism, manipulation, pre-VLA; LO: Humanoid design basics).
-   **Week 13: Conversational Robotics + VLA + Capstone**: `weekly-breakdown/week13-capstone.mdx` (Purpose: Module 4 integration, Capstone prep; LO: VLA system design, Capstone initiation).

### Assessment Pages

-   **ROS 2 Package Development Project**: `projects/ros2-package-project.mdx` (Purpose: Assess ROS 2 mastery; LO: Design and implement a ROS 2 package).
-   **Gazebo Simulation Implementation**: `projects/gazebo-simulation-project.mdx` (Purpose: Assess simulation skills; LO: Create and simulate a robot in Gazebo).
-   **Isaac Perception Pipeline**: `projects/isaac-perception-pipeline.mdx` (Purpose: Assess Isaac usage; LO: Build a perception pipeline using Isaac tools).
-   **Capstone: Simulated Humanoid Robot with Conversational AI**: `capstone/autonomous-humanoid.mdx` (Purpose: Integrate all modules; LO: Design, implement, and demonstrate a VLA-controlled humanoid).

## Phased Implementation

### Foundation Phase (Weeks 1-2 & Parallel Setup)

**Goals**: Establish technical infrastructure, deploy initial basic content, and confirm core tooling.
**Tasks (mapped to curriculum)**:
-   **Docusaurus Project Setup**: `docs/` structure, `docusaurus.config.js`, `sidebars.js` (initial setup).
-   **GitHub Pages Configuration**: `deploy.yml` GitHub Actions workflow.
-   **Sidebar & Global Structure**: Implement initial `sidebars.js` with placeholders for all modules, weekly breakdowns, projects, capstone, appendices.
-   **Preface Content**: Write `preface.mdx`.
-   **Weeks 1–2 Content**: Draft `weekly-breakdown/week1-2-intro.mdx`.
-   **Initial Research**: Kick off high-level research on "Embodied intelligence" and "Robotics learning outcomes" to inform content tone.

### Analysis Phase (Weeks 3-10 Content & Deeper Research)

**Goals**: Develop core module content, cross-link key concepts, and deepen academic research.
**Tasks (mapped to curriculum)**:
-   **Module 1 (ROS 2) Detailed Pages**: Draft all pages under `module1-ros2/`.
-   **Module 2 (Digital Twin) Detailed Pages**: Draft all pages under `module2-digital-twin/`.
-   **Module 3 (NVIDIA Isaac) Detailed Pages**: Draft all pages under `module3-nvidia-isaac/`.
-   **Weekly Breakdown Pages (Weeks 3-10)**: Draft `weekly-breakdown/week3-5-ros2.mdx`, `week6-7-gazebo.mdx`, `week8-10-isaac.mdx`.
-   **Cross-linking**: Identify and implement cross-references between ROS 2, Gazebo, and Isaac content where pipelines or concepts intertwine.
-   **Research Strategy Execution**:
    -   Academic sourcing for "ROS 2 architecture", "Gazebo physics simulation", "Isaac VSLAM and RL".
    -   Collect and verify claims, start populating `appendices/references.mdx`.
    -   Ensure APA citation formatting is correctly applied in MDX.

### Synthesis Phase (Weeks 11-13 & Capstone Integration)

**Goals**: Integrate VLA systems, finalize Capstone project details, and perform comprehensive review.
**Tasks (mapped to curriculum)**:
-   **Module 4 (VLA) Detailed Pages**: Draft all pages under `module4-vla/`.
-   **Weekly Breakdown Pages (Weeks 11-13)**: Draft `weekly-breakdown/week11-12-humanoids.mdx`, `week13-capstone.mdx`.
-   **Assessment Pages**: Draft content for all `projects/` and `capstone/` pages.
-   **VLA Integration**: Develop detailed explanation and code examples for the VLA pipeline, from Whisper to LLM planning to ROS Actions.
-   **Capstone Robotics Pipeline**: Articulate the full Capstone project, ensuring it integrates concepts from all modules.
-   **Final Polish & Proofing**: Review all content for clarity, grammar, consistency, and alignment with learning outcomes.
-   **Research Strategy Completion**: Finalize "VLA robotics integrations" research, ensure all citations are present and APA-correct.
-   **PDF Export Generation**: Investigate and implement a solution for generating a PDF version of the Docusaurus book.

## Research Strategy + APA Citations

### Academic Sourcing

-   **Embodied Intelligence**: Search for foundational papers (e.g., Rodney Brooks, Rolf Pfeifer), cognitive robotics, situated AI.
-   **ROS 2 Architecture**: Official ROS 2 documentation, design documents for DDS, rclpy/rclcpp.
-   **Gazebo Physics Simulation**: Gazebo documentation, papers on physics engines (ODE, PhysX), real-to-sim transfer in robotics.
-   **Isaac VSLAM and RL**: NVIDIA developer documentation, research papers on Isaac Sim/ROS, VSLAM algorithms (ORB-SLAM, VINS-Mono), reinforcement learning in simulation.
-   **VLA Robotics Integrations**: Recent papers on LLMs in robotics, language-guided control, vision-language models (e.g., CLIP, ViT, Gato-like architectures), prompt engineering for robotics.

### Tracking & Verifying Claims

-   Maintain a `research-notes.md` (or similar) during the research process to log sources, key findings, and their relevance.
-   Every factual claim in the book must be traceable to a credible source (official documentation, peer-reviewed paper, reputable academic textbook).
-   Code examples must be verified for correctness and reproducibility by running them.

### APA Citation Formatting in MDX

-   All inline citations will follow APA 7th edition style (e.g., (Author, Year) or Author (Year)).
-   A dedicated `appendices/references.mdx` page will list all full references in APA 7th edition format.
-   Docusaurus plugins or custom MDX components may be explored to streamline citation management, but manual formatting will be the fallback.

## Decision Documentation (ADRs)

For each significant decision, an Architectural Decision Record (ADR) will be suggested and, upon user consent, created in `history/adr/` using the `/sp.adr` command.

1.  **Docusaurus Navigation Structure Choice**
    -   **Context**: Docusaurus offers various ways to structure navigation (sidebar, navbar, doc categories). The book needs a clear, intuitive flow for a course.
    -   **Options**:
        1.  Strictly linear (`next/prev` only).
        2.  Module-first hierarchy (top-level modules, sub-items are weeks/topics).
        3.  Week-first hierarchy (top-level weeks, sub-items are module topics covered).
        4.  Hybrid (modules in sidebar, weekly breakdown as a separate section/view).
    -   **Trade-offs**:
        -   Linear: Simplest, but hard to browse large content.
        -   Module-first: Good for deep dives into specific tech, but hides weekly flow.
        -   Week-first: Excellent for following the course chronologically, but might fragment tech topics.
        -   Hybrid: Best of both, but potentially more complex to implement and maintain `sidebars.js`.
    -   **Chosen Decision**: Hybrid approach - primary navigation via Modules (Module 1-4) in the main sidebar, with a separate `Weekly Breakdown` section also in the sidebar to provide chronological context. This allows students to both deep-dive into a module and see the progression week-by-week.

2.  **Module-first vs Week-first Chapter Flow**
    -   **Context**: How the content is presented within the book: organized primarily by modules or by weeks.
    -   **Options**: (Same as Docusaurus Navigation Structure Choice, but for content flow).
    -   **Trade-offs**: (Same as above).
    -   **Chosen Decision**: Module-first content organization, with explicit cross-references to weekly sections where modules are covered. Each weekly page will link to relevant module pages. This makes the primary content reusable and modular while providing weekly guidance.

3.  **Digital Twin Strategy (Gazebo-first vs Unity-first)**
    -   **Context**: Deciding which simulation environment is primary for physics-based interactions versus high-fidelity visualization.
    -   **Options**:
        1.  Gazebo-first: Use Gazebo for all core physics, sensor simulation, and ROS 2 integration. Use Unity only for supplementary high-fidelity visualization if needed.
        2.  Unity-first: Attempt to use Unity as the primary physics engine and simulator, with ROS-Unity bridge.
    -   **Trade-offs**:
        -   Gazebo-first: Proven, robust for ROS robotics, extensive community support, easier ROS 2 integration. Less graphical fidelity.
        -   Unity-first: High graphical fidelity, potentially more intuitive UI for environment design, but ROS 2 integration might be less mature/performant for physics than Gazebo.
    -   **Chosen Decision**: Gazebo-first for core physics, sensor simulation, and primary ROS 2 interaction. Unity will be integrated as a complementary tool for high-fidelity rendering, advanced visualization, and specific human-robot interaction scenarios where its graphical capabilities provide significant value.

4.  **Isaac Integration Depth**
    -   **Context**: How deeply to integrate NVIDIA Isaac platform features, given its breadth.
    -   **Options**:
        1.  Focus on Isaac Sim for ROS 2 simulation and synthetic data.
        2.  Include Isaac ROS (specific packages like VSLAM, Nav2 perception components).
        3.  Deep dive into Isaac SDK for custom robot applications (beyond scope for an introductory course).
    -   **Trade-offs**: Deeper integration increases complexity but provides more advanced capabilities. Lighter integration keeps the course manageable.
    -   **Chosen Decision**: Focus on Isaac Sim for its robust ROS 2 simulation, synthetic data generation capabilities, and integration with Nav2. Also include key Isaac ROS packages like VSLAM to demonstrate real-world perception pipelines. Avoid deep dives into custom Isaac SDK development beyond what's directly applicable to the course objectives.

5.  **VLA Planning Pipeline Design (Single Model vs Multi-Model)**
    -   **Context**: How the LLM-based task planning integrates with other AI components.
    -   **Options**:
        1.  Single, large LLM for all reasoning (language understanding, task decomposition, action generation).
        2.  Multi-model approach: specialized models for speech-to-text (Whisper), a central LLM for high-level planning, and smaller, fine-tuned models/rules for translating LLM output to specific ROS 2 actions.
    -   **Trade-offs**:
        -   Single model: Simpler architecture, but may lack fine-grained control and domain-specific accuracy.
        -   Multi-model: More complex architecture, but allows for modularity, better performance for specific sub-tasks, and easier debugging.
    -   **Chosen Decision**: Multi-model approach using Whisper for robust speech-to-text, a powerful general-purpose LLM (e.g., GPT-4 class) for high-level semantic understanding and task decomposition, and then either smaller, fine-tuned models or rule-based systems to translate LLM-generated plans into precise ROS 2 action sequences. This provides robustness and allows leveraging strengths of different AI components.

6.  **Repo Structure & GitHub Pages Workflow Choices**
    -   **Context**: How the Docusaurus project coexists with the main course content repository and the best way to deploy to GitHub Pages.
    -   **Options**:
        1.  Docusaurus project in `docs/` subdirectory, deploy `docs/.docusaurus/build` to `gh-pages` branch.
        2.  Docusaurus project in root, use `main` branch directly.
        3.  Separate repository for Docusaurus.
    -   **Trade-offs**:
        -   Option 1: Keeps all course-related files in one repo, clear separation of source and build. Requires GitHub Actions to build and push to `gh-pages`.
        -   Option 2: Simplest if Docusaurus is the *only* content, but mixes source code with generated output if other things are in `main`.
        -   Option 3: Cleanest separation but requires managing two repositories and potentially more complex linking.
    -   **Chosen Decision**: Option 1: The Docusaurus project will reside in a `docs/` subdirectory within the main course repository. GitHub Actions will be configured to build the Docusaurus site and deploy the static artifacts to the `gh-pages` branch of the same repository. This keeps all relevant content co-located while providing a clean deployment mechanism.

## Testing & Quality Validation

### Book Quality Validation

-   **Citations Present & APA-Correct**: Manual and automated checks (if tools are available) to ensure every factual claim has an inline APA 7th edition citation and a corresponding entry in `references.mdx`.
-   **All Claims Verifiable**: Spot-check claims against original sources to ensure accuracy and correct interpretation.
-   **All Modules Aligned to Learning Outcomes**: Each module's content and assessments are reviewed against its stated learning outcomes to ensure comprehensive coverage.
-   **Clarity and Readability**: Flesch-Kincaid score (target 11-13) analysis and human review for clarity, conciseness, and pedagogical effectiveness.
-   **Grammar and Spelling**: Automated spell checkers and human proofreading.
-   **Diagram Correctness**: Verify all Mermaid.js or SVG diagrams accurately represent the described concepts.

### Technical Validation

-   **ROS 2 Examples Run**: All ROS 2 code snippets and lab exercises will be tested to ensure they compile and run correctly on a reference setup.
-   **Gazebo World Launches**: Custom Gazebo environments and robot models will be tested to ensure they load without errors and physics simulations behave as expected.
-   **Isaac Scenarios Functional**: Isaac Sim/ROS examples (e.g., VSLAM, Nav2) will be tested for correct functionality within the simulation environment.
-   **VLA Workflow Test (Whisper → LLM → ROS)**: The entire VLA pipeline, from voice command input to robot action execution in simulation, will be end-to-end tested with various commands.

### Docusaurus Validation

-   **Build Passes**: The `docusaurus build` command must complete without errors.
-   **Links Resolve**: All internal and external links within the Docusaurus site will be automatically checked for broken links during the build process.
-   **GitHub Pages Deploys Cleanly**: Verify that the GitHub Actions workflow successfully deploys the site, and the deployed site is accessible and functional.
-   **Mobile Responsiveness**: Test on various screen sizes and devices to ensure a mobile-friendly experience.
-   **Lighthouse Score > 90**: Run Google Lighthouse audits on key pages to ensure performance, accessibility, best practices, and SEO scores are above 90.

## Project Structure

### Documentation (this feature)

```text
specs/physical-ai-humanoid-robotics-book/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (placeholder, less relevant for book)
├── quickstart.md        # Phase 1 output (placeholder, less relevant for book)
├── contracts/           # Phase 1 output (placeholder, less relevant for book)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions for Docusaurus build & deploy
├── docs/                           # Docusaurus project root
│   ├── assets/                     # Shared images, diagrams
│   ├── preface.mdx                 # Course overview
│   ├── module1-ros2/               # Module 1 content
│   ├── module2-digital-twin/       # Module 2 content
│   ├── module3-nvidia-isaac/       # Module 3 content
│   ├── module4-vla/                # Module 4 content
│   ├── weekly-breakdown/           # Weekly content mapping
│   ├── projects/                   # Assessment projects
│   ├── capstone/                   # Capstone project details
│   ├── appendices/                 # References, etc.
│   ├── docusaurus.config.js        # Docusaurus configuration
│   └── sidebars.js                 # Sidebar definitions
├── robotics-code-examples/         # Standalone ROS 2, Gazebo, Isaac, VLA code
│   ├── ros2-ws/                    # ROS 2 workspace (packages)
│   ├── gazebo-sims/                # Gazebo world and model files
│   ├── unity-projects/             # Unity projects with ROS-Unity bridge
│   ├── isaac-sim-projects/         # Isaac Sim projects
│   └── vla-demos/                  # VLA pipeline demos
└── .specify/                       # Spec-Kit Plus configurations, scripts, templates
```

**Structure Decision**: The Docusaurus project will reside in the `docs/` subdirectory. All runnable code examples will be in a `robotics-code-examples/` directory at the repository root, separated by technology stack, to maintain reproducibility and clean separation from the Docusaurus content.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |