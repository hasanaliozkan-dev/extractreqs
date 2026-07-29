![PyPI version](https://img.shields.io/pypi/v/extractreqs.svg) [![License - MIT 3-Clause](https://img.shields.io/pypi/l/sfsgl.svg)](https://github.com/hasanaliozkan-dev/sfsgl/blob/main/LICENSE) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/extractreqs?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/extractreqs) ![Visitors](https://visitor-badge.laobi.icu/badge?page_id=hasanaliozkan-dev/extractreqs)

```text
           _                  _                      
  _____  _| |_ _ __ __ _  ___| |_ _ __ ___  __ _ ___ 
 / _ \ \/ / __| '__/ _` |/ __| __| '__/ _ \/ _` / __|
|  __/>  <| |_| | | (_| | (__| |_| | |  __/ (_| \__ \
 \___/_/\_\\__|_|  \__,_|\___|\__|_|  \___|\__, |___/
                                              |_|    
```
### Description 
A lightweight and intelligent tool designed to automatically analyze your Python source code, detect imported libraries, and generate accurate requirements.txt files without manual configuration.

### Features
* Automated Extraction: Recursively scans your Python files to identify all active dependencies.

* Standard Library Filtering: Smartly differentiates between built-in Python modules and third-party packages, keeping your requirements clean.

* File Generation: Automatically formats and writes a neatly sorted requirements.txt file ready for deployment.

* Dual Interface: Seamlessly use it as a command-line tool or import it as a module directly into your Python automation scripts.

* Zero Configuration: Just point it at a directory and it instantly handles the rest.

### Installation
You can install extractreqs directly from PyPI using standard package managers:

```bash
pip install extractreqs
```

### Usage Examples

#### Basic Python Usage

* extractreq(src_dir, write)

Scans the specified directory, extracts the necessary third-party modules, and optionally generates the file.

```python
import extractreqs

# Analyze source code and generate requirements.txt automatically
try:
    reqs = extractreqs.extractreq(src_dir="/path/to/your/source", write=True)
    print("Successfully extracted requirements:")
    for req in reqs:
        print(f"- {req}")
except Exception as e:
    print(f"Failed to extract requirements: {e}")
```
#### CLI Usage

```bash
extractreqs . -o requirements.txt
```

Under the hood, this will:

* Scan the current directory (.) for all .py files.

* Parse the Abstract Syntax Tree (AST) to find import and from ... import statements.

* Filter out Python's standard library modules.

* Write the final list of external dependencies into requirements.txt.

#### Complete Workflow Example
If you are building a deployment pipeline, you can dynamically generate your requirements before packaging:

```python
from pathlib import Path
import extractreqs

def prepare_deployment():
    project_root = Path.cwd()
    
    print(f"Scanning {project_root} for dependencies...")
    
    # 1. Extract requirements and create the file
    dependencies = extractreqs.extractreq(src_dir=str(project_root), write=True)
    
    # 2. Verify results
    if dependencies:
        print(f"Successfully generated requirements.txt with {len(dependencies)} packages.")
    else:
        print("No external dependencies found. Project uses only standard libraries.")

# Execute the workflow
prepare_deployment()
```
### Development
To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/extractreqs.git
cd extractreqs

# Install dependencies
uv sync

# Create a branch for development
git checkout -b feature/new-awesome-feature
```
### Author
extractreqs was created in 2026 by Hasan Ali Özkan.

### Credits
Built with Cookiecutter and the audreyfeldroy/cookiecutter-pypackage project template.