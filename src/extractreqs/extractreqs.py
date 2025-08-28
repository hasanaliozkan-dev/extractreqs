import os
import ast
import sys
import importlib.util
import importlib.metadata

def get_imports_from_file(filepath):
    """Extract top-level imports from a Python file."""
    with open(filepath, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=filepath)
    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            imports.add(n.module.split(".")[0])
    return imports


def get_all_imports(src_dir):
    all_imports = set()
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                all_imports |= get_imports_from_file(os.path.join(root, file))
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
    "torch": "torch",               # (often thought of as "pytorch")
    "jax": "jax",

    # Parsing / scraping
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "yaml": "PyYAML",
    "ruamel": "ruamel.yaml",

    # Crypto / security
    "Crypto": "pycryptodome",       # sometimes pycrypto (deprecated)
    "cryptography": "cryptography",

    # Date/time
    "dateutil": "python-dateutil",
    "pytz": "pytz",

    # Cloud / APIs
    "google": "google-api-python-client",  # can also be google-cloud-* packages
    "boto3": "boto3",
    "botocore": "botocore",
    "azure": "azure",              # split into azure-* subpackages

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

    result = set()
    for imp in imports:
        try:
            spec = importlib.util.find_spec(imp)
            if spec is None:
                continue  # not found
            if "site-packages" in (spec.origin or ""):
                dist_name = import_to_dist.get(imp, imp)
                try:
                    version = importlib.metadata.version(dist_name)
                    result.add(f"{dist_name}=={version}")
                except importlib.metadata.PackageNotFoundError:
                    pass
        except Exception:
            pass
    return result


def extract_requirements(src_dir, write):
    imports = get_all_imports(src_dir)
    requirements = sorted(filter_installed_packages(imports))
    if write:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
    return requirements
