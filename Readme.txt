Lipid Interaction Study Code

This repository contains scripts and tools developed by the University of Vienna for studying lipid interactions using computational methods. These tools are designed for researchers in biophysics, structural biology, and related fields.

Overview

The provided code enables detailed analysis of lipid-protein and lipid-lipid interactions in biological membranes. It supports a wide range of data inputs, including molecular dynamics (MD) simulation trajectories, experimental data formats, and structural models.

Key features include:

Interaction Mapping: Identification and quantification of lipid interaction sites.

Energy Calculations: Estimation of interaction energies using advanced force fields.

Visualization Tools: Generate publication-quality plots and 3D representations of lipid environments.

Customizable Workflows: Modular design for easy integration with existing pipelines.

Requirements

To run the code, you will need:

Software

Python (>=3.8)

NumPy (>=1.19)

Pandas (>=2.0)

Matplotlib (>=3.3)

FreeSimpleGUI (>=)

##MDAnalysis (>=2.0)

SciPy (>=1.6)

Optional: VMD or PyMOL for visualization

Hardware

Modern CPU (multi-core recommended)

At least 8 GB RAM

Optional: GPU acceleration for compatible tasks

Installation

Clone the repository to your local machine:

git clone https://github.com/univie-lipid-interaction/lipid-study.git
cd lipid-study

Install the required Python packages using pip:

pip install -r requirements.txt

Usage

1. Preprocessing

Prepare input data from your simulation or experimental setup. Ensure trajectories and topology files are in supported formats (e.g., .ntb, .txt).

2. Running the Analysis

Run the main script to perform lipid interaction studies:

python lipid_interaction_analysis.py --input trajectory.xtc --topology structure.pdb --output results/

3. Customizing Parameters

Edit the configuration file config.yaml to adjust parameters such as:

Distance cutoff for interactions

Selection criteria for lipids and residues

Output formats

4. Visualization

Use the included visualization script to generate plots:

python visualize_results.py --data results/interactions.csv --output plots/

Example Workflow

# Step 1: Preprocess input data
##python preprocess_data.py --input raw_data.xtc --topology structure.pdb --output preprocessed/

# Step 2: Run interaction analysis
##python lipid_interaction_analysis.py --input preprocessed/trajectory.xtc --topology structure.pdb --output results/

# Step 3: Visualize results
##python visualize_results.py --data results/interactions.csv --output plots/

Contributing

Contributions to improve this toolset are welcome. If you would like to contribute:

Fork this repository.

Create a feature branch (git checkout -b feature-name).

Commit your changes (git commit -m 'Add feature name').

Push to the branch (git push origin feature-name).

Open a pull request.

Please ensure all new code is well-documented and passes existing unit tests.

License

This project is licensed under the MIT License.

Contact

For inquiries or support, please contact the development team at:

Email: s.padiglioni@gmail.com - Stefano Padiglioni, gianluca.bello@univie.ac.at - Gianluca Bello

Website: University of Vienna AG Dailey
