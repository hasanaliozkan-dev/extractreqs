![PyPI version](https://img.shields.io/pypi/v/extractreqs.svg) [![License: MIT](https://img.shields.io/pypi/l/extractreqs.svg)](https://github.com/hasanaliozkan-dev/extractreqs/blob/main/LICENSE) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/extractreqs?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/extractreqs) ![Visitors](https://visitor-badge.laobi.icu/badge?page_id=hasanaliozkan-dev/extractreqs)

```text
           _                  _
  _____  _| |_ _ __ __ _  ___| |_ _ __ ___  __ _ ___
 / _ \ \/ / __| '__/ _` |/ __| __| '__/ _ \/ _` / __|
|  __/>  <| |_| | | (_| | (__| |_| | |  __/ (_| \__ \
 \___/_/\_\\__|_|  \__,_|\___|\__|_|  \___|\__, |___/
                                              |_|
```
### Description
extractreqs reads your Python source code, finds the third-party libraries it imports, and writes a `requirements.txt` pinned to the versions installed in your current environment. There is nothing to configure: point it at a folder and it does the rest.

### Features
* **Recursive scan**: parses every `.py` file in the folder and its subfolders, including imports inside functions and `try` blocks.
* **Standard library and local code filtered out**: only packages installed from PyPI end up in the file. Relative imports (`from .utils import x`) and your own modules are ignored.
* **Correct package names**: import names are mapped to the names you `pip install`, e.g. `sklearn` → `scikit-learn`, `PIL` → `Pillow`, `yaml` → `PyYAML`, `markdown_it` → `markdown-it-py`.
* **Pinned versions**: each line is `name==version`, sorted alphabetically.
* **Safe on real projects**: virtual environments (`.venv`, `venv`, or any folder with a `pyvenv.cfg`) and tool folders such as `.git`, `.tox` and `node_modules` are skipped. Files that fail to parse are skipped with a warning instead of stopping the scan.
* **CLI and Python API**, with no dependencies of its own.

### Installation
extractreqs needs Python 3.11 or newer.

```bash
pip install extractreqs
```

Install it into the same environment as your project's dependencies: versions are read from the environment extractreqs runs in, and packages that aren't installed there are left out.

### CLI usage
```bash
extractreqs . -o requirements.txt
```

* `src`: the folder to scan (required).
* `-o`, `--output`: the file to write, `requirements.txt` by default.

`python -m extractreqs . -o requirements.txt` does the same. Files that can't be parsed are reported on stderr:

```text
[!] Skipping ./old/legacy.py: invalid syntax (legacy.py, line 3)
[+] Extracted 12 requirements -> requirements.txt
```

### Python usage
```python
import extractreqs

# Returns the sorted list of "name==version" strings
reqs = extractreqs.extractreq("/path/to/your/project")

# write=True also writes requirements.txt into the current working directory
extractreqs.extractreq("/path/to/your/project", write=True)
```

`extractreq(src_dir, write=False)` scans `src_dir`, returns the requirements, and writes them to `requirements.txt` in the current working directory when `write` is `True`.

#### Example: generate requirements before packaging
```python
from pathlib import Path

import extractreqs


def prepare_deployment():
    project_root = Path.cwd()
    print(f"Scanning {project_root} for dependencies...")

    dependencies = extractreqs.extractreq(str(project_root), write=True)

    if dependencies:
        print(f"Generated requirements.txt with {len(dependencies)} packages.")
    else:
        print("No external dependencies found. The project only uses the standard library.")


prepare_deployment()
```

### Limitations
* Only static `import` statements are detected. Modules loaded by name at runtime (`importlib.import_module("x")`, `__import__`) are not.
* Every import counts, even optional ones inside `try`/`except ImportError`.
* A namespace import such as `google` can map to more than one PyPI package; extractreqs picks one installed package that provides it, so check those lines by hand.

### Development
```bash
git clone https://github.com/hasanaliozkan-dev/extractreqs.git
cd extractreqs
pip install -e ".[test]"
pytest
ruff check .
```

See [CONTRIBUTING.md](https://github.com/hasanaliozkan-dev/extractreqs/blob/main/CONTRIBUTING.md) for details and [HISTORY.md](https://github.com/hasanaliozkan-dev/extractreqs/blob/main/HISTORY.md) for the changelog.

### Author
extractreqs was created by Hasan Ali Özkan.

### License
MIT. See [LICENSE](https://github.com/hasanaliozkan-dev/extractreqs/blob/main/LICENSE).

### Credits
Built with Cookiecutter and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
