# History

## 0.2.0 (2026-10-28)

### Fixed
* Virtual environments inside the scanned folder (`.venv`, `venv`, any folder with a `pyvenv.cfg`) and tool folders like `.git` are skipped, so their packages no longer leak into `requirements.txt`.
* A file with a syntax error is skipped with a warning instead of stopping the whole scan.
* Files with a PEP 263 encoding declaration (e.g. `# -*- coding: latin-1 -*-`) are read correctly.
* Relative imports (`from .local import x`) are no longer treated as third-party packages.
* Packages whose import name differs from their PyPI name are found through the installed metadata (e.g. `markdown_it` → `markdown-it-py`) instead of being silently dropped.
* Packages installed in `dist-packages` (Debian/Ubuntu system Python) and namespace packages are detected.
* `extractreq(src_dir)` works without the `write` argument (defaults to `False`).
* `python -m extractreqs` works.

### Changed
* Requires Python 3.11 or newer.
* No runtime dependencies (the unused `typer` dependency was removed).
* Packaging is defined in `pyproject.toml` only; the outdated `setup.py` was removed.
* New test suite and a GitHub Actions workflow.

## 0.1.3 (2026-07-29)

* Maintenance release (configuration and README updates).

## 0.1.2 (2026-07-29)

* Maintenance release (configuration and README updates).

## 0.1.1 (2025-08-28)

* Minor fixes and README badges.

## 0.1.0 (2025-08-27)

* First release on PyPI.
