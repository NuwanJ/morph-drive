# Origami Robot Algorithms

## About the Project

This Python package provides a comprehensive suite of algorithms and tools specifically designed for the simulation, analysis, and control of origami-inspired robotic systems. Origami robotics is a rapidly evolving field that leverages the principles of origami—the ancient art of paper folding—to create robots that are lightweight, scalable, and capable of complex transformations. These robots have the potential to revolutionize various applications, from minimally invasive surgery and deployable space structures to reconfigurable manufacturing and interactive art.

The core functionality of this package revolves around providing a robust framework for:
*   **Simulating Folding and Unfolding:** Accurately model the kinematics and dynamics of origami structures as they fold and unfold.
*   **Motion Planning:** Develop and implement algorithms to plan the motion of origami robots, enabling them to achieve desired configurations and perform tasks.
*   **Control System Design:** Design and test control strategies for origami robots, ensuring stability and precise operation.
*   **Visualization:** Offer tools to visualize origami structures, their folding sequences, and their interactions with the environment.

This package aims to empower researchers and developers by providing a standardized, open-source platform for exploring the unique challenges and opportunities presented by origami robotics. It is built with modularity and extensibility in mind, allowing users to integrate their own algorithms and robot designs.

## Features

This package offers a range of features to support the development and analysis of origami robots:

*   **Origami Folding Algorithms:**
    *   **Kinematic Solvers:** Efficiently calculate the folded state of an origami pattern given a set of fold angles.
    *   **Self-Folding Simulation:** Simulate the autonomous folding of origami structures based on material properties and actuation methods.
    *   **Applications:** Design of self-deployable structures, programmable matter, and reconfigurable robots.

*   **Motion Planning and Control:**
    *   **Path Planning for Folding:** Generate sequences of fold operations to achieve a target 3D shape.
    *   **Locomotion Algorithms:** Develop gaits and control strategies for origami robots that can move and navigate.
    *   **Integration with MuJoCo:** Leverage the MuJoCo physics engine for realistic simulation of robot dynamics and interaction with the environment.
    *   **Applications:** Creating robots capable of navigating complex terrains, manipulating objects, or performing assembly tasks.

*   **Visualization Tools:**
    *   **2D Crease Pattern Display:** Visualize the initial flat crease pattern of an origami design.
    *   **3D Folded State Rendering:** Render the origami structure in its folded 3D configuration.
    *   **Animation of Folding Sequences:** Create animations to visualize the entire folding process.
    *   **Applications:** Debugging folding algorithms, communicating designs, and creating educational demonstrations.

*   **Robot Modeling and Simulation Environments:**
    *   **Pre-defined Robot Classes:** Access a library of common origami robot archetypes (e.g., crawling robots, flapping robots).
    *   **Customizable Environments:** Define new robot morphologies and simulation scenarios.
    *   **Hardware Integration Support (Experimental):** Interfaces for connecting with and controlling physical origami robots.
    *   **Applications:** Rapid prototyping of new robot designs, benchmarking control strategies, and virtual testing before physical deployment.

## Installation

```bash
pip install morph-drive
```

## Getting Started

This section will guide you through setting up the package and running a basic example.

### Prerequisites

*   Python 3.8 or higher
*   pip (Python package installer)
*   MuJoCo (for physics-based simulation - refer to the official MuJoCo documentation for installation instructions)

### Basic Example

Here's a simple example of how to simulate the folding of an origami pattern:

