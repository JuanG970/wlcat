from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='wlcat',
    version='0.0.1',
    author='wlcat contributors',
    description='Terminal viewer for Wolfram Language Notebooks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JuanG970/wlcat",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'wlcat = wlcat:app_main',
        ]
    }
)
