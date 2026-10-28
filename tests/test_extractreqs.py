"""Unit tests for extractreqs."""

import importlib.machinery
import importlib.metadata
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

import extractreqs
from extractreqs import cli
from extractreqs.extractreqs import (
    extract_requirements,
    filter_installed_packages,
    get_all_imports,
    get_imports_from_file,
)

SRC_DIR = Path(__file__).resolve().parents[1] / "src"


def write(path: Path, code: str, encoding: str = "utf-8") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding=encoding)
    return path


def pin(dist: str) -> str:
    return f"{dist}=={importlib.metadata.version(dist)}"


@pytest.fixture
def fake_installed(monkeypatch):
    """Pretend the given import names are installed at the given origin with the given dist versions."""

    def install(origins: dict[str, str], versions: dict[str, str]) -> None:
        real_find_spec = importlib.util.find_spec
        real_version = importlib.metadata.version

        def find_spec(name, *args, **kwargs):
            if name in origins:
                return importlib.machinery.ModuleSpec(name, None, origin=origins[name])
            return real_find_spec(name, *args, **kwargs)

        def version(dist):
            return versions[dist] if dist in versions else real_version(dist)

        monkeypatch.setattr(importlib.util, "find_spec", find_spec)
        monkeypatch.setattr(importlib.metadata, "version", version)

    return install


# get_imports_from_file


def test_plain_dotted_aliased_and_from_imports(tmp_path):
    f = write(tmp_path / "a.py", "import os\nimport a.b.c\nimport numpy as np\nfrom x.y import z\n")
    assert get_imports_from_file(str(f)) == {"os", "a", "numpy", "x"}


def test_nested_imports_are_found(tmp_path):
    code = "def f():\n    import inner\n\ntry:\n    import fast\nexcept ImportError:\n    import slow\n"
    f = write(tmp_path / "a.py", code)
    assert get_imports_from_file(str(f)) == {"inner", "fast", "slow"}


def test_relative_imports_are_ignored(tmp_path):
    f = write(tmp_path / "a.py", "from . import a\nfrom .local import b\nfrom ..pkg.mod import c\n")
    assert get_imports_from_file(str(f)) == set()


def test_file_with_declared_non_utf8_encoding(tmp_path):
    f = write(tmp_path / "a.py", "# -*- coding: latin-1 -*-\nimport requests\nname = 'Özkan'\n", encoding="latin-1")
    assert get_imports_from_file(str(f)) == {"requests"}


# get_all_imports


def test_walks_subdirectories_and_only_reads_py_files(tmp_path):
    write(tmp_path / "top.py", "import alpha\n")
    write(tmp_path / "pkg" / "sub" / "deep.py", "import beta\n")
    write(tmp_path / "notes.txt", "import gamma\n")
    assert get_all_imports(str(tmp_path)) == {"alpha", "beta"}


def test_file_with_syntax_error_does_not_abort_scan(tmp_path, capsys):
    write(tmp_path / "good.py", "import alpha\n")
    write(tmp_path / "broken.py", "def oops(:\n")
    assert get_all_imports(str(tmp_path)) == {"alpha"}
    assert "broken.py" in capsys.readouterr().err


@pytest.mark.parametrize("env_dir", [".venv", "venv"])
def test_virtualenv_inside_project_is_not_scanned(tmp_path, env_dir):
    write(tmp_path / "app.py", "import alpha\n")
    write(tmp_path / env_dir / "lib" / "python3.13" / "site-packages" / "dep" / "x.py", "import leaked\n")
    assert get_all_imports(str(tmp_path)) == {"alpha"}


def test_custom_named_virtualenv_is_detected_by_pyvenv_cfg(tmp_path):
    write(tmp_path / "app.py", "import alpha\n")
    write(tmp_path / "myenv" / "pyvenv.cfg", "home = /usr/bin\n")
    write(tmp_path / "myenv" / "lib" / "dep.py", "import leaked\n")
    assert get_all_imports(str(tmp_path)) == {"alpha"}


# filter_installed_packages


def test_stdlib_is_excluded():
    assert filter_installed_packages({"os", "sys", "json", "ast", "importlib"}) == set()


def test_unknown_module_is_excluded():
    assert filter_installed_packages({"definitely_not_a_real_module_xyz"}) == set()


def test_installed_package_is_pinned():
    assert filter_installed_packages({"pytest"}) == {pin("pytest")}


def test_known_import_name_is_mapped_to_dist(fake_installed):
    fake_installed({"sklearn": "/env/lib/python3.13/site-packages/sklearn/__init__.py"}, {"scikit-learn": "1.5.0"})
    assert filter_installed_packages({"sklearn"}) == {"scikit-learn==1.5.0"}


def test_unmapped_import_name_differing_from_dist_is_not_dropped():
    pytest.importorskip("markdown_it")  # installed by rich, a dependency of typer
    assert filter_installed_packages({"markdown_it"}) == {pin("markdown-it-py")}


def test_dist_packages_install_is_detected(fake_installed):
    # Debian/Ubuntu system Python installs third-party packages into dist-packages
    fake_installed({"requests": "/usr/lib/python3/dist-packages/requests/__init__.py"}, {"requests": "2.31.0"})
    assert filter_installed_packages({"requests"}) == {"requests==2.31.0"}


def test_namespace_package_is_detected(monkeypatch, fake_installed):
    fake_installed({}, {"google-api-python-client": "2.0.0"})
    spec = importlib.machinery.ModuleSpec("google", None, is_package=True)
    spec.submodule_search_locations = ["/env/lib/python3.13/site-packages/google"]
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util, "find_spec", lambda name, *a: spec if name == "google" else real_find_spec(name)
    )
    assert filter_installed_packages({"google"}) == {"google-api-python-client==2.0.0"}


# extract_requirements


def test_returns_sorted_list_without_writing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "src" / "app.py", "import pytest\nimport os\nimport _missing_module_\n")
    assert extract_requirements(str(tmp_path / "src"), False) == [pin("pytest")]
    assert not (tmp_path / "requirements.txt").exists()


def test_write_true_creates_requirements_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "src" / "app.py", "import pytest\n")
    reqs = extract_requirements(str(tmp_path / "src"), True)
    assert (tmp_path / "requirements.txt").read_text().splitlines() == reqs


def test_write_defaults_to_false(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path / "src" / "app.py", "import pytest\n")
    assert extractreqs.extractreq(str(tmp_path / "src")) == [pin("pytest")]
    assert not (tmp_path / "requirements.txt").exists()


def test_stdlib_only_project_gives_empty_list(tmp_path):
    write(tmp_path / "app.py", "import os, sys, json\n")
    assert extract_requirements(str(tmp_path), False) == []


def test_package_alias():
    assert extractreqs.extractreq is extract_requirements


# CLI


def test_cli_writes_output_file(tmp_path, monkeypatch, capsys):
    write(tmp_path / "src" / "app.py", "import pytest\n")
    out = tmp_path / "reqs.txt"
    monkeypatch.setattr(sys, "argv", ["extractreqs", str(tmp_path / "src"), "-o", str(out)])
    cli.main()
    assert out.read_text().splitlines() == [pin("pytest")]
    assert "Extracted 1 requirements" in capsys.readouterr().out


def test_python_dash_m_entry_point(tmp_path):
    write(tmp_path / "src" / "app.py", "import pytest\n")
    out = tmp_path / "reqs.txt"
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(SRC_DIR), os.environ.get("PYTHONPATH")]))}
    result = subprocess.run(
        [sys.executable, "-m", "extractreqs", str(tmp_path / "src"), "-o", str(out)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert out.read_text().splitlines() == [pin("pytest")]