```python
from morph_drive.simulation import OrigamiSimulator
from morph_drive.crease_pattern import CreasePattern

# 1. Define a crease pattern (e.g., a simple Miura-ori pattern)
# In a real scenario, you might load this from a file or define it programmatically.
cp = CreasePattern()
cp.add_node(0, (0, 0, 0))  # Node ID, coordinates
cp.add_node(1, (1, 0, 0))
cp.add_node(2, (0, 1, 0))
cp.add_node(3, (1, 1, 0))
cp.add_crease(0, 1, is_mountain=True) # Node1 ID, Node2 ID, fold type
cp.add_crease(0, 2, is_mountain=False)
cp.add_crease(1, 3, is_mountain=False)
cp.add_crease(2, 3, is_mountain=True)
cp.add_crease(0, 3, is_mountain=True) # Diagonal fold

# 2. Create a simulator instance
simulator = OrigamiSimulator(cp)

# 3. Define target fold angles (in radians)
# This depends on your specific crease pattern and desired folded state
target_angles = {
    (0, 3): 1.57,  # Fold the diagonal
    # Add other fold angles as needed
}

# 4. Run the simulation to fold the origami
folded_vertices, folded_faces = simulator.fold(target_angles)

# 5. Visualize the folded structure (optional, requires a visualizer setup)
# from morph_drive.visualization import OrigamiVisualizer
# visualizer = OrigamiVisualizer()
# visualizer.plot_origami(vertices=folded_vertices, faces=folded_faces) # Assuming faces are defined in CreasePattern

print("Simulation complete. Folded vertices:")
for i, vertex in enumerate(folded_vertices):
    print(f"Vertex {i}: {vertex}")

```

This example demonstrates the basic workflow:
1.  Define or load an origami `CreasePattern`.
2.  Instantiate an `OrigamiSimulator` with the crease pattern.
3.  Specify the `target_angles` for the creases you want to actuate.
4.  Call the `fold` method to perform the simulation.
5.  The result will be the new coordinates of the vertices in the folded state. You can then use these coordinates for further analysis or visualization.

For more detailed examples and advanced usage, please refer to the documentation and the examples directory in the repository.

## Usage

## Contributing

We welcome contributions to the Origami Robot Algorithms package! Whether you're interested in fixing bugs, adding new features, or improving documentation, your help is appreciated.

To contribute, please follow these guidelines:

1.  **Fork the Repository:** Start by forking the official repository to your own GitHub account.
2.  **Create a Branch:** Create a new branch in your forked repository for your contribution. Choose a descriptive branch name (e.g., `feature/new-algorithm`, `fix/bug-in-simulation`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
3.  **Make Your Changes:** Implement your changes, additions, or fixes in your branch.
    *   Ensure your code adheres to the existing coding style.
    *   Write clear and concise comments for new or complex code.
    *   If adding new features, include appropriate unit tests.
    *   If modifying existing features, ensure all existing tests pass.
4.  **Test Your Changes:** Run the test suite to ensure your changes haven't introduced any regressions.
    ```bash
    # (Command to run tests - e.g., pytest, python -m unittest)
    # pytest
    ```
5.  **Document Your Changes:** If you've added new functionality or changed existing behavior, update the documentation (including this README, if applicable) accordingly.
6.  **Commit Your Changes:** Commit your changes with a clear and descriptive commit message.
    ```bash
    git add .
    git commit -m "feat: Add new XYZ algorithm for path planning"
    ```
    We loosely follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.
7.  **Push to Your Fork:** Push your changes to your forked repository.
    ```bash
    git push origin feature/your-feature-name
    ```
8.  **Submit a Pull Request (PR):** Open a pull request from your branch to the `main` branch of the official repository.
    *   Provide a clear title and description for your PR, explaining the changes you've made and why.
    *   Reference any relevant issues if your PR addresses them.
9.  **Code Review:** Your PR will be reviewed by the maintainers. Be prepared to address any feedback or make further changes if requested.
10. **Merge:** Once your PR is approved, it will be merged into the main codebase.

### Reporting Bugs

If you encounter a bug, please open an issue on the GitHub repository. Include the following information in your report:
*   A clear and descriptive title.
*   Steps to reproduce the bug.
*   Expected behavior.
*   Actual behavior.
*   Your system environment (e.g., OS, Python version).

### Suggesting Enhancements

If you have an idea for a new feature or an improvement to an existing one, please open an issue to discuss it. This allows for feedback and coordination before significant development work begins.

Thank you for your interest in contributing to this project!

## License

This project is licensed under the Apache License, Version 2.0. You may obtain a copy of the License at:

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
