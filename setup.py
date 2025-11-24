from setuptools import setup, find_packages

setup(
    name="ntrs-nebula",
    version="1.0.0",
    description="NTRS: Zero-Point Optical Encryption Protocol",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="CHETHANA ABEYSINGHE",
    author_email="chethanaabeysinghe95@gmail.com",
    url="https://github.com/kcvabeysinghe/ntrs-nebula",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "numpy",
        "pillow",
        "reedsolo",
        "argparse",
    ],
    entry_points={
        'console_scripts': [
            'ntrs=ntrs.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)