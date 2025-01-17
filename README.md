
---

# AHP Tool

**Version**: 1.1  
**Author**: zh404  

## Overview

The **AHP Tool** is a Python-based utility that simplifies decision-making using the **Analytic Hierarchy Process (AHP)** methodology. This tool guides users step-by-step to create a decision hierarchy, input pairwise comparisons, calculate weights, and rank alternatives based on global scores.

The tool supports both numerical and categorical criteria, handles consistency checks, and provides detailed outputs for transparency and accuracy.

---

## Features

- **Step-by-Step Guidance**: Intuitive prompts for entering hierarchy, criteria comparisons, and alternatives.
- **Numerical and Categorical Support**: Flexible handling of both types of criteria.
- **Consistency Check**: Ensures the validity of pairwise comparisons using the Consistency Ratio (CR).
- **Global Weight Calculation**: Computes global scores for alternatives based on the AHP methodology.
- **Cross-Platform Support**: Run on Windows, macOS, and Linux with simple setup.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Usage](#usage)
3. [Requirements](#requirements)
4. [File Structure](#file-structure)
5. [License](#license)

---

## Getting Started

Follow these steps to get started with the AHP Tool:

### 1. Clone or Download the Repository
```bash
git clone https://github.com/intrail/ahp-tool.git
cd ahp-tool
```

### 2. Install Dependencies
Use the `requirements.txt` file to install necessary dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Tool
#### Option 1: Run via Python
```bash
python AHP_Tool.py
```

#### Option 2: Double-Click
- **Windows**: Double-click `AHP Tool.bat`.  
- **macOS**: Double-click `AHP Tool.command`.  
  If you encounter a "permission denied" error, run the following command to make it executable:
  ```bash
  chmod +x "AHP Tool.command"
  ```

---

## Usage

### Hierarchy Input
Define your decision hierarchy using commas and curly braces. For example:
```
A, B{a, b{i, ii}}, C
```
This structure represents:
- `A`
- `B`, with sub-criteria `a` and `b`, and further sub-criteria `i` and `ii` under `b`
- `C`

### Criteria Comparison
Provide pairwise comparisons for criteria and sub-criteria. The tool will guide you through the process with intuitive prompts.

### Alternatives Input
Enter alternatives and specify whether criteria are numerical or categorical. The tool will compute local and global weights for each alternative.

### Output
The tool generates:
1. Pairwise comparison matrices.
2. Normalized weights and consistency checks.
3. Global rankings for alternatives.

---

## Requirements

- Python 3.6 or later
- Required Python libraries:
  - `numpy`
  - `pandas`

Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## File Structure

```
AHP-Tool/
├── src/
│   ├── main.py          # Main logic for the AHP process
│   ├── ahp.py           # AHP calculations and helper functions
│   ├── hierarchy.py     # Hierarchy parsing and display functions
│   ├── alternatives.py  # Alternatives and local weight computations
├── AHP_Tool.py          # Entry point for the Python-based tool
├── AHP Tool.bat         # Windows executable script
├── AHP Tool.command     # macOS executable script
├── LICENSE              # MIT License
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── .gitignore           # Files to ignore in Git
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

