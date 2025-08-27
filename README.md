# requirePy

![PyPI version](https://img.shields.io/pypi/v/requirePy.svg)
[![Documentation Status](https://readthedocs.org/projects/requirePy/badge/?version=latest)](https://requirePy.readthedocs.io/en/latest/?version=latest)


requirePy is a tool to automatically extract and generate requirements.txt from Python source code by analyzing imports.

## How to Use

### Command Line

From your project root, run:

```bash
requirePy . -o requirements.txt
```

This will analyze your source code and generate a requirements.txt file.

### As a Python Module

You can also use requirePy in your own scripts:

```python
import requirePy
reqs = requirePy.extractreq(src_dir="/path/to/your/source", write=True)
print(reqs)
```

This will return a sorted list of requirements found in the given source directory.

* PyPI package: https://pypi.org/project/requirePy/
* Free software: MIT License
* Documentation: https://requirePy.readthedocs.io.

## Features

* TODO

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
