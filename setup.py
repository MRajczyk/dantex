from setuptools import setup, find_packages

setup(
    name="dantex",
    version="0.1.0",
    author="MRajczyk",
    author_email="mikolajrajczyk01@gmail.com",
    description="A module to download tasks and your accepted solutions from Dante platform at Technical University of Lodz",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "selenium"
    ],
    python_requires=">=3.7",
)