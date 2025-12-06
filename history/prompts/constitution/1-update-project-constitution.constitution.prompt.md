---
id: 1
title: Update project constitution
stage: constitution
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: null
command: /sp.constitution
labels: [constitution, update]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
- .specify/memory/constitution.md
tests:
null
---

## Prompt

# CONSTITUTION SPECIFICATION FOR PHYSICAL AI & HUMANID ROBOTICS BOOK PROJECT
## Project Title
**Physical AI & Humanoid Robotics: AI Systems in the Physical World – Quarter 4 Capstone Course Book**

## Project Goal
Bridge the gap between the digital brain and the physical body using ROS 2, Gazebo, Unity, NVIDIA Isaac Sim/ROS, and Vision-Language-Action models.

## 1. Core Principles (Non-Negotiable)
- Every technical claim must be validated against official docs (ROS 2, Gazebo, Isaac Sim, Isaac ROS) or peer-reviewed papers.
- Clarity level: Flesch-Kincaid 11–13 (intermediate–advanced CS students).
- Full reproducibility: all code & simulations must work out-of-the-box.
- Academic rigor using robotics textbooks, IEEE, ICRA, RSS, CoRL, etc.
- Zero plagiarism — 100% original wording.
- Entire book created using AI-native + Spec-Driven workflow (Spec-Kit Plus + Claude Code).

## 2. Exact Learning Outcomes (Must Appear Verbatim)
- Understand Physical AI principles and embodied intelligence
- Master ROS 2 (Robot Operating System) for robotic control
- Simulate robots with Gazebo and Unity
- Develop with NVIDIA Isaac AI robot platform
- Design humanoid robots for natural interactions
- Integrate GPT models and Vision-Language-Action systems for conversational robotics

## 3. Required Modules & 13-Week Breakdown (Exact Match)
Weeks 1–2  → Introduction to Physical AI + sensors
Weeks 3–5  → ROS 2 Fundamentals (Module 1)
Weeks 6–7  → Gazebo & Unity simulation (Module 2)
Weeks 8–10 → NVIDIA Isaac Platform (Module 3)
Weeks 11–12→ Humanoid kinematics, bipedal walking, manipulation
Week 13    → Conversational Robotics + VLA (Module 4) + Capstone integration

## 4. Capstone Project (Full Detail Required)
The Autonomous Humanoid: voice command → LLM task planning → Nav2 navigation → obstacle avoidance → CV object detection → manipulation.

## 5. Quality & Research Requirements
- 20,000 – 25,000 words total
- Minimum 20 sources (≥50% peer-reviewed: ICRA, RSS, CoRL, IEEE T-RO, etc.)
- APA 7th edition inline citations + full references section
- All diagrams in Mermaid.js or editable SVG
- Every chapter contains: objectives, lecture, runnable labs, mini-project, code, quiz

## 6. Assessments Section (Must Include)
- ROS 2 package development project
- Gazebo simulation implementation
- Isaac-based perception pipeline
- Capstone: Simulated humanoid robot with conversational AI

## 7. Output & Deployment
- Docusaurus site deployed on GitHub Pages
- PDF export version also generated
- Mobile-friendly + Lighthouse score > 90

## Response snapshot

The project constitution has been updated to version 0.1.0. This is a minor version bump as new content has been added.

The following templates require manual follow-up to ensure alignment with the updated constitution:
- .specify/templates/plan-template.md
- .specify/templates/spec-template.md
- .specify/templates/tasks-template.md
- .specify/templates/commands/*.md

Suggested commit message: `docs: amend constitution to v0.1.0 (initial content + governance update)`

## Outcome

- ✅ Impact: Constitution updated with initial project details.
- 🧪 Tests: No tests run for this documentation update.
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Review and update dependent templates (plan, spec, tasks, commands).
- 🧠 Reflection: Successfully updated the constitution file with the provided details. Fallback to agent-native PHR creation due to script not found.

## Evaluation notes (flywheel)

- Failure modes observed: PHR script `.specify/scripts/bash/create-phr.sh` not found.
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment: Ensure PHR creation script is available or improve agent's ability to locate it.
