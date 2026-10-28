import ast
import importlib.metadata
import importlib.util
import os
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".tox", ".nox", ".venv", "venv", "__pycache__", "node_modules", "site-packages"}


def get_imports_from_file(filepath):
    """Extract top-level imports from a Python file."""
    # Read bytes so ast honours PEP 263 coding declarations
    with open(filepath, "rb") as f:
        node = ast.parse(f.read(), filename=filepath)
    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            imports.add(n.module.split(".")[0])
    return imports


def get_all_imports(src_dir):
    all_imports = set()
    for root, dirs, files in os.walk(src_dir):
        # Prune virtualenvs and tool dirs so their packages' imports don't leak in
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not os.path.exists(os.path.join(root, d, "pyvenv.cfg"))]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    all_imports |= get_imports_from_file(path)
                except SyntaxError as exc:
                    print(f"[!] Skipping {path}: {exc}", file=sys.stderr)
    return all_imports


def filter_installed_packages(imports):
    """Map imports to installed distributions (ignores stdlib)."""
    # Map import names to PyPI distribution names if they differ
    import_to_dist = {
        # Scientific / ML stack
        "sklearn": "scikit-learn",
        "skimage": "scikit-image",
        "skopt": "scikit-optimize",
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "tensorflow": "tensorflow",
        "torch": "torch",  # (often thought of as "pytorch")
        "jax": "jax",
        # Parsing / scraping
        "bs4": "beautifulsoup4",
        "lxml": "lxml",
        "yaml": "PyYAML",
        "ruamel": "ruamel.yaml",
        # Crypto / security
        "Crypto": "pycryptodome",  # sometimes pycrypto (deprecated)
        "cryptography": "cryptography",
        # Date/time
        "dateutil": "python-dateutil",
        "pytz": "pytz",
        # Cloud / APIs
        "google": "google-api-python-client",  # can also be google-cloud-* packages
        "boto3": "boto3",
        "botocore": "botocore",
        "azure": "azure",  # split into azure-* subpackages
        # Databases
        "MySQLdb": "mysqlclient",
        "psycopg2": "psycopg2",
        "pymongo": "pymongo",
        "redis": "redis",
        "sqlalchemy": "SQLAlchemy",
        # Utils
        "dotenv": "python-dotenv",
        "Levenshtein": "python-Levenshtein",
        "gi": "PyGObject",
        "igraph": "python-igraph",
        # Visualization
        "mpl_toolkits": "matplotlib",
        "seaborn": "seaborn",
        "plotly": "plotly",
    }

    # Installed import name -> distributions providing it, e.g. markdown_it -> markdown-it-py
    dists_by_import = importlib.metadata.packages_distributions()

    result = set()
    for imp in imports:
        try:
            spec = importlib.util.find_spec(imp)
        except Exception:
            continue
        if spec is None:
            continue  # not found
        # Namespace packages (google, azure) have no origin, only search locations
        origin = spec.origin or next(iter(spec.submodule_search_locations or []), "")
        if not {"site-packages", "dist-packages"} & set(Path(origin).parts):
            continue  # stdlib or local module
        candidates = [import_to_dist[imp]] if imp in import_to_dist else []
        for dist_name in candidates + dists_by_import.get(imp, [imp]):
            try:
                result.add(f"{dist_name}=={importlib.metadata.version(dist_name)}")
                break
            except importlib.metadata.PackageNotFoundError:
                pass
    return result


def extract_requirements(src_dir, write=False):
    imports = get_all_imports(src_dir)
    requirements = sorted(filter_installed_packages(imports))
    if write:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
    return requirements
