from setuptools import setup, find_packages

setup(
	name="extractreqs",
	version="0.1.1",
	description="A tool to automatically extract and generate requirements.txt from Python source code by analyzing imports.",
	author="hasanaliozkan",
	author_email="hasanaliozkan@mu.edu.tr",
	packages=find_packages(where="src"),
	package_dir={"": "src"},
	include_package_data=True,
	install_requires=["typer"],
	entry_points={
		"console_scripts": [
			"extractreqs=extractreqs.cli:main",
		]
	},
)
